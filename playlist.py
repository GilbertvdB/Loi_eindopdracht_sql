"""
Auteur: G van der Biezen
Naam bestand: playlist.py

Het volgende programma laat een gebruiker een playlist maken van een
tekst file met naam van liedjes of zoekwoorden. De gebruiker geeft zelf
een bestand naam aan en een playlist naam. De gegevens worden
gecontroleerd en toegevoegd aan de database.

Python versie: 3.10.2
IDE: IntelliJ IDEA Community Edition 2021.3.2
Last update: 15/06/2021
"""
import sqlite3  # Import voor toegang tot de database.
from sqlite3 import Error  # Database exception handeling.
import os  # Import om de file directory te controleren.
import sys  # Import om de het programma te stoppen via sys.exit.


def opstarten_db():
    """ Definieer de naam van de database en maak een verbinding. Ook
    wordt een cursor gemaakt om de database te benaderen. """
    # Definieer als global om buiten de functie gebruikt te worden.
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
    :return: connectie object of None.
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


def get_lijnen(bestand):
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
    `zoek_lijst`. Voeg, per woord, het resultaat in een nieuwe lijst toe.
    :param zoek_lijst: lijst met woorden om te zoeken.
    :return: de originele lijst en de nieuwe lijst.
    """
    info_lijst = []  # Lege lijst om het zoekresultaat te bewaren.
    # Zoek voor elke lijn de titel, artiest en id-nummer.
    for worden in zoek_lijst:
        cur.execute(f''' SELECT tracks.Name, artists.name, tracks.TrackId
                    FROM tracks
                    INNER JOIN albums ON albums.AlbumId = tracks.AlbumId
                    INNER JOIN artists ON albums.ArtistId = artists.ArtistId
                    WHERE tracks.name LIKE "{worden}%" ''')
        info = cur.fetchall()
        info_lijst.append(info)  # Voeg lijst met titel, artist en id.
    return zoek_lijst, info_lijst


def get_playlist_id(playlist_naam):
    """ Retourneer de playlist id-nummer uit de database.
    :param playlist_naam: naam van de playlist.
    :return: playlist id nummer.
    """
    cur.execute(f'''SELECT PlaylistId FROM playlists
                WHERE name = '{playlist_naam}' ''')
    playlist_id = cur.fetchone()

    return playlist_id[0]


def import_playlist(lijst_info, playlist_id):
    """ Voeg de liedjes in de playlist toe door de titel en trackId
     uit `lijst_info` op te halen. Bij meer dan 1 gevonden titel wordt
     een keuze menu aangegeven en bij 0 een melding."""
    print("--- Start import van playlist ---")
    zoek_titel, informatie = lijst_info
    for list_info in informatie:
        x = informatie.index(list_info)
        titel_lied = lijst_info[0][2]

        # Maar 1 titel is gevonden voor de zoekterm.
        if len(list_info) == 1:
            add_track(titel_lied, playlist_id)
        # Meerdere titels gevonden voor de zoekterm.
        elif len(list_info) > 1:
            add_track(track_keuze(list_info), playlist_id)
        # Geen titels zijn gevonden voor de zoekterm.
        else:
            print(f"--- Geen tracks gevonden voor {zoek_titel[x]} ---")
    print("--- Import van playlist gereed ---")


def add_track(track_id, playlist_id):
    """ Voeg een liedje, door zijn `track_id`, toe aan een playlist.
    Een uitzondering wordt gemaakt indien de database een foutmelding
    geeft dat `track_id` al in bestaat in de playlist.
    :param track_id: id-nummer van het lied.
    :param playlist_id: id-nummer van de playlist. """
    try:
        cur.execute(f'''INSERT INTO playlist_track 
                    VALUES ({playlist_id}, {track_id}) ''')
        conn.commit()
    except Error:  # Unique of duplicate item error in de tabel.
        pass


def track_keuze(info_lijst):
    """ Toon een keuze menu aan voor de gebruiker voor elke liedje
    in `info_lijst`. Retourneert de track id van de gemaakte keuze.
    :param info_lijst: lijst met alle gevonden liedjes (+ artiest & id)
    :return: track id-nummer van de gekozen lied.
    """
    nummering = 0
    m_len = max_lengte_string(info_lijst)  # Code voor leesbaarheid.
    print("Maak een keuze uit de volgende tracks:")
    for opties in info_lijst:
        nummering += 1
        titel, artist = opties[0], opties[1]
        print(f"{nummering:<4} {titel:<{m_len}} {artist}")

    keuze = int(input("Uw keuze: "))
    keuze_track_id = info_lijst[keuze - 1][2]
    return keuze_track_id


def max_lengte_string(lijst_titel):
    """ Retourneer van de langste titel uit `lijst_titel` de lengte.
    Dit wordt gebruikt om de gegevens uit het lijst netjes te tonen.
    :return: de maximale string lengte voor titel."""
    max_lengte = 0
    for titels in lijst_titel:
        if len(titels[0]) > max_lengte:
            max_lengte = len(titels[0]) + 4  # +4 is tab lengte.
    return max_lengte


def main():
    """ Start de hele applicatie op. Hier bevind zich de volgorde van de
     functies en methodes met als comment een korte samenvatting. """
    # Bestanden check.
    opstarten_db()  # Verbinden met database en cursor maken.
    tekst_bestand = check_bestand()  # Check .txt bestand.
    naam = naam_playlist()  # Check naam playlist.
    add_playlist_naam(naam)  # Voeg playlist toe.

    # Start import playlist.
    info_lijst = get_lijnen(tekst_bestand)  # Lees en haal lijnen op.
    lied_gegevens = zoek_worden(info_lijst)  # Sla de zoekresultaten op.
    playlist_id = get_playlist_id(naam)  # Zoek playlist id nummer.
    import_playlist(lied_gegevens, playlist_id)  # Voeg liedjes toe.

    # Sluit de cursor en de verbinding met de database.
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
