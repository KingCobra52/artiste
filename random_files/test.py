import requests
import os
from dotenv import load_dotenv

load_dotenv()

test_artists = ["EsDeeKid", "fakemink", "Zeddy Will", "Kai Ca$h", "JELEEL!", "BunnaB", "iAMLYRIC", "Central Factory", "Kae", "kae"]

for artist in test_artists:
    response = requests.get("http://ws.audioscrobbler.com/2.0/", params={
        "method": "artist.getinfo",
        "artist": artist,
        "api_key": os.getenv("LASTFM_API_KEY"),
        "format": "json"
    })
    data = response.json()
    if "error" in data:
        print(f"{artist}: NOT FOUND")
    else:
        print(f"{artist}: {data['artist']['stats']['listeners']} listeners")