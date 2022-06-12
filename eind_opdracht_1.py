"""
Auteur: G van der Biezen
Naam bestand: eind_opdracht_1.py

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


def verbinding_maken(db_file):
    """ Controleert of het bestand in de directory bestaat. Maakt daarna
    een verbinding met de SQLite database aangegeven door de `db_file`.
    Als het bestand niet bestaat, wordt het programma gesopt.
    :param db_file: database file.
    :return: connection object of None.
    """
    # verbinding maken als het bestand bestaat.
    if os.path.isfile(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return None
    # programma stoppen als het bestand niet bestaat
    else:
        import sys
        print(f"{db_file} niet gevonden.")
        sys.exit(1)


def cursor():
    """ Maakt een cursor door eerst verbinding te maken met de database."""
    database_naam = "chinook.db"
    conn = verbinding_maken(database_naam)
    return conn.cursor()  # cursor om de database te benaderen.


def gegevens_database():
    """ Vraagt de database voor de gewenste gegevens zoals artist, album
    en het aantal liedjes. Retourneert de eerste 10 regels in aflopend
    volgorde.
    :return: Een lijst van 10 regels. """
    cur = cursor()  # cursor om de database te benaderen.

    # vraag de database voor de gewenste gegevens, artist, albums en aantal.
    cur.execute('''SELECT artists.Name, albums.Title, COUNT(*)
                FROM invoice_items
                INNER JOIN tracks ON tracks.TrackId = invoice_items.TrackId
                INNER JOIN albums ON albums.AlbumId = tracks.AlbumId
                INNER JOIN artists ON albums.ArtistId = artists.ArtistId
                GROUP BY albums.Title
                ORDER BY COUNT(*) DESC''')

    # sla de opgehaalde data op voor de eerste 10 regels.
    top_lijst = cur.fetchmany(10)
    return top_lijst


def spacing_padding():
    """ Haal de maximale string lengte voor de kolom artist en albums
    gebaseerd op de langste word zodat de geprinte data leesbaar is.
    :return: de maximale string lengte voor artist en album."""
    len_art = 0  # lengte van de langste artiest naam in het lijst.
    len_tit = 0  # lengte van de langste album titel in het lijst.
    top10_lijst = gegevens_database()
    # Vergelijk elke regel met elkaar en slaat de langste lengte op.
    for string_lengte in top10_lijst:
        if len(string_lengte[0]) > len_art:
            len_art = len(string_lengte[0]) + 4  # +4 is de lengte van een tab
        elif len(string_lengte[1]) > len_tit:
            len_tit = len(string_lengte[1]) + 4
    return len_art, len_tit


def top10_albums():
    """ Print the top 10 albums uit met de meest beluisterde liedjes."""
    top_10_lijst = gegevens_database()
    positie = 0  # nummering voor de posities in de top 10 list.
    len_art, len_tit = spacing_padding()
    print("Top 10 Albums")
    print("-------------")
    for top in top_10_lijst:
        positie += 1
        artist, album_naam, aantal_keren = top[0], top[1], top[2]
        print(f"{positie:<4} {artist:<{len_art}} {album_naam:<{len_tit}} {aantal_keren}")


if __name__ == '__main__':
    top10_albums()
