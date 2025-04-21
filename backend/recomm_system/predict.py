import pandas as pd
import torch
import torch.nn as nn
import sys
sys.path.append('E:\\my_projects\\backend')
from recomm_system.gnn_model import GNNRecommender

# Load Business Dataset
business_df = pd.read_csv("E:/my_projects/yelp_dataset/business.csv")

# Fix missing values
business_df = business_df.copy()
business_df['name'] = business_df['name'].fillna("Unknown")
business_df['stars'] = business_df['stars'].fillna(0)

# **Filter only Restaurants**
if 'categories' in business_df.columns:
    business_df = business_df[business_df['categories'].str.contains("Restaurant|Food", na=False, case=False)]

# Load GNN Model
model = GNNRecommender(input_dim=16, hidden_dim=16, output_dim=16)
model.load_state_dict(torch.load("E:/my_projects/backend/recomm_system/gnn_recommender.pth"), strict=False)
model.eval()

# Get recommendations (Assume `user_id` is given)
user_id = "some_user_id"

# Simulate model prediction (Replace with actual recommendation logic)
top_indices = [250, 90, 1005, 9, 30, 334, 183, 134, 327, 147]
predicted_scores = [10.49, 9.62, 9.45, 8.93, 8.90, 8.85, 8.54, 8.46, 8.31, 8.24]

# Ensure indices are valid
max_index = len(business_df) - 1
top_indices = [idx for idx in top_indices if idx <= max_index]

# Get recommended restaurants
top_restaurants = business_df.iloc[top_indices][["business_id", "name", "stars"]]

# **Filter out non-restaurants**
top_restaurants = top_restaurants[top_restaurants['name'] != "0"]

# Print Results
print("\n🔹 **Top 10 Recommended Restaurants:**")
print(top_restaurants)
