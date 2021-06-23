import requests
import os
import re
import spotipy
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

URL = "https://www.billboard.com/charts/hot-100/"
rex = re.compile("(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])")
correct_input = False

while not correct_input:
    historical_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

    if rex.match(historical_date):
        # Billboard Hot 100 scraping
        response = requests.get(URL + historical_date)
        website_html = response.text
        soup = BeautifulSoup(website_html, "html.parser")

        all_songs = soup.find_all(name="span", class_="chart-element__information__song")
        song_titles = [song.getText() for song in all_songs]

        # Spotify Authentication
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope="playlist-modify-private",
                redirect_uri="http://example.com",
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                show_dialog=True,
                cache_path="token.txt",
            )
        )

        user_id = sp.current_user()["id"]
        # print(user_id)

        # Search Spotify for songs by title
        song_uris = []
        year = historical_date.split("-")[0]

        for song in song_titles:
            result = sp.search(q=f"track:{song} year:{year}", type="track")
            # print(result)

        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

        # Creating a new private playlist in Spotify
        playlist = sp.user_playlist_create(user=user_id, name=f"{historical_date} Billboard 100", public=False)
        # print(playlist)

        # Adding songs found into the new playlist
        sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

        correct_input = True
