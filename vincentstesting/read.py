import pandas as pd


df = pd.read_csv("data/df_spotify_2.csv")

df.head()


df.shape


# In[20]:


df = df.dropna()


# In[42]:


from sentence_transformers import SentenceTransformer
import torch
from pprint import pprint
from sklearn.cluster import KMeans


# In[32]:


df.shape


# In[54]:


df["genre_copy"] = df["genre"]


# In[55]:


def filmi_to_bolly(str):
    if str == "filmi":
        return "bollywood"
    return str


# In[57]:


df["genre_copy"] = df["genre_copy"].apply(filmi_to_bolly)


# In[58]:


device = torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'

embedder = SentenceTransformer(
    "paraphrase-MiniLM-L6-v2",
    device = device
)


corpus = list(df["genre_copy"])

embeddings = embedder.encode(corpus)

num_clusters = 5

clustering_model = KMeans(n_clusters=num_clusters)
clustering_model.fit(embeddings)
cluster_assignment = clustering_model.labels_

clustered_sentences = [[] for i in range(num_clusters)]
for sentence_id, cluster_id in enumerate(cluster_assignment):
    clustered_sentences[cluster_id].append(corpus[sentence_id])

for i, cluster in enumerate(clustered_sentences):
    print("Cluster ", i + 1)
    print(cluster[0])
    print("")


import matplotlib.pyplot as plt
# %matplotlib ipympl
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA

print(clustered_sentences)

pca = PCA(n_components=3)
embeddings_3d = pca.fit_transform(embeddings)

# Assuming embeddings_3d is your 3D embeddings
fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(111, projection='3d')
for i, cluster in enumerate(clustered_sentences):
    ax.scatter(embeddings_3d[cluster_assignment == i, 0], embeddings_3d[cluster_assignment == i, 1], embeddings_3d[cluster_assignment == i, 2], label=f'Cluster {clustered_sentences[i][1]}')
ax.legend()
ax.set_title('K-means Clustering Visualization (3D)')
ax.set_xlabel('Dimension 1')
ax.set_ylabel('Dimension 2')
ax.set_zlabel('Dimension 3')
plt.show()

