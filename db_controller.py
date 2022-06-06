import sqlite3
from sqlite3 import Error

def sql_connection():

    try:
        db = "ransomwareLeaksDB.db"
        con = sqlite3.connect(db)
        print("\nConnection established with " + db)
        return con
    except Error:
        print(Error)

def sql_create(con):
    
    con.execute("PRAGMA foreign_keys = 1")
    cursorObj = con.cursor()
    
    cursorObj.execute("""CREATE TABLE IF NOT EXISTS family(
        groupName text PRIMARY KEY, 
        onionversion text, 
        groupTitle text, 
        information text, 
        lastCrawledGroup date)
    """)
    cursorObj.execute("""CREATE TABLE IF NOT EXISTS attack(
        id INTEGER PRIMARY KEY,
        title text, 
        link text, 
        location text, 
        information text, 
        date date, 
        views integer, 
        ransomMoney real, 
        publishedPercentage integer, 
        dataSize text, 
        lastCrawledLeak date, 
        groupName text,
        FOREIGN KEY (groupName) REFERENCES family(groupName))
    """)
    
    print("Database Tables Created")
    con.commit()
