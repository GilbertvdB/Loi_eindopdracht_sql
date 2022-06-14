import top10_albums as lib


# lib.cursor()
database_naam = "chinook.db"
conn = lib.verbinding_maken(database_naam)
cur = conn.cursor()

cur.execute(''' SELECT PlaylistId 
FROM playlists
ORDER BY PlaylistId DESC''')
last_pl_id = cur.fetchone()
last = last_pl_id[0] + 1

# row_id = 8716


for x in range(19, last):
    cur.execute(f''' DELETE FROM "main"."playlist_track" WHERE PlaylistId = {x} ''')
    conn.commit()

    cur.execute(f''' DELETE FROM "main"."playlists" WHERE PlaylistId = {x} ''')
    conn.commit()

print("Data removed!")

cur.close()
conn.close()
