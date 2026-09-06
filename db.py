import sqlite3

db_name = "rss.db"

def connect_db():
    dbcon = sqlite3.connect(db_name)
    dbcon.execute("PRAGMA foreign_keys = ON") 
    dbcon.row_factory = sqlite3.Row #allows acessing by name not just index
    return dbcon