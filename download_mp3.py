import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
import numpy as np
import os
from tempfile import mktemp
import pickle

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

df = pd.read_csv("data/df_spotify_small.csv")

df_splits = []

def download_mp3(url, id):
    response = requests.get(url)
    
    # Save the MP3 file temporarily
    with open("temp.mp3", "wb") as f:
        f.write(response.content)
    
    # Convert MP3 to WAV
    mp3_audio = AudioSegment.from_mp3("temp.mp3")
    mp3_audio.export(f"data/songs/{id}.wav", format="wav")
    
    # Remove the temporary MP3 file
    
    os.remove("temp.mp3")
            
    return None

for i in range(1140):
    df_splits.append(df.iloc[i * 50:i * 50 + 50,:])
    
print("starting saving")

for i, df_split in enumerate(df_splits):
    songs_list = list(df_split["track_id"])

    tracks = sp.tracks(songs_list)["tracks"]
    
    print(f"Running: {i}")
    
    for track in tracks:
        # print("hi")
        if track['preview_url']:
            download_mp3(track['preview_url'], track['id'])