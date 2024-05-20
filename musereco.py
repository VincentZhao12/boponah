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

def save_features(features, file_path):
    np.save(file_path, features)
    logging.info(f'Features saved to {file_path}')

def load_features(file_path):
    features = np.load(file_path)
    logging.info(f'Features loaded from {file_path}')
    return features

def aggregate_features_pca(features_list, pca):
    return pca.transform(features_list).mean(axis=0)

def main():
    folder_path = 'songs'
    features_file = 'audio_features.npy'
    list_of_audio_files = list_files_in_folder(folder_path)
    
    if os.path.exists(features_file):
        logging.info('Loading features from file...')
        X = load_features(features_file)
    else:
        logging.info('Extracting features from files...')
        list_of_audio_files = list_files_in_folder(folder_path)
        logging.info(f'Found {len(list_of_audio_files)} files.')

        start_time = time.time()
        X = []
        total_files = len(list_of_audio_files)
        for i, file in enumerate(list_of_audio_files):
            file_start_time = time.time()
            logging.info(f'Processing file {i + 1}/{total_files}: {file}')
            features = extract_audio_features(file)
            X.append(features)
            file_time = time.time() - file_start_time
            elapsed_time = time.time() - start_time
            remaining_files = total_files - (i + 1)
            estimated_total_time = (elapsed_time / (i + 1)) * total_files
            estimated_remaining_time = estimated_total_time - elapsed_time
            logging.info(f'Added features for file {file}. Time taken: {file_time:.2f} seconds.')
            logging.info(f'Elapsed time: {elapsed_time:.2f} seconds. Estimated remaining time: {estimated_remaining_time:.2f} seconds.')

        X = np.array(X)
        feature_extraction_time = time.time() - start_time
        logging.info(f'Feature extraction completed in {feature_extraction_time:.2f} seconds.')
        
        save_features(X, features_file)
    
    # Standardize features before PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Apply PCA
    pca = PCA(n_components=20)  # Adjust n_components as needed
    X_pca = pca.fit_transform(X_scaled)

    playlist_files = [
        'songs/Problem - Ariana Grande.mp3',
        'songs/Love on Top - Beyoncé.mp3',
        'songs/Heart Attack - Demi Lovato.mp3',
    ]

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
    nearest_neighbors = [list_of_audio_files[idx] for idx in indices[0] if list_of_audio_files[idx] not in playlist_files]

    # Output the indices of the nearest neighbors
    logging.info(f'Nearest neighbors: ')
    for neighbor in nearest_neighbors:
        logging.info(f'Nearest neighbor: {neighbor}')

if __name__ == "__main__":
    main()
