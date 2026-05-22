import sqlite3
import requests 
import os 
from dotenv import load_dotenv 
import sqlite3
from datetime import date  

load_dotenv()

artists = ["Drake", "Future", "Travis Scott"]
today = date.today()

lastfm_api_key = os.getenv("LASTFM_API_KEY")

url = "http://ws.audioscrobbler.com/2.0/"
params = {
    "method": "artist.getinfo",
    "artist": "Drake",
    "api_key": lastfm_api_key,
    "format": "json"
}

conn = sqlite3.connect("artiste.db")
cursor = conn.cursor()

for artist in artists:
    params["artist"] = artist 
    response = requests.get(url, params=params)
    data = response.json()
    print(data["artist"]["stats"])


    #starting db stuff 
    query = f"SELECT EXISTS(SELECT 1 FROM artists WHERE name = ?)"
    cursor.execute(query, (artist,))

    #fetch result as 0 or 1 
    exists = cursor.fetchone()[0]

    if exists:
        query = f"SELECT id FROM artists WHERE name = ?"
        cursor.execute(query, (artist,))
        artist_id = cursor.fetchone()[0]

    else:
        #insert artist into the artists table 
        new_user = (artist,)
        cursor.execute(
            'INSERT INTO artists (name) VALUES (?)',
            new_user
        )

        #get the artist id -> write it to artist_snapshots 
        artist_id = cursor.lastrowid

    listeners = data["artist"]["stats"]["listeners"]
    playcount = data["artist"]["stats"]["playcount"]
    new_id = (artist_id, listeners, playcount, today)
    cursor.execute(
        'INSERT INTO artist_snapshots (artist_id, listeners, playcount, date) VALUES (?, ?, ?, ?)',
        new_id
    )

conn.commit()
