from db import connect_db
from fetch_feed import save_feed_and_entries


def sync():
  dbcon = connect_db()
  feeds = dbcon.execute("SELECT template_id, url FROM feeds").fetchall()
  dbcon.close()

  for feed in feeds:
    save_feed_and_entries(feed["template_id"], feed["url"])


if __name__ == "__main__":
  sync()