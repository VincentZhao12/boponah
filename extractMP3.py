import librosa
import numpy as np
import os

from sklearn.neighbors import NearestNeighbors
import numpy as np

list_of_audio_files = []

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



list_of_audio_files = list_files_in_folder('songs') 

# List of MP3 files
# Extract features from all files
X = np.array([extract_audio_features(file) for file in list_of_audio_files])

# Train k-NN model
knn = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
knn.fit(X)

# Example query
query_file = 'songs/Starboy - The Weeknd.mp3.mp3'
query_features = extract_audio_features(query_file)
distances, indices = knn.kneighbors([query_features])

# Output the indices of the nearest neighbors
print(indices[0])
print(indices[1])
print(indices[2])


