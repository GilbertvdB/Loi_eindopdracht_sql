"""
Auteur: G van der Biezen
Naam bestand: test.py

Het volgende programma print de top 10 albums uit van een database.
Eerst wordt de verbinding gemaakt met een database. Vervolgens worden
data aangevraagd en daarna worden ze verwerkt in een top 10 lijst.

Python versie: 3.10.2
IDE: IntelliJ IDEA Community Edition 2021.3.2
Last update: 09/06/2021
"""

import sqlite3  # import voor toegang tot de database.
from sqlite3 import Error  # database exception handeling.
import os  # import om de file directory te controleren.
import top10_albums as lib


database_naam = "chinook.db"
conn = lib.verbinding_maken(database_naam)
cur = conn.cursor()


def check(x):
    # cur = conn.cursor()
    cur.execute(''' SELECT name FROM playlists''')
    rows = cur.fetchall()
    if x in rows[0]:
        # print("Deze playlist bestaat al.")
        return True
    else:
        return False
        # print("---- Start import van playlist ----")


def import_plist(x):
    pass


def read_file(x):
    with open(x, 'r') as tekst:
        # count = 0
        # for x in tekst:
        #     count += 1
        #     print(count, x)
        lines = tekst.readlines()  # read and convert lines into a list
        print(lines)
        for titel in lines:  # for each titel in lines
            # print(titel)
            # naam = titel
            # if titel.isspace() is True:
            #     pass
            # else:
            print("1", titel)  # todo
            cur.execute(f''' SELECT name FROM tracks WHERE name = '{titel}' ''')
            info = cur.fetchall()
            print(titel + " row is", info)


file_prompt = "MijnMuziek.txt"  # input("Geef naam van het te importeren bestand: ")

if os.path.isfile(file_prompt):
    print("Bestand gevonden.")
    playlist = "Music"    # input("Geef naam van de playlist: ")
    if check(playlist) is True:
        print("Deze playlist bestaat al.")
    else:
        print("---- Start import van playlist ----")
        import_plist(playlist)
        read_file(file_prompt)


else:
    print("Bestand niet gevonden.")


cur.close()
conn.close()
