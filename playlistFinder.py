from flask import Flask, request, redirect, session, url_for
import spotipy
import time
import json
from spotipy.oauth2 import SpotifyOAuth
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'test123'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = False
Session(app)

TOKEN_INFO = 'token_info'

# Set up Spotify API credentials
client_id = 'a376fc207dbb49158be47873998e16af'
client_secret = 'e26cc9aeb4e04173beff691a527630e3'
redirect_uri = 'http://127.0.0.1:5000/redirect'
scope = 'playlist-read-private'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
    )

@app.route('/')
def login():
    session.clear()  # Clear the session to ensure a fresh start
    print("Session cleared at login")
    auth_url = create_spotify_oauth().get_authorize_url()
    print(f"Redirecting to {auth_url}")
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    print(f"Token Info: {token_info}")
    if token_info:
        print("Login/auth successful")
    else:
        print("Login/auth failed")
    return redirect(url_for('get_playlists'))

@app.route('/get_playlists')
def get_playlists():
    token_info = session.get(TOKEN_INFO)
    if not token_info:
        print("Token not found, redirecting to login")
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Fetch and print the current user's ID
    user_info = sp.current_user()
    user_id = user_info['id']
    print(f'User ID: {user_id}')

    # Fetch and print the current user's playlists
    playlists = sp.current_user_playlists(limit=5)['items']
    all_playlists = {}
    for playlist in playlists:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        playlist_tracks = sp.playlist_tracks(playlist_id)
        
        tracks_info = [item['track']['name'] for item in playlist_tracks['items']]
        all_playlists[playlist_name] = tracks_info

    print(f"Playlists for user {user_id}: {json.dumps(all_playlists, indent=2)}")

    return json.dumps(all_playlists, indent=2)

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        print("No token info in session")
        return None

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        print("Token expired, refreshing...")
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
        print(f"Refreshed Token Info: {token_info}")

    return token_info

@app.route('/logout')
def logout():
    session.clear()
    print("Session cleared at logout")
    return redirect('/')

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)
