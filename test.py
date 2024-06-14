from flask import Flask, redirect, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import yt_dlp as youtube_dl
from playlistFinder import get_playlists
from mp3Finder import process_one_song, process_song_list
from musereco import give_recommendations


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
playlistGlobal = None

app.config['SECRET_KEY'] = 'key'

client_id = 'a376fc207dbb49158be47873998e16af'
client_secret = 'e26cc9aeb4e04173beff691a527630e3'
#redirect_uri = 'http://localhost:5000/redirect'
redirect_uri = 'http://127.0.0.1:5001/redirect'
#redirect_uri = 'https://7a63-67-188-104-131.ngrok-free.app/redirect'

scope = 'playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True

)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    return 'Welcome to the Spotify Playlist Processor! <a href="/login">Login to Spotify</a>'

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists_ui'))

@app.route('/get_playlists')
def get_playlists_ui():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    print("Fetching your playlists...")

    playlists = get_lists()
    playlist_options = ""
    for i, (name, _) in enumerate(playlists.items()):
        playlist_options += f"<option value='{i}'>{name}</option>"
    
    return f'''
        <form action="/select_playlist" method="post">
            <label for="playlists">Choose a playlist:</label>
            <select name="playlist" id="playlists">
                {playlist_options}
            </select>
            <input type="submit" value="Select Playlist">
        </form>
    '''
@app.route('/select_playlist', methods=['POST'])
def select_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlist_index = int(request.form['playlist'])
    sp = Spotify(auth_manager=sp_oauth)
    playlists = get_lists()
    selected_playlist = list(playlists.items())[playlist_index]
    playlist_name, playlist_details = selected_playlist
    playlist_id = playlist_details['id']
    tracks = playlist_details['tracks']

    logging.info(f"Selected playlist: {playlist_name}")

    # Ensure tracks is a list of dictionaries with 'name' and 'artist'
    formatted_tracks = [{'name': track['name'], 'artist': track['artist']} for track in tracks]
    
    list_of_songs = process_song_list(formatted_tracks)

    # Assuming give_recommendations is a function that processes the list of songs and provides recommendations
    nn = give_recommendations(list_of_songs)

    logging.info(f'Nearest neighbors: ')
    for neighbor in nn:
        logging.info(f'Nearest neighbor: {neighbor}')

    recommendations_html = f"<h1>Recommendations for {playlist_name}</h1><ul>"
    for neighbor in nn:
        recommendations_html += f"<li>{neighbor}</li>"
    recommendations_html += "</ul>"
    recommendations_html += '<a href="/">Back to Home</a>'

    return recommendations_html

def get_lists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
     
    try:
        user_info = sp.current_user()
        user_id = user_info['id']
    except Exception as e:
        pass

    try:
        playlists = sp.current_user_playlists(limit=5)['items']
    except Exception as e:
        pass
    
    all_playlists = {}
    for playlist in playlists:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        all_tracks = []
        offset = 0
        while True:
            try:
                playlist_tracks = sp.playlist_tracks(playlist_id, offset=offset)
                if playlist_tracks is None or 'items' not in playlist_tracks:
                    break
                tracks_info = [{'name': item['track']['name'], 'artist': item['track']['artists'][0]['name']} for item in playlist_tracks['items'] if item['track'] is not None]
                all_tracks.extend(tracks_info)
                if len(playlist_tracks['items']) < 100:
                    break
                offset += 100
            except Exception as e:
                pass
        
        all_playlists[playlist_name] = {
            "id": playlist_id,
            "tracks": all_tracks
        }
    return all_playlists

if __name__ == "__main__":
    app.run(debug=True,port=5001)
