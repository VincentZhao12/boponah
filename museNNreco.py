import numpy as np
import librosa
import os
import time
from sklearn.preprocessing import StandardScaler
from keras import Model, Sequential
from keras import layers
import logging
import pickle

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_audio_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        features = {
            'mfcc': librosa.feature.mfcc(y=y, sr=sr).mean(axis=1),
            'chroma': librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1),
            'spectral_contrast': librosa.feature.spectral_contrast(y=y, sr=sr).mean(axis=1),
            'tonnetz': librosa.feature.tonnetz(y=y, sr=sr).mean(axis=1),
            'zcr': librosa.feature.zero_crossing_rate(y).mean(),
            'tempo': librosa.beat.tempo(y=y, sr=sr)[0]
        }
        return np.hstack(list(features.values()))
    except Exception as e:
        logging.error(f'Error processing {file_path}: {e}')
        return None

def load_dataset(folder_path, features_file='features.npy', files_file='files.pkl'):
    if os.path.exists(features_file) and os.path.exists(files_file):
        logging.info('Loading pre-saved dataset...')
        X = np.load(features_file)
        with open(files_file, 'rb') as f:
            files = pickle.load(f)
    else:
        X = []
        files = []
        start_time = time.time()
        for i, file_name in enumerate(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                logging.info(f'Processing file {i + 1}/{len(os.listdir(folder_path))}: {file_path}')
                file_start_time = time.time()
                features = extract_audio_features(file_path)
                if features is not None:
                    X.append(features)
                    files.append(file_path)
                file_time = time.time() - file_start_time
                elapsed_time = time.time() - start_time
                remaining_files = len(os.listdir(folder_path)) - (i + 1)
                estimated_total_time = (elapsed_time / (i + 1)) * len(os.listdir(folder_path))
                estimated_remaining_time = estimated_total_time - elapsed_time
                logging.info(f'File processed in {file_time:.2f} seconds.')
                logging.info(f'Elapsed time: {elapsed_time:.2f} seconds. Estimated remaining time: {estimated_remaining_time:.2f} seconds.')

        X = np.array(X)
        with open(files_file, 'wb') as f:
            pickle.dump(files, f)
        np.save(features_file, X)
        logging.info(f'Dataset saved to {features_file} and {files_file}')
    
    return X, files

# Load dataset
folder_path = 'songs'
logging.info(f'Loading dataset from {folder_path}')
X, files = load_dataset(folder_path)

if X.size == 0:
    logging.error('No audio files were processed. Please check the folder path and file formats.')
    raise ValueError('No audio files were processed. Please check the folder path and file formats.')

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Define the autoencoder model
input_dim = X_scaled.shape[1]
encoding_dim = 32  # You can adjust the dimension of the latent space

input_layer = layers.Input(shape=(input_dim,))
encoded = layers.Dense(128, activation='relu')(input_layer)
encoded = layers.Dropout(0.5)(encoded)
encoded = layers.Dense(64, activation='relu')(encoded)
encoded = layers.Dropout(0.5)(encoded)
encoded = layers.Dense(encoding_dim, activation='relu')(encoded)

decoded = layers.Dense(64, activation='relu')(encoded)
decoded = layers.Dropout(0.5)(decoded)
decoded = layers.Dense(128, activation='relu')(decoded)
decoded = layers.Dropout(0.5)(decoded)
decoded = layers.Dense(input_dim, activation='linear')(decoded)

autoencoder = Model(input_layer, decoded)
autoencoder.compile(optimizer='adam', loss='mean_squared_error')

# Training the autoencoder model with logging
logging.info('Training the autoencoder model...')
start_time = time.time()
history = autoencoder.fit(X_scaled, X_scaled, epochs=50, batch_size=32, validation_split=0.2)
training_time = time.time() - start_time
logging.info(f'Training completed in {training_time:.2f} seconds.')

# Save the model
autoencoder.save('music_recommendation_autoencoder.h5')
logging.info('Model saved to music_recommendation_autoencoder.h5')

# Encoder model for generating latent space representations
encoder = Model(input_layer, encoded)

# Function to get music recommendations
def recommend_songs(file_path, n_recommendations=5):
    features = extract_audio_features(file_path)
    if features is None:
        return []

    features_scaled = scaler.transform([features])
    latent_vector = encoder.predict(features_scaled)

    latent_vectors = encoder.predict(X_scaled)
    distances = np.linalg.norm(latent_vectors - latent_vector, axis=1)
    
    recommendations = np.argsort(distances)[:n_recommendations]
    recommended_files = [files[idx] for idx in recommendations]
    
    return recommended_files

# Example usage
playlist_files = [
    'songs/All of Me - John Legend.mp3',
    'songs/24k Magic - Bruno Mars.mp3',
]

recommendations = recommend_songs(playlist_files[0])
logging.info('Recommended songs:')
for song in recommendations:
    logging.info(song)
