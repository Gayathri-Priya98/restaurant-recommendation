import torch
from torch_geometric.data import Data
import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from recomm_system.load_data import load_datasets
from recomm_system.hybrid_recommender import hybrid_recommend

def get_recommendations(user_id, lat, lng, query):
    from recomm_system.hybrid_recommender import hybrid_recommend
    recommendations = hybrid_recommend(user_id, lat, lng, query)
    return recommendations

def recommend_restaurants(user_id, business_df, review_df, top_n=5):
    """
    Hybrid Recommendation System using:
    - GNN-based recommendations
    - Collaborative Filtering (User-User)
    - Content-Based Filtering

    Args:
        user_id (str): The ID of the user to generate recommendations for.
        business_df (DataFrame): Business dataset.
        review_df (DataFrame): Reviews dataset.
        top_n (int): Number of top recommendations.

    Returns:
        DataFrame: Top recommended restaurants.
    """
    # ✅ Hybrid Recommendation using GNN
    gnn_recommendations = hybrid_recommend(user_id, business_df, review_df)

    # ✅ Collaborative Filtering (User Similarity)
    user_business_matrix = review_df.pivot(index="user_id", columns="business_id", values="stars").fillna(0)
    
    if user_id not in user_business_matrix.index:
        return gnn_recommendations  # If new user, return GNN-based recommendations
    
    user_vector = user_business_matrix.loc[user_id].values.reshape(1, -1)
    similarities = cosine_similarity(user_vector, user_business_matrix)
    similar_users = np.argsort(similarities[0])[-10:][::-1]
    
    recommended_businesses = set()
    for sim_user in similar_users:
        user_reviews = user_business_matrix.iloc[sim_user].nonzero()[0]
        recommended_businesses.update(user_reviews)
    
    # ✅ Content-Based Filtering (Top Rated Restaurants)
    recommended_businesses = list(recommended_businesses)
    content_based_recommendations = business_df.sort_values(by="stars", ascending=False).head(top_n)

    # ✅ Merge All Recommendations
    final_recommendations = pd.concat([gnn_recommendations, content_based_recommendations]).drop_duplicates().head(top_n)

    print(f"✅ Hybrid Recommendations for User {user_id} Generated!")
    return final_recommendations

# ✅ Load Dataset
dataset_path = "E:/my_projects/final_dataset_updated.csv"

if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"❌ Dataset file not found: {dataset_path}")

df = pd.read_csv(dataset_path).dropna(subset=['user_id', 'business_id', 'average_stars', 'business_stars'])

# ✅ Graph Data Preparation (GNN)
user_ids = {user: idx for idx, user in enumerate(df['user_id'].unique())}
restaurant_ids = {rest: idx + len(user_ids) for idx, rest in enumerate(df['business_id'].unique())}

user_idx_list = df['user_id'].map(user_ids).to_numpy()
rest_idx_list = df['business_id'].map(restaurant_ids).to_numpy()
edges = np.vstack([user_idx_list, rest_idx_list])
edge_index = torch.tensor(edges, dtype=torch.long)

df['user_avg'] = df.groupby('user_id')['average_stars'].transform('mean')
df['restaurant_avg'] = df.groupby('business_id')['business_stars'].transform('mean')

user_features = torch.tensor(df.drop_duplicates('user_id')['user_avg'].to_numpy().reshape(-1, 1), dtype=torch.float32)
restaurant_features = torch.tensor(df.drop_duplicates('business_id')['restaurant_avg'].to_numpy().reshape(-1, 1), dtype=torch.float32)
x = torch.cat((user_features, restaurant_features), dim=0)

data = Data(x=x, edge_index=edge_index)
print("✅ Graph Data Successfully Created!")
print(data)

# ✅ Testing Hybrid Recommendation System
if __name__ == "__main__":
    from load_data import load_datasets
    business_df, review_df, user_df = load_datasets()
    
    user_id = user_df.iloc[0]["user_id"]  # First user in dataset
    recommendations = recommend_restaurants(user_id, business_df, review_df, top_n=5)

    print(f"🔹 Top 5 Recommendations for User {user_id}:\n", recommendations)
