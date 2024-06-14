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

def list_files_in_folder(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        if os.path.isfile(full_path):
            files.append(full_path)
    return files
def save_features_and_songs(features_dict, song_list, file_path):
    np.savez(file_path, features=features_dict, songs=song_list)
    logging.info(f'Features and songs saved to {file_path}')

def load_features_and_songs(file_path):
    if os.path.exists(file_path):
        data = np.load(file_path, allow_pickle=True)
        features_dict = data['features'].item() if 'features' in data else {}
        song_list = data['songs'].tolist() if 'songs' in data else []
        logging.info(f'Features and songs loaded from {file_path}')
        return features_dict, song_list
    else:
        return {}, []

def aggregate_features_pca(features_list, pca):
    return pca.transform(features_list).mean(axis=0)

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
'''
def give_recommendations(playlist_files):
    folder_path = 'songs'
    features_file = 'audio_features.npz'
    
    if os.path.exists(features_file):
        logging.info('Loading features from file...')
        features_dict, song_list = load_features_and_songs(features_file)
    else:
        features_dict, song_list = {}, []

    logging.info('Extracting features from files...')
    list_of_audio_files = list_files_in_folder(folder_path)
    logging.info(f'Found {len(list_of_audio_files)} files.')

    start_time = time.time()
    total_files = len(list_of_audio_files)
    process_files(list_of_audio_files, features_dict, start_time, total_files)

    feature_extraction_time = time.time() - start_time
    logging.info(f'Feature extraction completed in {feature_extraction_time:.2f} seconds.')
    
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

    # Ensure playlist files are included in the features dictionary
    playlist_files_to_process = [file for file in playlist_files if os.path.splitext(os.path.basename(file))[0] not in features_dict]
    if playlist_files_to_process:
        logging.info('Processing playlist files...')
        process_files(playlist_files_to_process, features_dict, time.time(), len(playlist_files_to_process))
        # Re-save features to include playlist files
        save_features_and_songs(features_dict, list(features_dict.keys()), features_file)

        # Convert updated dictionary to lists for further processing
        filenames = list(features_dict.keys())
        X = np.array(list(features_dict.values()))

        # Standardize features before PCA
        X_scaled = scaler.fit_transform(X)

        # Apply PCA
        X_pca = pca.fit_transform(X_scaled)

    # Train k-NN model
    logging.info('Training k-NN model...')
    start_time = time.time()
    knn = NearestNeighbors(n_neighbors=8, algorithm='ball_tree')
    knn.fit(X_pca)
    training_time = time.time() - start_time
    logging.info(f'Training completed in {training_time:.2f} seconds.')
    
    # Example playlist query
    logging.info(f'Extracting features from playlist files: {playlist_files}...')
    playlist_features = [extract_audio_features(file) for file in playlist_files]
    playlist_features_scaled = scaler.transform(playlist_features)
    user_profile = aggregate_features_pca(playlist_features_scaled, pca)
    
    logging.info('Finding nearest neighbors...')
    start_time = time.time()
    distances, indices = knn.kneighbors([user_profile])
    query_time = time.time() - start_time
    logging.info(f'Query completed in {query_time:.2f} seconds.')

    # Filter out query files from the nearest neighbors
    playlist_filenames_without_ext = [os.path.splitext(os.path.basename(file))[0] for file in playlist_files]
    nearest_neighbors = [filenames[idx] for idx in indices[0] if filenames[idx] not in playlist_filenames_without_ext]

    return nearest_neighbors
'''
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
def check_npz_file(file_path):
    try:
        data = np.load(file_path, allow_pickle=True)
        assert 'features' in data and 'songs' in data, "Missing keys in the .npz file"
        features_dict = data['features'].item()
        song_list = data['songs'].tolist()
        assert isinstance(features_dict, dict), "Features should be a dictionary"
        assert isinstance(song_list, list), "Songs should be a list"
        logging.info("The .npz file is valid and contains the expected data.")
        return True
    except Exception as e:
        logging.error(f"Error in the .npz file: {e}")
        return False

if __name__ == "__main__":
    print(check_npz_file('audio_features.npz'))
    # Replace with actual playlist files you want to query
    playlist_files = [
        'Problem - Ariana Grande',
        'Love on Top - Beyoncé',
        'Heart Attack - Demi Lovato',
    ]

    recommendations = give_recommendations(playlist_files)
    print("Recommended songs:", recommendations)
