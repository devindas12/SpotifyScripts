import spotipy
import spotipy.util as util
from datetime import datetime
import json
from math import ceil

# I often listen to full albums/playlists on repeat, so songs that I don't 
# actually like will show up in my top songs. 
#
# Helper function to remove non-liked tracks from my top songs:
def filter_tracks(top_tracks, liked_song_ids):
    removed_song_count = 0

    for track in top_tracks:
        if track not in liked_song_ids:
            top_tracks.remove(track)
            removed_song_count = removed_song_count + 1 

    print(f"Removed {removed_song_count} non-liked songs from the playlist.")

# Get liked tracks
def get_liked_track_uris(client):
    print("Getting liked tracks...")
    liked_track_uris = set()

    # Get liked track count from Spotify
    NUM_LIKED_TRACKS = client.current_user_saved_tracks()["total"]

    # I have a lot of liked songs, batch request + offset
    batch_count = ceil(NUM_LIKED_TRACKS / 50)
    batches = range(0, batch_count)
    for batch in batches:

        # print("LT Batch Count: " + str(batch + 1))
        liked_tracks = client.current_user_saved_tracks(limit = 50, offset = batch * 50)['items']

        # Extract the IDs
        for track in liked_tracks:
            id = track["track"]["id"]
            liked_track_uris.add(id)
    
    return liked_track_uris

# Create the monthly favorites playlist
def create_monthly_playlist(client, USER_NAME):
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    current_month = months[datetime.now().month - 1]
    current_year = str(datetime.now().year)
    timestamp = current_month + current_year 
    
    playlist_name = timestamp + " - favorites"
    print("Making a " + timestamp + " playlist...")
    playlist_description = ""
    playlist = client.user_playlist_create(user=USER_NAME, name=playlist_name, public=False, description=playlist_description)
    return playlist

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

    # Set the scope of the authorization
    SCOPE = 'user-top-read playlist-modify-private user-library-read playlist-modify-public'

    # Set the time range for the top tracks
    time_range = 'short_term'

    # Create a Spotipy object
    token = util.prompt_for_user_token(username=USER_NAME, scope=SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    client = spotipy.Spotify(auth=token)

    # Get the top 50 tracks from the last month
    print("Getting top 50 tracks...")
    results = client.current_user_top_tracks(limit = 50, time_range = time_range)
    track_ids = [track['id'] for track in results['items']]

    # Get liked songs, and then filter the top 50 songs through them
    liked_track_ids = get_liked_track_uris(client)
    filter_tracks(track_ids, liked_track_ids)

    playlist = create_monthly_playlist(client, USER_NAME)
    client.playlist_add_items(playlist_id = playlist['id'], items = track_ids)

    print("Done!")

if __name__ == '__main__':
    main()
