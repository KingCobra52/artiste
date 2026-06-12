import psycopg2
import requests 
import os 
from dotenv import load_dotenv 
from datetime import date  

load_dotenv()

artists = [
        "Drake", "Travis Scott", "Future", "Kendrick Lamar", "J. Cole", "Lil Baby",
        "Playboi Carti", "Don Toliver", "GloRilla", "Central Cee", "Ice Spice",
        "Rod Wave", "21 Savage", "Gunna", "Sexyy Red",
        "JID", "Denzel Curry", "EsDeeKid", "fakemink", "Zeddy Will",
        "Kai Ca$h", "JELEEL!", "BunnaB", "Kae", "Baby Keem"
    ]

today = date.today()

lastfm_api_key = os.getenv("LASTFM_API_KEY")

url = "http://ws.audioscrobbler.com/2.0/"
params = {
        "method": "artist.getinfo",
        "artist": "Drake",
        "api_key": lastfm_api_key,
        "format": "json"
    }

if __name__ == "__main__":

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    for artist in artists:
        params["artist"] = artist 
        response = requests.get(url, params=params)
        data = response.json()
        if "error" in data:
            print(f"Error for {artist}: {data['message']}")
            continue
        print(data["artist"]["stats"])


        #starting db stuff 
        query = f"SELECT EXISTS(SELECT 1 FROM artists WHERE name = %s)"
        cursor.execute(query, (artist,))

        #fetch result as 0 or 1 
        exists = cursor.fetchone()[0]

        if exists:
            query = f"SELECT id FROM artists WHERE name = %s"
            cursor.execute(query, (artist,))
            artist_id = cursor.fetchone()[0]

        else:
            #insert artist into the artists table 
            new_user = (artist,)
            cursor.execute(
                'INSERT INTO artists (name) VALUES (%s) RETURNING id',
                new_user
            )

            #get the artist id -> write it to artist_snapshots 
            artist_id = cursor.fetchone()[0]

        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM artist_snapshots WHERE artist_id = %s AND date = %s)",
            (artist_id, today)
        )
        snapshot_exists = cursor.fetchone()[0]

        if snapshot_exists:
            print(f"Snapshot already exists for {artist}, skipping.")
        else:
            listeners = data["artist"]["stats"]["listeners"]
            playcount = data["artist"]["stats"]["playcount"]
            new_id = (artist_id, listeners, playcount, today)
            cursor.execute(
                'INSERT INTO artist_snapshots (artist_id, listeners, playcount, date) VALUES (%s, %s, %s, %s)',
                new_id
            )
            print(f"Inserted snapshot for {artist} with artist_id {artist_id}")

    conn.commit()
    conn.close()