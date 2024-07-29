import os
import pandas as pd
import numpy as np
import json
from openai import OpenAI
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()  # Load the variables from .env

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def filter_rows_by_keywords(dataframe, keywords):
    dataframe.loc[:, 'combined_text'] = dataframe.apply(lambda row: f"{row['Code']} {row['Content']}", axis=1)
    keyword_regex = '|'.join(keywords)
    filtered_df = dataframe[dataframe['combined_text'].str.contains(keyword_regex, case=False, na=False)]
    return filtered_df

def preprocess_text(df):
    df.loc[:, 'combined_text'] = df.apply(lambda row: f"{row['Code']} {row['Content']}", axis=1)
    return df

def get_openai_embeddings(text_list, model="text-embedding-3-large"):
    embeddings = []
    for text in text_list:
        try:
            response = client.embeddings.create(input=[text], model=model)
            embeddings.append(response.data[0].embedding)
        except Exception as e:
            if "maximum context length" in str(e):
                print(f"Text too long: {text[:50]}... - using 'Code' only for embedding.")
                response = client.embeddings.create(input=[text.split(' ', 1)[0]], model=model)
                embeddings.append(response.data[0].embedding)
            else:
                print(f"Error embedding text: {text[:50]}... - Error: {e}")
                embeddings.append(np.zeros(1536))  # Assuming embedding size is 1536
    return np.array(embeddings)

def cluster_rows(embeddings, n_clusters=None):
    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        raise ValueError("Embeddings array is empty or not 2D.")
    if n_clusters:
        if len(embeddings) < n_clusters:
            raise ValueError(f"n_samples={len(embeddings)} should be >= n_clusters={n_clusters}.")
        kmeans = KMeans(n_clusters=n_clusters, init="k-means++", random_state=42)
        kmeans.fit(embeddings)
        return kmeans.labels_
    else:
        dbscan = DBSCAN(eps=0.5, min_samples=5, metric='cosine')
        dbscan.fit(embeddings)
        return dbscan.labels_

def visualize_clusters_3d(embeddings, labels):
    tsne = TSNE(n_components=3, perplexity=15, random_state=42, init="random", learning_rate=200)
    vis_dims3 = tsne.fit_transform(embeddings)

    df_vis = pd.DataFrame({
        'x': vis_dims3[:, 0],
        'y': vis_dims3[:, 1],
        'z': vis_dims3[:, 2],
        'Cluster': labels
    })

    fig = px.scatter_3d(df_vis, x='x', y='y', z='z', color='Cluster', title="Clusters visualized in 3D using t-SNE")
    fig.show()

def create_grouped_dataframe(df, labels):
    df.loc[:, 'Group'] = labels
    return df

def update_embeddings(df, stored_df, model):
    embeddings = []
    for index, row in df.iterrows():
        stored_match = stored_df[(stored_df['Code'] == row['Code']) & (stored_df['Content'] == row['Content'])]
        if not stored_match.empty:
            stored_row = stored_match.iloc[0]
            embedding = np.array(stored_row['Embedding'])
            embeddings.append(embedding)
        else:
            combined_text = row['combined_text']
            try:
                response = client.embeddings.create(input=[combined_text], model=model)
                embedding = response.data[0].embedding
            except Exception as e:
                if "maximum context length" in str(e):
                    print(f"Text too long: {combined_text[:50]}... - using 'Code' only for embedding.")
                    response = client.embeddings.create(input=[row['Code']], model=model)
                    embedding = response.data[0].embedding
                else:
                    print(f"Error for row Title: {row['Title']} Code: {row['Code']}")
                    raise e
            embeddings.append(embedding)
            new_row = pd.DataFrame([{
                'Title': row['Title'],
                'Code': row['Code'],
                'Content': row['Content'],
                'combined_text': combined_text,
                'Embedding': embedding  # Store embedding directly
            }])
            stored_df = pd.concat([stored_df, new_row], ignore_index=True)
    return np.array(embeddings), stored_df

def clustering_df(dataframe, output_path, keywords=None, n_clusters=None, update=False, model="text-embedding-3-large"):
    """
       Main function to process, embed, cluster, and visualize text data.

       Parameters:
       ----------
       dataframe : pd.DataFrame
           The input DataFrame containing at least the following columns: 'Title', 'Code', 'Content'.
       output_path : str
           The file path where the final output Excel file will be saved.
       keywords : list, optional
           A list of keywords to filter the rows in the DataFrame. If None, no filtering is applied. Default is None.
       n_clusters : int, optional
           The number of clusters to use for KMeans clustering. If None, DBSCAN will be used to determine the clusters automatically. Default is None.
       update : bool, optional
           If True, the function will update embeddings for rows that have changed since the last run and save them. If False, it will use the stored embeddings from the previous run. Default is False.
       model : str, optional
           The OpenAI model to use for generating embeddings. Default is "text-embedding-3-large".

       Returns:
       -------
       grouped_df : pd.DataFrame
           The final DataFrame containing the columns 'Title', 'Code', 'Content', and 'Group' indicating the cluster group.

       Notes:
       -----
       - The function first filters the DataFrame based on the provided keywords (if any).
       - It then preprocesses the text by combining 'Code' and 'Content' columns.
       - If `update` is True or if the storage file does not exist, it generates embeddings using the specified OpenAI model.
       - Embeddings are stored locally in 'stored_embeddings.csv' and retrieved in subsequent runs if `update` is False.
       - Clustering is performed using either KMeans (if `n_clusters` is provided) or DBSCAN (if `n_clusters` is None).
       - The function also visualizes the clusters in a 3D plot using Plotly.
       - The final output is saved as an Excel file at the specified `output_path`.

       Example Usage:
       --------------
       df = pd.read_csv('input_data.csv')
       main(dataframe=df, output_path='output.xlsx', keywords=['cyber', 'law'], n_clusters=5, update=True)

       This will filter the DataFrame for rows containing 'cyber' or 'law', update the embeddings, perform KMeans clustering with 5 clusters, visualize the clusters, and save the results to 'output.xlsx'.
       """
    storage_path = 'tored_embeddings.csv'

    if keywords:
        df = filter_rows_by_keywords(dataframe, keywords)
    else:
        df = dataframe
    df = preprocess_text(df)

    if update or not os.path.exists(storage_path):
        stored_df = pd.DataFrame(columns=['Title', 'Code', 'Content', 'combined_text', 'Embedding'])
        embeddings, stored_df = update_embeddings(df, stored_df, model)
        stored_df.to_csv(storage_path, index=False)
    else:
        stored_df = pd.read_csv(storage_path)
        stored_df['Embedding'] = stored_df['Embedding'].apply(eval)  # Convert the string representation of lists back to lists
        embeddings, stored_df = update_embeddings(df, stored_df, model)
        stored_df.to_csv(storage_path, index=False)

    if embeddings.size == 0:
        print("No embeddings generated. Exiting.")
        return

    labels = cluster_rows(embeddings, n_clusters)
    df.loc[:, 'Group'] = labels  # Ensure 'Group' column is added here using loc to avoid SettingWithCopyWarning
    grouped_df = create_grouped_dataframe(df, labels)
    grouped_df = grouped_df[['Title', 'Code', 'Content', 'Group']]  # Ensure the correct columns are included
    visualize_clusters_3d(embeddings, labels)  # Plot the clusters using Plotly
    grouped_df.to_excel(output_path, index=False)
    return grouped_df
