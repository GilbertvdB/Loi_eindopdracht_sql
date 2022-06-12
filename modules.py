"""
Auteur: G van der Biezen
Naam bestand: eind_opdracht_2.py

Het volgende programma laat een gebruiker een playlist maken.
De gebruiker geeft zelf een bestand naam aan en een playlist naam.
De gegevens worden gecontroleerd en toegevoegd aan de database.

Python versie: 3.10.2
IDE: IntelliJ IDEA Community Edition 2021.3.2
Last update: 12/06/2021
"""
import sqlite3  # import voor toegang tot de database.
from sqlite3 import Error  # database exception handeling.
import os  # import om de file directory te controleren.
import sys
import eind_opdracht_1 as lib


def start_up():
    global conn
    global cur

    database_naam = "chinook.db"
    conn = lib.verbinding_maken(database_naam)
    cur = conn.cursor()


def input_bestand():
    bestand = "test.txt"
    # bestand = input("Geef naam van het te importeren bestand: ")  # todo
    if os.path.isfile(bestand):
        # print("Bestand gevonden.")
        return bestand
    else:
        print("Bestaand niet gevonden")
        sys.exit(1)


def naam_playlist():
    playlist = input("Geef naam van de playlist: ")  # todo
    c = check_db(playlist)
    if c is False:  # if check_db is false. playlist not yet in db.
        return playlist
    else:
        print("Deze playlist bestaat al")
        sys.exit(1)


def check_db(name_to_check):
    # print(name_to_check)
    cur.execute(f''' SELECT EXISTS( SELECT name FROM playlists WHERE name = '{name_to_check}') ''')
    rows = cur.fetchone()
    for x in rows:
        if x == 1:  # name exists in database
            return True
        else:
            return False  # name does not exist yet in database


def get_last_id():
    # find the last playlist id number
    cur.execute('''SELECT PlaylistId FROM playlists
                ORDER BY PlaylistId DESC''')
    last_id = cur.fetchone()
    return last_id[0]


def add_playlist_naam():
    # add the playlist name into the db table
    new_id = get_last_id() + 1
    pl_naam = naam_playlist()  # "Mijn Muziek"
    cur.execute(f'''INSERT INTO playlists VALUES ({new_id}, '{pl_naam}') ''')
    conn.commit()

    return new_id, pl_naam


def get_line(bestand):   # todo check from lines
    with open(bestand, 'r') as tekst:
        lines = tekst.read().splitlines()
        for empty_line in lines:  # remove empty strings
            if empty_line == '':
                lines.remove(empty_line)

        return lines


def search_db(linez):
    # print(linez)
    info_list = []
    for words in linez:
        cur.execute(f''' SELECT tracks.Name, artists.name, tracks.TrackId
                    FROM tracks
                    INNER JOIN albums ON albums.AlbumId = tracks.AlbumId
                    INNER JOIN artists ON albums.ArtistId = artists.ArtistId
                    WHERE tracks.name LIKE "{words}%" ''')
        info = cur.fetchall()  # is a list
        info_list.append(info)
    return linez, info_list


def add_the_tracks(info_lst, name_pl):
    print("--- Start import van playlist ---")
    n_lis, i_lis = info_lst
    for y in i_lis:
        x = i_lis.index(y)
        if len(y) == 1:
            # print(f"For {x} will be added to playlist")
            # add track function
            add_track_to_playlist(y[0][2], name_pl)
        elif len(y) > 1:
            # print(f"For {x}:\nchoice menu goes here")
            # choice function
            # track_choice(x)
            # add track function
            add_track_to_playlist(track_choice(y), name_pl)   # todo here
        else:
            print(f"--- Geen tracks gevonden voor {n_lis[x]} ---")

    print("--- Import van playlist gereed ---")


def add_track_to_playlist(track_number, name_pl):
    # add song to the playlist by adding PlaylistID en trackID
    # insert new line into playlist_track
    pl_id = name_pl[0]
    try:
        cur.execute(f'''INSERT INTO playlist_track VALUES ({pl_id}, {track_number}) ''')
        conn.commit()
    except Error as e:  # Unique or duplicate error in table
        pass  # print(e)


def track_choice(x_l):
    positie = 0
    m_len = max_length_string(x_l)
    print("Maak een keuze uit de volgende tracks:")
    for options in x_l:
        positie += 1
        track, artist = options[0], options[1]
        print(f"{positie:<4} {track:<{m_len}} {artist}")

    # make a choice
    keuze = int(input("Uw keuze "))
    song_choice_track_id = x_l[keuze - 1][2]
    return song_choice_track_id


def max_length_string(kolom):
    max_len = 0
    for string_lengte in kolom:
        if len(string_lengte[0]) > max_len:
            max_len = len(string_lengte[0]) + 4  # +4 is de lengte van een tab
    return max_len


def main():
    start_up()
    geldig_bestand = input_bestand()  # check of the txt. bestaat
    # n_pl = naam_playlist()  # check op naam playlist
    my_pl = add_playlist_naam()
    # start import playlist
    lines = get_line(geldig_bestand)
    infos = search_db(lines)
    add_the_tracks(infos, my_pl)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
