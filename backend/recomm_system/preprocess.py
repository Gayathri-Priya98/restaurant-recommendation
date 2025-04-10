import torch
from torch_geometric.data import Data
import numpy as np
import pandas as pd

def preprocess_data(business_df, review_df, user_df):
    # Merge review with business and user
    merged_df = review_df.merge(business_df, on='business_id', how='left')
    merged_df = merged_df.merge(user_df, on='user_id', how='left')

    # Drop missing essential values
    final_df = merged_df.dropna(subset=['business_id', 'user_id'])

    # Create filtered versions of individual dataframes for GNN
    business_df = final_df[['business_id', 'name', 'stars']].drop_duplicates()
    review_df = final_df[['user_id', 'business_id', 'stars']].drop_duplicates()
    # User dataframe – corrected columns
    user_df = final_df[['user_id', 'review_count_user', 'useful_user', 'funny_user', 'cool_user']].rename(
    columns={
        'review_count_user': 'review_count',
        'useful_user': 'useful',
        'funny_user': 'funny',
        'cool_user': 'cool'
    }).drop_duplicates()

    return final_df, business_df, review_df, user_df


def create_graph_data(user_df, business_df, review_df):
    # Required columns
    user_required_columns = ['useful', 'funny', 'cool']
    business_required_columns = ['stars']

    # Add missing columns with default 0
    for col in user_required_columns:
        if col not in user_df.columns:
            print(f"⚠️ Warning: '{col}' column missing in user_df. Adding default values (0).")
            user_df[col] = 0

    for col in business_required_columns:
        if col not in business_df.columns:
            print(f"⚠️ Warning: '{col}' column missing in business_df. Adding default values (0).")
            business_df[col] = 0

    # Convert features to tensors
    user_features = torch.tensor(user_df[user_required_columns].values, dtype=torch.float)
    business_features = torch.tensor(business_df[business_required_columns].values, dtype=torch.float)

    # Pad to 16 dimensions
    user_features = torch.nn.functional.pad(user_features, (0, 16 - user_features.shape[1]), "constant", 0)[:, :16]
    business_features = torch.nn.functional.pad(business_features, (0, 16 - business_features.shape[1]), "constant", 0)[:, :16]

    # Combine user and business features
    x = torch.cat([user_features, business_features], dim=0)

    # Build edge index
    user_id_map = {uid: i for i, uid in enumerate(user_df['user_id'])}
    business_id_map = {bid: i + len(user_df) for i, bid in enumerate(business_df['business_id'])}

    edge_list = []
    for _, row in review_df.iterrows():
        if row['user_id'] in user_id_map and row['business_id'] in business_id_map:
            u_idx = user_id_map[row['user_id']]
            b_idx = business_id_map[row['business_id']]
            edge_list.append((u_idx, b_idx))

    edge_array = np.array(edge_list, dtype=np.int64).T
    edge_index = torch.tensor(edge_array, dtype=torch.long)

    # Create PyG Data object
    graph_data = Data(x=x, edge_index=edge_index)

    return graph_data
