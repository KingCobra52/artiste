import sqlite3

conn = sqlite3.connect("artiste.db")
cursor = conn.cursor()

established_a = ["Drake", "Travis Scott", "Future", "Kendrick Lamar", "J. Cole", "Lil Baby"]

rising_a = ["Playboi Carti",
    "Don Toliver",
    "GloRilla",
    "Central Cee",
    "Ice Spice",
    "Rod Wave",
    "21 Savage",
    "Gunna",
    "Sexyy Red"]

breaking_a = ["JID",
    "Denzel Curry",
    "EsDeeKid",
    "fakemink",
    "Zeddy Will",
    "Kai Ca$h",
    "JELEEL!",
    "BunnaB",
    "Kae",
    "Baby Keem"]

query = "UPDATE artists SET tier = ? WHERE name = ?"

for artist in established_a:
    cursor.execute(query, ("Established", artist))

for artist in rising_a:
    cursor.execute(query, ("Rising", artist))

for artist in breaking_a:
    cursor.execute(query, ("Breaking", artist))

conn.commit()
conn.close()
