import os
from flask import Flask, session,redirect,url_for,request

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import json



app = Flask(__name__)

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
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    return redirect(url_for('get_playlists'))
    
@app.route('/redirect')
def redirect_page():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists'))

    
@app.route('/get_playlists')
def get_playlists(sp_obj):
    sp = sp_obj
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
                tracks_info = [item['track']['name'] for item in playlist_tracks['items'] if item['track'] is not None]
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
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5001,debug=True)