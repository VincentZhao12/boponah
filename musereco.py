import os
import numpy as np
import librosa
import time
import logging
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Creates a feature matrix based on an audio part, this will be used later to create the recommendation system
# Parameters: file_path - the path to the audio file
# Returns: a feature matrix
def extract_audio_features(file_path):
    y, sr = librosa.load(file_path, sr=None)  # sr=None to preserve the original sample rate
    features = {
        'mfcc': librosa.feature.mfcc(y=y, sr=sr).mean(axis=1),
        'chroma': librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1),
        'spectral_contrast': librosa.feature.spectral_contrast(y=y, sr=sr).mean(axis=1),
        'tonnetz': librosa.feature.tonnetz(y=y, sr=sr).mean(axis=1),
        'zcr': librosa.feature.zero_crossing_rate(y).mean(),
        'tempo': librosa.beat.tempo(y=y, sr=sr)[0]
    }
    return np.hstack(list(features.values()))

# Lists all files in a folder. Helper method to store all of the audio files
# Parameters: folder_path - the path to the folder
# Returns: a list of file paths
def list_files_in_folder(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        if os.path.isfile(full_path):
            files.append(full_path)
    return files

# Saves the features and songs to a .npz file to be later used in the recommendation system
# Parameters: features_dict - a dictionary containing the features of the songs
#             song_list - a list of song names
#             file_path - the path to save the .npz file
# Returns: None
def save_features_and_songs(features_dict, song_list, file_path):
    np.savez(file_path, features=features_dict, songs=song_list)
    logging.info(f'Features and songs saved to {file_path}')

# Loads the features and songs from a .npz file
# Parameters: file_path - the path to the .npz file
# Returns: a tuple containing the features dictionary and the list of songs
def load_features_and_songs(file_path):
    if os.path.exists(file_path):
        data = np.load(file_path, allow_pickle=True)
        features_dict = data['features'].item() if 'features' in data else {}
        song_list = data['songs'].tolist() if 'songs' in data else []
        logging.info(f'Features and songs loaded from {file_path}')
        return features_dict, song_list
    else:
        return {}, []

# Aggregates the features using PCA. This is used to create a user profile based on the playlist
# Parameters: features_list - a list of features
#             pca - the PCA model
# Returns: the aggregated features
def aggregate_features_pca(features_list, pca):
    return pca.transform(features_list).mean(axis=0)

# Processes the files to extract features and add them to the features dictionary
# Parameters: list_of_audio_files - a list of audio file paths
#             features_dict - a dictionary containing the features of the songs
#             start_time - the start time of the process
#             total_files - the total number of files
# Returns: None
def process_files(list_of_audio_files, features_dict, start_time, total_files):
    for i, file in enumerate(list_of_audio_files):
        file_name_without_ext = os.path.splitext(os.path.basename(file))[0]
        if file_name_without_ext not in features_dict:
            logging.info(f'Processing file {i + 1}/{total_files}: {file}')
            features = extract_audio_features(file)
            features_dict[file_name_without_ext] = features
            file_time = time.time() - start_time
            elapsed_time = time.time() - start_time
            remaining_files = total_files - (i + 1)
            estimated_total_time = (elapsed_time / (i + 1)) * total_files
            estimated_remaining_time = estimated_total_time - elapsed_time
            logging.info(f'Added features for file {file}. Time taken: {file_time:.2f} seconds.')
            logging.info(f'Elapsed time: {elapsed_time:.2f} seconds. Estimated remaining time: {estimated_remaining_time:.2f} seconds.')
        else:
            logging.info(f'Skipping file {i + 1}/{total_files}: {file} (already processed).')

# Provides recommendations based on the user's playlist
# Parameters: playlist_files - a list of playlist files
#             features_file - the path to the .npz file containing the features
# Returns: a list of recommended songs
            
def give_recommendations(playlist_files, features_file='audio_features.npz'):
    if os.path.exists(features_file):
        logging.info('Loading features from file...')
        features_dict, song_list = load_features_and_songs(features_file)
    else:
        logging.error('Features file does not exist.')
        features_dict, song_list = {}, []

    # Process any new playlist files not in the features dictionary
    new_files = [file for file in playlist_files if file not in features_dict]
    if new_files:
        logging.info('Processing new files...')
        for file in new_files:
            file = 'songs/'+file + '.mp3'
            features = extract_audio_features(file)
            file_name_without_ext = os.path.splitext(os.path.basename(file))[0]
            features_dict[file_name_without_ext] = features

        # Save updated features and songs
        save_features_and_songs(features_dict, list(features_dict.keys()), features_file)

    # Convert dictionary to lists for further processing
    filenames = list(features_dict.keys())
    X = np.array(list(features_dict.values()))

    # Standardize features before PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Apply PCA
    pca = PCA(n_components=20)  # Adjust n_components as needed
    X_pca = pca.fit_transform(X_scaled)

    # Extract features for the playlist files from the features dictionary
    logging.info(f'Extracting features from playlist files: {playlist_files}...')
    playlist_features = [features_dict[os.path.splitext(os.path.basename(file))[0]] for file in playlist_files if os.path.splitext(os.path.basename(file))[0] in features_dict]

    if not playlist_features:
        logging.error('None of the playlist files are found in the features dictionary.')
        return []

    # Standardize and aggregate playlist features
    playlist_features_scaled = scaler.transform(playlist_features)
    user_profile = aggregate_features_pca(playlist_features_scaled, pca)
    
    # Train k-NN model
    logging.info('Training k-NN model...')
    knn = NearestNeighbors(n_neighbors=8, algorithm='ball_tree')
    knn.fit(X_pca)
    
    logging.info('Finding nearest neighbors...')
    distances, indices = knn.kneighbors([user_profile])

    # Filter out query files from the nearest neighbors
    nearest_neighbors = [filenames[idx] for idx in indices[0] if filenames[idx] not in [os.path.splitext(os.path.basename(file))[0] for file in playlist_files]]

    return nearest_neighbors
  
def process_files_from_folder(folder_path, features_dict, start_time):
    list_of_audio_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp3') or f.endswith('.wav')]  # Adjust extensions as needed
    total_files = len(list_of_audio_files)
    
    for i, file in enumerate(list_of_audio_files):
        file_name_without_ext = os.path.splitext(os.path.basename(file))[0]
        if file_name_without_ext not in features_dict:
            logging.info(f'Processing file {i + 1}/{total_files}: {file}')
            features = extract_audio_features(file)
            features_dict[file_name_without_ext] = features
            file_time = time.time() - start_time
            elapsed_time = time.time() - start_time
            remaining_files = total_files - (i + 1)
            estimated_total_time = (elapsed_time / (i + 1)) * total_files
            estimated_remaining_time = estimated_total_time - elapsed_time
            logging.info(f'Added features for file {file}. Time taken: {file_time:.2f} seconds.')
            logging.info(f'Elapsed time: {elapsed_time:.2f} seconds. Estimated remaining time: {estimated_remaining_time:.2f} seconds.')
        else:
            logging.info(f'Skipping file {i + 1}/{total_files}: {file} (already processed).')
    save_features_and_songs(features_dict, list(features_dict.keys()), 'audio_features.npz')




  

if __name__ == "__main__":
    # Replace with actual playlist files you want to query
    folder_path = 'songs'  # Adjust the folder path as needed
    features_dict = {}
    start_time = time.time()
    process_files_from_folder(folder_path, features_dict, start_time)