from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import youtube_dl

def search_youtube(query):
    # Set up the WebDriver (assumes ChromeDriver is in PATH)
    driver = webdriver.Chrome()
    driver.get("https://www.youtube.com")

    # Find the search bar and enter the query
    search_bar = driver.find_element(By.NAME, "search_query")
    search_bar.send_keys(query)
    search_bar.send_keys(Keys.RETURN)

    # Wait for the results to load and display the title
    time.sleep(3)

    # Find the first video link
    video = driver.find_element(By.XPATH, '//*[@id="video-title"]')
    video_url = video.get_attribute('href')

    # Close the WebDriver
    driver.quit()
    return video_url




'''
def download_mp3(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

if __name__ == "__main__":
    query = "Imagine Dragons Believer"
    video_url = search_youtube(query)
    print("Found video URL:", video_url)

    output_path = 'output/%(title)s.%(ext)s'  # Save as title.mp3 in the output directory
    download_mp3(video_url, output_path)
    print("Downloaded and converted to MP3.")
'''
import yt_dlp as youtube_dl

def download_mp3(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ss', '10', '-t', '40'  # Start at 0 seconds, extract 30 seconds
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
        title = row['title']  # Assuming the column name is 'title'
        artist = row['artist']  # Assuming the column name is 'artist'
        search_query = f"{title} {artist}" + " lyrics"
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

       
        

if __name__ == "__main__":
    csv_file_path = 'top10s.csv'
    file_encoding = 'latin1'  # Replace with the correct encoding if needed
    process_csv(csv_file_path, file_encoding)