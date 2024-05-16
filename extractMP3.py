import librosa
import numpy as np
import os
import time
import logging
from sklearn.neighbors import NearestNeighbors

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

def main():
    folder_path = 'songs'
    
    # List of MP3 files
    logging.info('Listing files in folder...')
    list_of_audio_files = list_files_in_folder(folder_path)
    logging.info(f'Found {len(list_of_audio_files)} files.')
    
    # Extract features from all files with detailed logging and timing
    logging.info('Extracting features from files...')
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
    
    # Train k-NN model
    logging.info('Training k-NN model...')
    start_time = time.time()
    knn = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
    knn.fit(X)
    training_time = time.time() - start_time
    logging.info(f'Training completed in {training_time:.2f} seconds.')
    
    # Example query
    query_file = 'songs/Cheap Thrills - Sia.mp3'
    logging.info(f'Extracting features from query file: {query_file}...')
    query_features = extract_audio_features(query_file)
    logging.info('Finding nearest neighbors...')
    start_time = time.time()
    distances, indices = knn.kneighbors([query_features])
    query_time = time.time() - start_time
    logging.info(f'Query completed in {query_time:.2f} seconds.')
    
    # Output the indices of the nearest neighbors
    logging.info(f'Nearest neighbors indices: {indices[0]}')
    for idx in indices[0]:
        logging.info(f'Nearest neighbor: {list_of_audio_files[idx]}')

if __name__ == "__main__":
    main()
