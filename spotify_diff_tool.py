import spotipy
import json

from math import ceil
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from datetime import date

PLAYLIST_NAME = "between lines: " + str(date.today())

def get_liked_track_uris(client, NUM_LIKED_TRACKS):
    # Get liked tracks
    print("Getting liked tracks...")
    liked_track_uris = set()

    batch_count = ceil(NUM_LIKED_TRACKS / 50)
    batches = range(0, batch_count)
    for batch in batches:

        # print("LT Batch Count: " + str(batch + 1))
        liked_tracks = client.current_user_saved_tracks(limit = 50, offset = batch * 50)['items']

        for track in liked_tracks:

            uri = track["track"]["uri"]
            liked_track_uris.add(uri)
    
    return liked_track_uris

def get_playlist_uris(client, NUM_PLAYLISTS, DISPLAY_NAME):
    # Get playlists
    print("Getting playlists...")
    months = ['january', 'february', 
              'march', 'april', 'may', 
              'june', 'july', 'august', 
              'september', 'october', 
              'november', 'december']
    playlist_uris = dict()

    batch_count = ceil(NUM_PLAYLISTS / 50)
    batches = range(0, batch_count)

    for batch in batches:

        # print("PL Batch Count: " + str(batch + 1))
        playlists = client.current_user_playlists(limit = 50, offset = batch * 50)['items']

        for playlist in playlists:

            uri = playlist["uri"]
            playlist_name = playlist["name"]

            # Only select playlists that are by me
            if (playlist["owner"]["display_name"] == DISPLAY_NAME
            ):

                # Do not include "favorites" playlists 
                if "favorites" in playlist_name:
                    continue

                # Do not include "between lines"
                if "between lines" == playlist_name:
                    continue

                # Do not include monthly playlists (ex: may2022)
                if any(month in playlist_name for month in months):
                    continue

                playlist_uris[uri] = {"name" : playlist_name, "count" : playlist["tracks"]["total"]}

    return playlist_uris

def get_seen_track_uris(client, playlist_uris):
    # For each playlist in the list, go through each track
    # Add the track to a "seen" playlist
    print("Getting seen tracks...")

    seen_track_uris = set()
    i = 0
    for playlist_uri in playlist_uris:

        playlist_id = playlist_uri.split(":")[2]
        playlist_name = playlist_uris[playlist_uri]["name"]
        playlist_size = playlist_uris[playlist_uri]["count"]

        # print("Playlist Count: " + str(i))
        # print("Playlist Length: " + str(playlist_size))

        if playlist_size != 0:

            batch_count = playlist_size / 50
            batches = range(0, ceil(batch_count))

            for batch in batches:

                tracks = client.playlist_tracks(playlist_id, limit = 50, offset = batch * 50)["items"]

                for track in tracks:

                    uri = track["track"]["uri"]
                    seen_track_uris.add(uri)

        i = i + 1
    
    return seen_track_uris

def create_playlist(client, track_uris, USER_NAME):
    print("Creating playlist...")

    playlist = client.user_playlist_create(USER_NAME, PLAYLIST_NAME, public=False)
    playlist_id = playlist["uri"]

    track_uris_list = list(track_uris)
    batch_count = len(track_uris) / 100
    batch_id = 0

    while batch_id < batch_count:
        lower = (batch_id * 100)
        upper = ((batch_id + 1) * 100)
        client.playlist_add_items(playlist_id, track_uris_list[lower : upper])
        
        batch_id = batch_id + 1

def main():
    # Get Spotify API credentials (I have them in a separate JSON)
    # I suggest you write your secrets this way as well!
    print("Reading secrets...")
    with open('secrets/spotify_secrets.json') as json_data:
        secrets = json.load(json_data)

    CLIENT_ID = secrets["CLIENT_ID"]
    CLIENT_SECRET = secrets["CLIENT_SECRET"]
    REDIRECT_URI = secrets["REDIRECT_URI"]
    USER_NAME = secrets["USER_NAME"]
    DISPLAY_NAME = secrets["DISPLAY_NAME"]

    # Set up Spotify API access
    client = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = REDIRECT_URI,
        scope = 'user-top-read playlist-modify-private user-library-read playlist-modify-public'
    ))

    # Get the number of saved tracks
    NUM_LIKED_TRACKS = client.current_user_saved_tracks()["total"]
    NUM_PLAYLISTS = client.current_user_playlists()["total"]

    print("TODO: prevent duplicate songs by maintaining a Set<Title + Artist>")

    # Get list of playlists
    playlist_uris = get_playlist_uris(client, NUM_PLAYLISTS, DISPLAY_NAME)
    print("Playlists: " + str(len(playlist_uris)))

    # Get list of seen tracks
    seen_track_uris = get_seen_track_uris(client, playlist_uris)
    print("Seen Tracks: " + str(len(seen_track_uris)))

    # Get list of tracks
    liked_track_uris = get_liked_track_uris(client, NUM_LIKED_TRACKS)
    print("Liked Tracks: " + str(len(liked_track_uris)))

    missing_uris = liked_track_uris.difference(seen_track_uris)
    print("Missing Tracks: " + str(len(missing_uris)))

    create_playlist(client, missing_uris, USER_NAME)

    print("Finished!")

if __name__ == '__main__':
    main()
