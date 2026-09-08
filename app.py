from flask import Flask, render_template, request, redirect
import sqlite3
import feedparser
from db import connect_db
from fetch_feed import save_feed_and_entries

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    dbcon = connect_db()

    #when button on website is pressed code below is executed 
    if request.method == "POST":
        template_name = request.form["name"]
        headers = request.form["headers"]

        #inserts into database (?,?) unnamed parameters prevents sql injection
        dbcon.execute("INSERT INTO feed_templates (name, headers) VALUES (?, ?)",(template_name, headers))
        dbcon.commit()
        dbcon.close()

        # clean get request refresh
        return redirect("/")

    templates = dbcon.execute("SELECT * FROM feed_templates").fetchall()
    
    feeds = dbcon.execute("""
        SELECT feeds.id, feeds.title, feeds.url, feed_templates.name AS template_name
        FROM feeds
        JOIN feed_templates ON feeds.template_id = feed_templates.id
    """).fetchall()
    
    dbcon.close()

    #uses the template created in templates/index.html
    return render_template("index.html", templates=templates,feeds=feeds)

@app.route("/feed/<int:feed_id>")
def view_feed(feed_id):
    dbcon = connect_db()

    #fetch feed and teplate def
    feed = dbcon.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,)).fetchone()
    if not feed:
        dbcon.close()
        return "Feed not found", 404

    template = dbcon.execute("SELECT * FROM feed_templates WHERE id = ?", (feed["template_id"],)).fetchone()

    target_headers = []
    for header in template["headers"].split(","):
        cleaned = header.strip()
        if cleaned:
            target_headers.append(cleaned)

    # fetch base entries
    entries = dbcon.execute( "SELECT * FROM entries WHERE feed_id = ? ORDER BY id ASC", (feed_id,)).fetchall()

    # fetch all custom headers belonging to these entries
    header_rows = dbcon.execute(
        """
        SELECT eh.entry_id, eh.header_name, eh.header_value
        FROM entry_headers eh
        JOIN entries e ON eh.entry_id = e.id
        WHERE e.feed_id = ?
        """,(feed_id,), ).fetchall()
    dbcon.close()

    # map headers by entry_id:
    headers_by_entry = {}
    for row in header_rows:
        headers_by_entry.setdefault(row["entry_id"], {})[row["header_name"]] = row["header_value"]

    #entries with targheader
    entries_data = []
    for entry in entries:
        entries_data.append({
            "id": entry["id"],
            "title": entry["title"],
            "link": entry["link"],
            "published": entry["published"],
            "headers": headers_by_entry.get(entry["id"], {})
        })

    return render_template("feed.html",feed=feed,template=template,target_headers=target_headers,entries=entries_data)

@app.route("/add-feed", methods=["POST"])
def add_feed():
    #user inputs the template ID they want to use + the feed they want to track.
    template_id = int(request.form["template_id"])
    feed_url = request.form["feed_url"].strip()

    #calls the fetching function for that url
    save_feed_and_entries(template_id, feed_url)

    #connects to the database to get the id number to direct the user to the right feed
    dbcon = connect_db()
    feed = dbcon.execute("SELECT id FROM feeds WHERE url = ?", (feed_url,)).fetchone()
    dbcon.close()

    
    #directs them if feed worked
    if feed:
        return redirect(f"/feed/{feed['id']}")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)