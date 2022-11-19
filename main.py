import requests
import os
from bs4 import BeautifulSoup
import spotipy

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
validation = True
while validation:
    user_date = input("Enter date which you would like to travel to in DD-MM-YYYY format: ").split("-")[::-1]
    try:
        historic_date = f"{user_date[0]}-{user_date[1]}-{user_date[2]}"
        response = requests.get(f"https://www.billboard.com/charts/hot-100/{historic_date}")
        response.raise_for_status()
    except (IndexError, requests.exceptions.HTTPError):
        print("Invalid date format")
    else:
        validation = False

soup = BeautifulSoup(response.text, "html.parser")
hot_100 = soup.select(".lrv-u-width-100p .lrv-a-unstyle-list h3#title-of-a-story")
song_titles = [song.getText().strip() for song in hot_100]
spotify = spotipy.Spotify(
    auth_manager=spotipy.oauth2.SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://valentino7504.github.io/Musical-Time-Machine/",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
    )
)
user_id = spotify.current_user()["id"]
song_uris = []
for song in song_titles:
    result = spotify.search(q=f"track:{song} year:{user_date[0]}", limit=(1, 1, 1), type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        continue
playlist = spotify.user_playlist_create(user=user_id, name=f"{user_date[2]}-{user_date[1]}-{user_date[0]} Time Machine",
                                        public=False,
                                        description=f"A playlist with the Billboard Hot 100 from {user_date[2]}-{user_date[1]}-{user_date[0]}")
spotify.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
