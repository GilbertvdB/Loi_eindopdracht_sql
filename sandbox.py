import sqlite3  # import voor toegang tot de database.
from sqlite3 import Error  # database exception handeling.
import os  # import om de file directory te controleren.
import top10_albums as lib

database_naam = "chinook.db"
conn = lib.verbinding_maken(database_naam)
cur = conn.cursor()


def add_playlist_naam(id_nr, naam):
    # add the playlist name into the db table
    new_id = id_nr
    pl_naam = naam_playlist()  # "Mijn Muziek"
    # print(naam)
    # avoid adding duplicates playlist names
    if naam is not False:  # indien naam nog niet bestaat
        new_id += 1
        cur.execute(f'''INSERT INTO playlists VALUES ({new_id}, '{pl_naam}') ''')
        conn.commit()
    else:
        # print("update pl")
        pass

    return new_id, pl_naam