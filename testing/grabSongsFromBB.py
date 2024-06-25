import billboard
import pandas as pd
from datetime import datetime, timedelta
import time

def fetch_billboard_data(start_date, end_date, interval='weekly'):
    """
    Fetch Billboard Hot 100 data between the specified dates.
    
    Args:
    - start_date (str): The start date in the format 'YYYY-MM-DD'.
    - end_date (str): The end date in the format 'YYYY-MM-DD'.
    - interval (str): The interval for fetching data. Options are 'weekly'.
    
    Returns:
    - DataFrame: A pandas DataFrame containing the Billboard Hot 100 data.
    """
    # Generate dates for fetching data
    date_format = "%Y-%m-%d"
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    
    current_date = start
    all_chart_data = []
    unique_songs = set()

    total_dates = 0
    while current_date <= end:
        total_dates += 1
        current_date += timedelta(weeks=1)

    current_date = start
    processed_dates = 0
    start_time = time.time()

    while current_date <= end:
        try:
            date_str = current_date.strftime(date_format)
            chart = billboard.ChartData('hot-100', date=date_str)
            
            for song in chart:
                song_key = (song.title, song.artist)
                if song_key not in unique_songs:
                    unique_songs.add(song_key)
                    all_chart_data.append({
                        'date': date_str,
                        'position': song.rank,
                        'song_name': song.title,
                        'artist_name': song.artist,
                        'last_position': song.lastPos,
                        'peak_position': song.peakPos,
                        'weeks_on_chart': song.weeks
                    })
            processed_dates += 1
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / processed_dates) * total_dates
            remaining_time = estimated_total_time - elapsed_time
            print(f"Fetched data for {date_str}")
            print(f"Elapsed time: {elapsed_time:.2f} seconds, Estimated remaining time: {remaining_time:.2f} seconds")
        except Exception as e:
            print(f"Failed to fetch data for {date_str}: {e}")
        
        if interval == 'weekly':
            current_date += timedelta(weeks=1)

    return pd.DataFrame(all_chart_data)

# Fetch Billboard Hot 100 data from 2000 to 2024 as an example
df = fetch_billboard_data('2000-01-01', '2024-05-20')
df.to_csv('billboard_hot_100_2000_2024.csv', index=False)

print("Billboard Hot 100 data saved to billboard_hot_100_2000_2024.csv")
