import spotipy
import spotipy.util as util
from datetime import datetime
import json

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
    sp = spotipy.Spotify(auth=token)

    # Create the monthly favorites playlist
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    current_month = months[datetime.now().month - 1]
    current_year = str(datetime.now().year)
    timestamp = current_month + current_year 
    playlist_name = timestamp + " - favorites"
    print("Making a " + timestamp + " playlist...")
    playlist_description = ""
    playlist = sp.user_playlist_create(user=USER_NAME, name=playlist_name, public=False, description=playlist_description)

    # Get the top 50 tracks from the last month
    results = sp.current_user_top_tracks(limit = 50, time_range = time_range)
    track_ids = [track['id'] for track in results['items']]

    # Add the tracks to the playlist
    print("Adding tracks to " + timestamp + "...")
    sp.playlist_add_items(playlist_id = playlist['id'], items = track_ids)

    print("Done!")

if __name__ == '__main__':
    main()
