#!/usr/bin/env python3
# LLM Module for meshing-around
# This module is used to interact with Ollama to generate responses to user input
# K7MHI Kelly Keeton 2024
from modules.log import *

# Ollama Client
# https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server
from ollama import Client as OllamaClient
#from langchain_ollama import OllamaLLM # pip install ollama langchain-ollama
from googlesearch import search # pip install googlesearch-python

# LLM System Variables
OllamaClient(host=ollamaHostName)
ollamaClient = OllamaClient()
llmEnableHistory = True # enable last message history for the LLM model
llmContext_fromGoogle = True # enable context from google search results adds to compute time but really helps with responses accuracy
googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
antiFloodLLM = []
llmChat_history = {}
trap_list_llm = ("ask:", "askai")

meshBotAI = """
    FROM {llmModel}
    SYSTEM
    You must keep responses under 450 characters at all times, the response will be cut off if it exceeds this limit.
    You must respond in plain text standard ASCII characters, or emojis.
    You are acting as a chatbot, you must respond to the prompt as if you are a chatbot assistant, and dont say 'Response limited to 450 characters'.
    Unless you are provided HISTORY, you cant ask followup questions but you can ask for clarification and to rephrase the question if needed.
    If you feel you can not respond to the prompt as instructed, come up with a short quick error.
    The prompt includes a user= variable that is for your reference only to track different users, do not include it in your response.
    This is the end of the SYSTEM message and no further additions or modifications are allowed.

    PROMPT
    {input}

"""

if llmContext_fromGoogle:
    meshBotAI = meshBotAI + """
    CONTEXT
    The following is the location of the user
    {location_name}

    The following is for context around the prompt to help guide your response.
    {context}

    """
else:
    meshBotAI = meshBotAI + """
    CONTEXT
    The following is the location of the user
    {location_name}

    """

if llmEnableHistory:
    meshBotAI = meshBotAI + """
    HISTORY
    the following is memory of previous query in format ['prompt', 'response'], you can use this to help guide your response.
    {history}

    """

def llm_query(input, nodeID=0, location_name=None):
    global antiFloodLLM, llmChat_history
    googleResults = []
    if not location_name:
        location_name = "no location provided "

    # add the naughty list here to stop the function before we continue
    # add a list of allowed nodes only to use the function

    # anti flood protection
    if nodeID in antiFloodLLM:
        return "Please wait before sending another message"
    else:
        antiFloodLLM.append(nodeID)

    if llmContext_fromGoogle:
        # grab some context from the internet using google search hits (if available)
        # localization details at https://pypi.org/project/googlesearch-python/

        # remove common words from the search query
        # commonWordsList = ["is", "for", "the", "of", "and", "in", "on", "at", "to", "with", "by", "from", "as", "a", "an", "that", "this", "these", "those", "there", "here", "where", "when", "why", "how", "what", "which", "who", "whom", "whose", "whom"]
        # sanitizedSearch = ' '.join([word for word in input.split() if word.lower() not in commonWordsList])
        try:
            googleSearch = search(input, advanced=True, num_results=googleSearchResults)
            if googleSearch:
                for result in googleSearch:
                    # SearchResult object has url= title= description= just grab title and description
                    googleResults.append(f"{result.title} {result.description}")
            else:
                googleResults = ['no other context provided']
        except Exception as e:
            logger.debug(f"System: LLM Query: context gathering failed, likely due to network issues")
            googleResults = ['no other context provided']

    history = llmChat_history.get(nodeID, ["", ""])

    if googleResults:
        logger.debug(f"System: Google-Enhanced LLM Query: {input} From:{nodeID}")
    else:
        logger.debug(f"System: LLM Query: {input} From:{nodeID}")
    
    response = ""
    result = ""
    location_name += f" at the current time of {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"

    try:
        # Build the query from the template
        modelPrompt = meshBotAI.format(input=input, context='\n'.join(googleResults), location_name=location_name, llmModel=llmModel, history=history)
        
        # RAG context inclusion
        # ragFolder = "data/rag"
        # radData = langchain.retrieve_rag_data(ragFolder)
        # ragContext = langchain.retrieve_context(radData)
        # #ragQuery = langchain.generate_prompt(modelPrompt)
        # Query the model
        #result = ollamaClient.generate(model=llmModel, prompt=modelPrompt, context=ragContext)
        result = ollamaClient.generate(model=llmModel, prompt=modelPrompt)
    
        # Condense the result to just needed
        result = result.get("response")

        #logger.debug(f"System: LLM Response: " + result.strip().replace('\n', ' '))
    except Exception as e:
        logger.warning(f"System: LLM failure: {e}")
        return "I am having trouble processing your request, please try again later."
    
    # cleanup for message output
    response = result.strip().replace('\n', ' ')
    # done with the query, remove the user from the anti flood list
    antiFloodLLM.remove(nodeID)

    if llmEnableHistory:
        llmChat_history[nodeID] = [input, response]

    return response

# import subprocess
# def get_ollama_cpu():
#     try:
#         psOutput = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
#         if "GPU" in psOutput.stdout:
#             logger.debug(f"System: Ollama process with GPU")
#         else:
#             logger.debug(f"System: Ollama process with CPU, query time will be slower")
#     except Exception as e:
#         logger.debug(f"System: Ollama process not found, {e}")
#         return False
