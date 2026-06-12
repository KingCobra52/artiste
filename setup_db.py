import os 
from dotenv import load_dotenv 
import psycopg2

load_dotenv()

DATABASE_URL_IPV4 = os.getenv("DATABASE_URL_IPV4")
DATABASE_URL_IPV6 = os.getenv("DATABASE_URL_IPV6")

conn = psycopg2.connect(DATABASE_URL_IPV4) #creates the postgres schema 
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        id SERIAL PRIMARY KEY,
        name TEXT,  
        spotify_id TEXT, 
        genre TEXT,
        image_url TEXT,
        tier TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS artist_snapshots (
        id SERIAL PRIMARY KEY, 
        artist_id INTEGER REFERENCES artists(id),
        listeners INTEGER, 
        playcount INTEGER,
        date DATE 
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY, 
        username TEXT, 
        email TEXT,
        hashed_password TEXT,
        bars INTEGER DEFAULT 10000
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS holdings (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        artist_id INTEGER REFERENCES artists(id), 
        shares INTEGER,
        price_per_share FLOAT, 
        bought_at DATE 
    )
""")

conn.commit()
conn.close()