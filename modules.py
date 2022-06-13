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
    een verbinding met de SQLite database. Als het bestand niet bestaat,
     wordt het programma gestopt.
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


# bestand gerelateerd functies
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


# playlist gerelateerd functies
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


def get_lines(bestand):
    """ Haal de lijnen uit `bestand` op als een lijst. Verwijder lege
    lijnen die er tussen zitten en retourneer de lijst.
    :param bestand: naam van het bestand.
    :return: lijst zonder lege waarden.
    """
    with open(bestand, 'r') as tekst:
        lijst_lijnen = tekst.read().splitlines()
        for lege_lijn in lijst_lijnen:
            if lege_lijn == '':
                lijst_lijnen.remove(lege_lijn)
        return lijst_lijnen


def zoek_worden(zoek_lijst):
    """ Zoek in de database voor liedjes die woorden bevatten uit
    `zoek_lijst`. Voeg het zoekresultaat in een nieuwe lijst toe.
    :param zoek_lijst: lijst met woorden om te zoeken.
    :return: de originele lijst en de nieuwe lijst.
    """
    info_lijst = []  # lege lijst om het zoekresultaat te bewaren
    # zoek voor elke lijn de liedjes naam, artiest en id nummers.
    for worden in zoek_lijst:
        cur.execute(f''' SELECT tracks.Name, artists.name, tracks.TrackId
                    FROM tracks
                    INNER JOIN albums ON albums.AlbumId = tracks.AlbumId
                    INNER JOIN artists ON albums.ArtistId = artists.ArtistId
                    WHERE tracks.name LIKE "{worden}%" ''')
        info = cur.fetchall()
        info_lijst.append(info)
    return zoek_lijst, info_lijst


def import_playlist(lijst_info, playlist_id):  # TODO doorgaan met docstrings vanaf hier
    """ Importeert """
    print("--- Start import van playlist ---")
    naam, informatie = lijst_info
    for y in informatie:
        x = informatie.index(y)
        naam_lied = y[0][2]

        # maar 1 lied is gevonden voor de zoekterm
        if len(y) == 1:
            add_track_to_playlist(naam_lied, playlist_id)
        # meerdere liedjes gevonden voor de zoekterm
        elif len(y) > 1:
            add_track_to_playlist(track_choice(y), playlist_id)
        # geen liedjes zijn gevonden voor de zoekterm
        else:
            print(f"--- Geen tracks gevonden voor {naam[x]} ---")

    print("--- Import van playlist gereed ---")


def add_track_to_playlist(track_number, pname_id):
    # add song to the playlist by adding PlaylistID en trackID
    # insert new line into playlist_track
    pl_id = pname_id
    try:
        cur.execute(f'''INSERT INTO playlist_track VALUES ({pl_id}, {track_number}) ''')
        conn.commit()
    except Error:  # Unique or duplicate error in table
        pass


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
    pl_id = get_playlist_id(n_pl)
    # start import playlist
    lines = get_lines(geldig_bestand)
    infos = zoek_worden(lines)
    import_playlist(infos, pl_id)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
