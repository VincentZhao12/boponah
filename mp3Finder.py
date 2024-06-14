from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import yt_dlp as youtube_dl
import os
import numpy as np
from youtubesearchpython import VideosSearch
from musereco import load_features_and_songs

npz_file_path = 'audio_features.npz'

def load_npz_file(file_path):
    if os.path.exists(file_path):
        features, list = load_features_and_songs(file_path)

        return list
        # Assuming the second item in the file is the list of songs
    return []


def save_to_npz_file(file_path, songs_list):
    np.savez(file_path, songs=songs_list)

def search_youtube(query):
    # Use youtube-search-python for faster searches
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    video_url = result['result'][0]['link']
    return video_url

def download_mp3(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ss', '10', '-t', '40'  # Start at 10 seconds, extract 30 seconds
        ],
        'outtmpl': output_path
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def process_csv(file_path, encoding='utf-8'):
    # Read the CSV file with the specified encoding
    df = pd.read_csv(file_path, encoding=encoding)

    # Loop through each title and artist in the CSV file
    for index, row in df.iterrows():
        title = row['song_name']  # Assuming the column name is 'title'
        artist = row['artist_name']  # Assuming the column name is 'artist'
        search_query = f"{title} {artist} lyrics"
        print(f"Processing: {search_query}")

        # Search YouTube for the title and artist
        video_url = search_youtube(search_query)
        print(f"Found video URL: {video_url}")

        # Define the output path
        output_path = f'songs/{title} - {artist}.mp3'

        # Download and extract 30-second MP3
        try:
            download_mp3(video_url, output_path)
        except Exception as e:
            print(f"Error downloading: {e}")
            continue
        else:
            print(f"Downloaded and converted to MP3 (30 seconds): {output_path}")

def process_one_song(song_name, artist_name):
    existing_songs = load_npz_file(npz_file_path)
    song_key = f"{song_name} - {artist_name}"

    if song_key in existing_songs:
        print(f"Skipping {song_key}, already exists.")
        return None
    
    search_query = f"{song_name} {artist_name} lyrics"
    print(f"Processing: {search_query}")

    # Search YouTube for the title and artist
    video_url = search_youtube(search_query)
    print(f"Found video URL: {video_url}")

    # Define the output path
    output_path = f'songs/{song_name} - {artist_name}'

    # Download and extract 30-second MP3
    try:
        download_mp3(video_url, output_path)
    except Exception as e:
        print(f"Error downloading: {e}")
        return None
    else:
        print(f"Downloaded and converted to MP3 (30 seconds): {output_path}")
        return song_key

def process_song_list(song_list):
    generated_files = []
    for song in song_list:
        song_key = process_one_song(song['name'], song['artist'])
        generated_files.append(song['name'] + " - " + song['artist'])
    
    return generated_files


if __name__ == "__main__":
    '''
    csv_file_path = 'billboard_hot_100_2000_2024.csv'
    file_encoding = 'latin1'  # Replace with the correct encoding if needed
    # process_csv(csv_file_path, file_encoding)
    song_name = "mahiye jinhe sohna darshan"
    process_one_song(song_name)
    
    song_list = ["song1", "song2", "song3"]  # Replace with your list of songs
    generated_files = process_song_list(song_list)
    print("Generated files:", generated_files)
    '''


