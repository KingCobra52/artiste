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

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT, 
        email TEXT,
        hashed_password TEXT,
        bars INTEGER DEFAULT 10000
    )
""")

conn.commit()
conn.close()