from dotenv import load_dotenv 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os 

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
))

# artists = ["Drake", "Travis Scott", "Future"]

# for artist in artists:
#     query = f"artist:{artist}"
#     results = sp.search(q=query, type='artist', limit=1)
#     artist_found = results.get('artists', {}).get('items', [])[0]
#     artist_id = artist_found['id']
#     data = sp.artist(artist_id)

#     print(type(data))
#     print(data)

data = sp.artist("3TVXtAsR1Inumwj472S9r4")
print(data.keys())


