# Module to respomnd to new nodes we havent seen before with a hello message
# K7MHI Kelly Keeton 2024

import sqlite3
from modules.log import *

def initalize_qrz_database():
    # create the database
    conn = sqlite3.connect(qrz_db)
    c = conn.cursor()
    # Check if the qrz table exists, and create it if it doesn't
    c.execute('''CREATE TABLE IF NOT EXISTS qrz
                 (qrz_id INTEGER PRIMARY KEY, qrz_call TEXT, qrz_name TEXT, qrz_qth TEXT, qrz_notes TEXT)''')
    conn.commit()
    conn.close()

def never_seen_before(nodeID):
    # check if we have seen this node before and sent a hello message
    conn = sqlite3.connect(qrz_db)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM qrz WHERE qrz_call = ?", (nodeID,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return True
        else:
            return False
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            initalize_qrz_database()
            return True
        else:
            raise
    
def hello(nodeID, name, qth, notes):
    # send a hello message
    conn = sqlite3.connect(qrz_db)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO qrz (qrz_call, qrz_name, qrz_qth, qrz_notes) VALUES (?, ?, ?, ?)", (nodeID, name, qth, notes))
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            initalize_qrz_database()
            c.execute("INSERT INTO qrz (qrz_call, qrz_name, qrz_qth, qrz_notes) VALUES (?, ?, ?, ?)", (nodeID, name, qth, notes))
        else:
            raise
    conn.commit()
    conn.close()
    return True


    
