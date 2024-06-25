from flask import Flask, redirect, request, session, url_for,render_template,jsonify
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

app.config['SECRET_KEY'] = 'key'

client_id = 'a376fc207dbb49158be47873998e16af'
client_secret = 'e26cc9aeb4e04173beff691a527630e3'
redirect_uri = 'http://127.0.0.1:5001/redirect'

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

@app.route('/')
def home():
    return render_template('home.html')

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

    sp = Spotify(auth_manager=sp_oauth)
    playlists = sp.current_user_playlists(limit=10)
    return render_template('playlists.html', playlists=playlists['items'])

@app.route('/select_playlist', methods=['POST'])
def select_playlist():
    data = request.get_json()
    playlist_id = data.get('playlist_id')

    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({'redirect': auth_url}), 401

    sp = Spotify(auth_manager=sp_oauth)
    playlist = sp.playlist(playlist_id)
    playlist_name = playlist['name']
    tracks = [{'name': track['track']['name'], 'artist': track['track']['artists'][0]['name']} for track in playlist['tracks']['items']]

    logging.info(f"Selected playlist: {playlist_name}")

    list_of_songs = process_song_list(tracks)
    recommendations = give_recommendations(list_of_songs)

    logging.info(f'Nearest neighbors: ')
    for neighbor in recommendations:
        logging.info(f'Nearest neighbor: {neighbor}')

    return jsonify({
        "playlist_name": playlist_name,
        "recommendations": recommendations
    })

@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route('/results', methods=['POST'])
def results():
    data = request.get_json()
    recommendations = data.get('recommendations')
    playlist_name = data.get('playlist_name')
    return render_template('results.html', recommendations=recommendations, playlist_name=playlist_name)

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
    app.run(debug=True, port=5001)



