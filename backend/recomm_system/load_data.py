import pandas as pd
import torch
from torch_geometric.data import Data
import os

# ✅ File Path
dataset_path = r"E:\my_projects\final_dataset_updated.csv"


def load_datasets():
    if os.path.exists(dataset_path):
        print("*Loading dataset from CSV...")
        df = pd.read_csv(dataset_path)
        print("Available Columns:", df.columns.tolist())

        if 'user_id' not in df.columns:
            print("❌ Error: 'user_id' column not found!")
            return None, None, None
       
        df.rename(columns={'business_stars': 'stars'}, inplace=True)
        df.fillna(0, inplace=True)

        print("✅ Dataset Loaded Successfully!")

        # ✅ Separate Business, Review, and User DataFrames
        business_df = df[['business_id', 'name', 'categories', 'stars', 'business_review_count', 'latitude', 'longitude']].drop_duplicates()
        review_df = df[['review_id', 'business_id', 'user_id', 'review_stars', 'text']].drop_duplicates()
        user_df = df[['user_id', 'user_review_count', 'average_stars', 'user_review_group']].drop_duplicates()

                   # ✅ Debugging user_df
        print("✅ Checking user_df structure:")
        print(user_df.head())  # First 5 rows print cheyyandi
        print(f"Total Users in user_df: {len(user_df)}")

# ✅ Check if 'user_id' column is present
        if "user_id" not in user_df.columns:
          print("❌ Error: 'user_id' column missing in user_df!")

# ✅ Check if 'user_id' has any null values
        if user_df["user_id"].isnull().sum() > 0:
          print(f"❌ Error: {user_df['user_id'].isnull().sum()} missing user_id values!")

# ✅ Check unique user count
          print(f"Unique Users in user_df: {user_df['user_id'].nunique()}")

# ✅ Compare with full dataset
        full_df = pd.read_csv(dataset_path)
        print(f"Total Unique Users in CSV: {full_df['user_id'].nunique()}")

        return business_df, review_df, user_df

    else:
        print("❌ File not found:", dataset_path)
        return None, None, None  

# ✅ Load Data when Script Runs
if __name__ == "__main__":
    business_df, review_df, user_df = load_datasets()

    if business_df is not None:
        print("✅ Business Data:\n", business_df.head())
        print("✅ Review Data:\n", review_df.head())
        print("✅ User Data:\n", user_df.head())





