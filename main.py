import sys
from spotify_dl.scaffold import log
from spotify_dl.utils import sanitize
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import easygui
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

playlist_link = easygui.enterbox("Enter the link for your spotify playlist:")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

def fetch_tracks(sp, url):
    songs_list = []
    song_names = []
    offset = 0

    while True:
        items = sp.playlist_items(playlist_id=url,

                                    fields='items.track.name,items.track.artists(name, uri),'
                                            'items.track.album(name, release_date, total_tracks, images),'

                                            'items.track.track_number,total, next,offset,'
                                            'items.track.id',
                                    additional_types=['track'], offset=offset)
        total_songs = items.get('total')
        for item in items['items']:
            track_name = item['track']['name']
            offset += 1

            song_names.append(track_name)

        log.info(f"Fetched {offset}/{total_songs} songs in the playlist")
        if total_songs == offset:
            log.info('All pages fetched, time to leave. Added %s songs in total', offset)
            break

    return song_names


def parse_spotify_url(url):

    if url.startswith("spotify:"):
        log.error("Spotify URI was provided instead of a playlist/album/track URL.")
        sys.exit(1)
    parsed_url = url.replace("https://open.spotify.com/", "")
    item_type = parsed_url.split("/")[0]
    item_id = parsed_url.split("/")[1]
    return item_type, item_id


def get_item_name(sp, item_type, item_id):
    if item_type == 'playlist':
        name = sp.playlist(playlist_id=item_id, fields='name').get('name')
    return sanitize(name)

def validate_spotify_url(url):
    item_type, item_id = parse_spotify_url(url)
    log.debug(f"Got item type {item_type} and item_id {item_id}")
    if item_type not in ['album', 'track', 'playlist']:
        log.error("Only albums/tracks/playlists are supported")
        return False
    if item_id is None:
        log.error("Couldn't get a valid id")
        return False
    return True

songs = fetch_tracks(sp,playlist_link)

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
driver = webdriver.Chrome(ChromeDriverManager().install())

result = []

for song in songs:

    driver.get('https://getsongbpm.com/')
    elems = driver.find_element_by_name("search_db")

    elems.send_keys(song)
    elems.send_keys(Keys.RETURN)

    try:
        driver.find_element_by_xpath("//div[@class=\'search_results\']//a").click()
        bpm = driver.find_element_by_xpath("//div[@class=\'col-xs-12 col-sm-3\']//span").text
        result.append(song + " " + bpm + "\n")
    except:
        result.append("Unable to calculate BPM for " + song + "\n")

with open("Output.txt", "w") as txt_file:
    for line in result:
        txt_file.write(line)

driver.quit()