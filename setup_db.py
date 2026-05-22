import sqlite3

conn = sqlite3.connect("artiste.db") #creates the sqlite schema file
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,  
        spotify_id TEXT, 
        genre TEXT,
        image_url TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS artist_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        artist_id INTEGER REFERENCES artists(id),
        listeners INTEGER, 
        playcount INTEGER,
        date DATE 
    )
""")

conn.commit()
conn.close()