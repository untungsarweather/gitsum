# Super sloppy multimon-ng output cleaner for processing by EAS2Text
# I maed dis, sorta, mostly just mashed code I found or that chatGPT hallucinated
# by Mike O'Connell/skrrt, no licence or whatever just be chill yo
# enhanced by sheer.cold

import re
from EAS2Text import EAS2Text

buff=[] # store messages for writing
seen=set()
pattern = re.compile(r'ZCZC.*?NWS-')
while True:
  try:
    # Handle piped input
    line=input().strip()
  except EOFError:
    break
  # only want EAS lines
  if line.startswith("EAS:") or line.startswith("EAS (part):"):
    content=line.split(maxsplit=1)[1]
    if content=="NNNN": # end of EAS message
      # write if we have something
      if buff:
        print("writing")
        with open("alert.txt","w") as fh:
          fh.write('\n'.join(buff))
        # prepare for new data
        buff.clear()
        seen.clear()
    elif content in seen:
      # don't need repeats'
      continue
    else:
      # check for national weather service
      match=pattern.search(content)
      if match:
        seen.add(content)
        msg=EAS2Text(content).EASText
        print("got message", msg)
        buff.append(msg)