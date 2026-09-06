from flask import Flask, render_template, request, redirect
import sqlite3
import feedparser
from db import connect_db

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    dbcon = connect_db()

    #when button on website is pressed code below is executed 
    if request.method == "POST":
        template_name = request.form["name"]
        headers = request.form["headers"]

        #inserts into database (?,?) unnamed parameters prevents sql injection
        dbcon.execute(
                "INSERT INTO feed_templates (name, headers) VALUES (?, ?)",
                (template_name, headers))
        dbcon.commit()
        dbcon.close()

    
        # clean get request refresh
        return redirect("/")

    templates = dbcon.execute("SELECT * FROM feed_templates").fetchall()
    dbcon.close()

    #uses the template created in templates/index.html
    return render_template("index.html", templates=templates)

if __name__ == "__main__":
    app.run(debug=True)