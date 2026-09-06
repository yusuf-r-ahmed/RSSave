from flask import Flask
import sqlite3

def connect_db():
    dbcon = sqlite3.connect("rss.db")
    dbcon.row_factory = sqlite3.Row #allows acessing by name not just index
    return dbcon

app = Flask(__name__)

@app.route("/")
def home():
    dbcon = connect_db()
    templates = dbcon.execute("SELECT * FROM feed_templates").fetchall()
    dbcon.close()

    #bulding a html list from db
    html = "<ul>"
    for entry in templates:
        html += f"<li>{entry["name"]} headers = {entry["headers"]}"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(debug=True)