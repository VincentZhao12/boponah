import os
from flask import Flask, session,redirect,url_for,request

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import json



app = Flask(__name__)

app.config['SECRET_KEY'] = 'key'

client_id = 'test'
client_secret = 'hehe'
redirect_uri = 'http://127.0.0.1:5000/redirect'
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
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    return redirect(url_for('get_playlists'))
    
@app.route('/redirect')
def redirect_page():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists'))

    
@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    user_info = sp.current_user()
    user_id = user_info['id']

    # Fetch and print the current user's playlists
    playlists = sp.current_user_playlists(limit=5)['items']
    all_playlists = {}
    for playlist in playlists:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        all_tracks = []
        offset = 0
        while True:
            playlist_tracks = sp.playlist_tracks(playlist_id, offset=offset)
            tracks_info = [item['track']['name'] for item in playlist_tracks['items']]
            all_tracks.extend(tracks_info)
            if len(playlist_tracks['items']) < 100:
                break
            offset += 100
        
        all_playlists[playlist_name] = all_tracks

    html_content = f"<h1>Playlists for user {user_id}</h1>"
    for playlist_name, tracks in all_playlists.items():
        html_content += f"<h2>{playlist_name}</h2><ul>"
        for track in tracks:
            html_content += f"<li>{track}</li>"
        html_content += "</ul>"

    return html_content
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)