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


def start_up():
    global conn
    global cur

    database_naam = "chinook.db"
    conn = verbinding_maken(database_naam)
    cur = conn.cursor()


def verbinding_maken(database_file):
    """ Controleert of de database in de directory bestaat. Maakt daarna
    een verbinding met de SQLite database aangegeven door de `db_file`.
    Als het bestand niet bestaat, wordt het programma gestopt.
    :param database_file: database file.
    :return: connection object of None.
    """
    if os.path.isfile(database_file):
        try:
            conn = sqlite3.connect(database_file)
            return conn
        except Error as e:
            print(e)
        return None
    else:  # Programma stoppen als het bestand niet bestaat.
        print(f"{database_file} niet gevonden.")
        sys.exit(1)


def check_bestand():
    """ Vraag de gebruiker de naam van de tekst bestand en controleer
    of het een geldig bestand is.
    :return: een geldige bestand naam. """
    naam_bestand = input("Geef naam van het te importeren bestand: ")
    if os.path.isfile(naam_bestand):
        return naam_bestand
    else:
        print("Bestand niet gevonden.")
        sys.exit(1)


def naam_playlist():
    """ Vraag de gebruiker de naam van de playlist en controleer in
    de database of het niet al bestaat en dus mogelijk voor gebruik.
    :return: naam van de playlist. """
    playlist_naam = input("Geef naam van de playlist: ")
    c = check_in_db(playlist_naam)
    if c is False:  # Playlist naam nog niet in gebruik.
        return playlist_naam
    else:
        print("Deze playlist bestaat al.")
        sys.exit(1)


def check_in_db(playlist_naam):
    """ Zoek in de database of de playlist naam gevonden kan worden.
    :param playlist_naam: naam van de playlist.
    :return: True als de naam bestaat, anders False. """
    cur.execute(f''' SELECT EXISTS( SELECT name FROM playlists 
                WHERE name = '{playlist_naam}') ''')
    row = cur.fetchone()
    for x in row:
        if x == 1:
            return True
        else:
            return False


def add_playlist_naam(playlist_naam):
    """ Voeg de nieuwe playlist toe aan de tabel 'playlists' in de
    database.
    :param playlist_naam: naam van de playlist.
    :return: naam van de playlist. """
    cur.execute(f'''INSERT INTO playlists 
                VALUES (NULL, '{playlist_naam}') ''')
    conn.commit()


def get_playlist_id(playlist_naam):
    """ Retourneer de playlist id nummer uit de database.
    :param playlist_naam: naam van de playlist.
    :return: playlist id nummer.
    """
    cur.execute(f'''SELECT PlaylistId FROM playlists
                WHERE name = '{playlist_naam}' ''')
    playlist_id = cur.fetchone()
    return playlist_id[0]


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


def add_the_tracks(info_lst, pl_id):
    print("--- Start import van playlist ---")
    n_lis, i_lis = info_lst
    for y in i_lis:
        x = i_lis.index(y)
        if len(y) == 1:
            # print(f"For {x} will be added to playlist")
            # add track function
            add_track_to_playlist(y[0][2], pl_id)
        elif len(y) > 1:
            # print(f"For {x}:\nchoice menu goes here")
            # choice function
            # track_choice(x)
            # add track function
            add_track_to_playlist(track_choice(y), pl_id)   # todo here
        else:
            print(f"--- Geen tracks gevonden voor {n_lis[x]} ---")

    print("--- Import van playlist gereed ---")


def add_track_to_playlist(track_number, pname_id):
    # add song to the playlist by adding PlaylistID en trackID
    # insert new line into playlist_track
    pl_id = pname_id
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
    geldig_bestand = check_bestand()  # check of the txt. bestaat
    n_pl = naam_playlist()  # check op naam playlist
    add_playlist_naam(n_pl)
    pl_id = get_playlist_name_id(n_pl)
    # start import playlist
    lines = get_line(geldig_bestand)
    infos = search_db(lines)
    add_the_tracks(infos, pl_id)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
