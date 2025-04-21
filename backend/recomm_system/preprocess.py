import torch
from torch_geometric.data import Data
import numpy as np

def preprocess_data(business_df, review_df, user_df):
    # Data preprocessing, merging, and cleaning
    user_df = user_df.rename(columns={
        'user_review_count': 'review_count_user'
    })

    # Add missing columns if not exist (safe default)
    for col in ['useful_user', 'funny_user', 'cool_user']:
        if col not in user_df.columns:
            print(f"⚠️ '{col}' not found in user_df. Filling with 0.")
            user_df[col] = 0

    merged_df = review_df.merge(business_df, on='business_id', how='left')
    merged_df = merged_df.merge(user_df, on='user_id', how='left')

    final_df = merged_df.dropna(subset=['business_id', 'user_id'])

    business_df = business_df.drop_duplicates(subset=["business_id"])
    review_df = final_df[['user_id', 'business_id', 'stars']].drop_duplicates()

    user_columns = ['user_id', 'review_count_user', 'useful_user', 'funny_user', 'cool_user']
    user_columns_present = [col for col in user_columns if col in final_df.columns]
    print("✅ Extracting columns:", user_columns_present)

    user_df = final_df[user_columns_present].rename(
        columns={
            'review_count_user': 'review_count',
            'useful_user': 'useful',
            'funny_user': 'funny',
            'cool_user': 'cool'
        }).drop_duplicates()

    return final_df, business_df, review_df, user_df


def create_graph_data(user_df, business_df, review_df):
    user_required_columns = ['useful', 'funny', 'cool']
    business_required_columns = ['stars']

    for col in user_required_columns:
        if col not in user_df.columns:
            print(f"⚠️ Warning: '{col}' column missing in user_df. Adding default values (0).")
            user_df[col] = 0

    for col in business_required_columns:
        if col not in business_df.columns:
            print(f"⚠️ Warning: '{col}' column missing in business_df. Adding default values (0).")
            business_df[col] = 0

    user_features = torch.tensor(user_df[user_required_columns].values, dtype=torch.float)
    business_features = torch.tensor(business_df[business_required_columns].values, dtype=torch.float)

    # Padding the feature vectors to make them uniform in size
    user_features = torch.nn.functional.pad(user_features, (0, 16 - user_features.shape[1]), "constant", 0)[:, :16]
    business_features = torch.nn.functional.pad(business_features, (0, 16 - business_features.shape[1]), "constant", 0)[:, :16]

    x = torch.cat([user_features, business_features], dim=0)

    # Mapping user and business IDs to indices
    user_id_map = {uid: i for i, uid in enumerate(user_df['user_id'])}
    business_id_map = {bid: i + len(user_df) for i, bid in enumerate(business_df['business_id'])}

    edge_list = []
    for _, row in review_df.iterrows():
        if row['user_id'] in user_id_map and row['business_id'] in business_id_map:
            u_idx = user_id_map[row['user_id']]
            b_idx = business_id_map[row['business_id']]
            edge_list.append((u_idx, b_idx))

    edge_array = np.array(edge_list, dtype=np.int64).T
    if edge_array.size == 0:
       print("❌ Edge list is empty! No user-business interactions were mapped.")
       return None
    edge_index = torch.tensor(edge_array, dtype=torch.long)
    graph_data = Data(x=x, edge_index=edge_index)

    return graph_data
