import sqlite3
import feedparser
from db import connect_db

def save_feed_and_entries(template_id, feed_url):
    dbcon = connect_db()
    cursor = dbcon.cursor()

    template = cursor.execute("SELECT headers FROM feed_templates WHERE id = ?", (template_id,)).fetchone()

    if not template:
        print(f"Error: Template with ID {template_id} does not exist.")
        dbcon.close()
        return
    
    target_headers = []
    for header in template["headers"].split(","):
        cleaned = header.strip()
        if cleaned:
            target_headers.append(cleaned)


    print(f"Fetching: {feed_url} ...")
    parsed = feedparser.parse(feed_url)

    if not parsed.entries:
        print("Warning: No entries found or invalid RSS URL.")
        dbcon.close()
        return

    feed_title = parsed.feed.get("title", "Untitled Feed")

#feed id
    cursor.execute(
        "INSERT OR IGNORE INTO feeds (template_id, title, url) VALUES (?, ?, ?)",
        (template_id, feed_title, feed_url)
    )
    dbcon.commit()

    feed_record = cursor.execute(
        "SELECT id FROM feeds WHERE url = ?", (feed_url,)
    ).fetchone()
    feed_id = feed_record["id"]


#saves new entries
    new_entries_count = 0
    for item in parsed.entries:
        title = item.get("title", "Untitled Post")
        link = item.get("link", "#")
        published = item.get("published", "")

        #base entry
        cursor.execute("INSERT OR IGNORE INTO entries (feed_id, title, link, published) VALUES (?, ?, ?, ?)",(feed_id, title, link, published))

        entry_id = cursor.lastrowid #gives new entry id 0 if duplicate

        if entry_id:
            new_entries_count += 1
            for header in target_headers:
                # convert ':' -> '_'
                normalized_key = header.strip().lower().replace(":", "_")

                # Check exact header name, fallback to normalized key
                raw_value = item.get(header) or item.get(normalized_key, "")

                # handle media audio/video links if header is 'enclosures'
                if header == "enclosures" and item.get("enclosures"):
                    raw_value = item.enclosures[0].get("href", "")

                cursor.execute(
                    """INSERT INTO entry_headers (entry_id, header_name, header_value)
                       VALUES (?, ?, ?)""",
                    (entry_id, header, str(raw_value))
                )

    dbcon.commit()
    dbcon.close()
    print(f"Saved feed '{feed_title}' with {new_entries_count} new entries.")


if __name__ == "__main__":
    save_feed_and_entries(template_id=1,feed_url="https://letterboxd.com/(placeholder)/rss/")