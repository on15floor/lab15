import os
import csv
from io import StringIO
from datetime import timedelta
from argparse import ArgumentParser

import requests
from bs4 import BeautifulSoup


def _get_song_name(line):
    songtag = line.find(class_="songs-list__col--song")
    songname = songtag.find(class_="songs-list-row__song-name")
    return songname.contents[0]


def _get_artist(line):
    arttag = line.find(class_="songs-list__col--artist")
    artistname = arttag.find(class_="songs-list-row__link")
    return artistname.contents[0]


def _get_album(line):
    albtag = line.find(class_="songs-list__col--album")
    albname = albtag.find(class_="songs-list-row__link")
    return albname.contents[0]


def _get_duration(line):
    timetag = line.find(class_="songs-list-row__length")
    mins, secs = (int(i) for i in timetag.contents[0].split(':'))
    return str(timedelta(minutes=mins, seconds=secs))


def _get_links(soup):
    applelinks = soup.find_all('meta', attrs={"property": "music:song"})
    for link in applelinks:
        yield link.get("content")


def _parse_playlist(playlist):
    response = requests.get(playlist)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = _get_links(soup)
    table = soup.find(class_='songs-list typography-callout')

    for song in table.find_all(class_='songs-list-row'):
        yield {
            "title": _get_song_name(song),
            "artist": _get_artist(song),
            "album": _get_album(song),
            "duration": _get_duration(song),
            'link': next(links)
        }


def playlist_saver(playlist_link, folder=None):
    songs_data = [s for s in _parse_playlist(playlist_link)]
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


def playlist_data_gen(playlist_link):
    songs_data = [s for s in _parse_playlist(playlist_link)]
    if songs_data:
        data = StringIO()
        csv_buffer = csv.writer(data)

        field_names = songs_data[0].keys()
        csv_buffer.writerow(field_names)
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for song in songs_data:
            csv_buffer.writerow(song.values())
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('--playlist', required=True, help='playlist link')
    parser.add_argument('--dst_path', required=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    playlist_saver(playlist_link=args.playlist, folder=args.dst_path)
