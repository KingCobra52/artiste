import sqlite3
from flask import Flask, render_template
import sqlite3 

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("artiste.db")
    conn.row_factory = sqlite3.Row 
    return conn 

@app.route("/")
def market():
    db = get_db()
    artists = db.execute("SELECT artists.name, artist_snapshots.listeners, artist_snapshots.playcount, artist_snapshots.date, artists.tier FROM artist_snapshots JOIN artists ON artists.id = artist_snapshots.artist_id ORDER BY artists.id").fetchall()
    return render_template("market.html", artists=artists)
    

@app.route("/artist/<name>")
def artist(name):
    query = "SELECT * FROM artist_snapshots JOIN artists ON artists.id = artist_snapshots.artist_id WHERE artists.name = ? ORDER BY artist_snapshots.date DESC LIMIT 1"
    db = get_db()
    artist = db.execute(query, (name, )).fetchone()
    return render_template("artist.html", artist=artist)

if __name__ == "__main__":
    app.run(debug=True)