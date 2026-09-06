import sqlite3

rssdb = sqlite3.connect("rss.db")

with open ("schema.sql") as schema:
    rssdb.executescript(schema.read())

rssdb.commit()
rssdb.close()

print("Database setup")