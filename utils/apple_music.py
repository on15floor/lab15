import os
from datetime import timedelta
import csv

from bs4 import BeautifulSoup
import requests


def get_song_name(line):
    songtag = line.find(class_="songs-list__col--song")
    songname = songtag.find(class_="songs-list-row__song-name")
    return songname.contents[0]


def get_artist(line):
    arttag = line.find(class_="songs-list__col--artist")
    artistname = arttag.find(class_="songs-list-row__link")
    return artistname.contents[0]


def get_album(line):
    albtag = line.find(class_="songs-list__col--album")
    albname = albtag.find(class_="songs-list-row__link")
    return albname.contents[0]


def get_duration(line):
    timetag = line.find(class_="songs-list-row__length")
    mins, secs = (int(i) for i in timetag.contents[0].split(':'))
    return str(timedelta(minutes=mins, seconds=secs))


def get_links(soup):
    applelinks = soup.find_all('meta', attrs={"property": "music:song"})
    for link in applelinks:
        yield link.get("content")


def get_playlist(playlist):
    response = requests.get(playlist)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = get_links(soup)
    table = soup.find(class_='songs-list typography-callout')

    for song in table.find_all(class_='songs-list-row'):
        yield {
            "title": get_song_name(song),
            "artist": get_artist(song),
            "album": get_album(song),
            "duration": get_duration(song),
            'link': next(links)
        }


def main(playlist_link, folder=None):
    songs_data = [s for s in get_playlist(playlist_link)]
    if not folder:
        print(songs_data)
        return

    if songs_data:
        field_names = songs_data[0].keys()
        fname = os.path.join(folder, f'playlist_{len(songs_data)}.csv')
        with open(fname, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(field_names)
            for song in songs_data:
                writer.writerow(song.values())


if __name__ == '__main__':
    playlist = 'https://music.apple.com/ru/playlist/armada-chill/pl.8dfe81575d33494db90c12e4c3a180a9?l=uk'
    main(playlist, os.path.join('/Users/a.e.anisimov/Downloads/'))
