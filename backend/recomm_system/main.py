import sys
sys.path.append("E:/my_projects/backend")

from recomm_system.load_data import load_datasets
from recomm_system.preprocess import preprocess_data, create_graph_data
from recomm_system.hybrid_recommender import hybrid_recommend

def main():
    # Load raw data
    business_df, review_df, user_df = load_datasets()

    # Preprocess data
    final_df, business_df, review_df, user_df = preprocess_data(business_df, review_df, user_df)

    # GNN graph creation (optional but for GNN-based recsys)
    graph_data = create_graph_data(user_df, business_df, review_df)
    print("Graph data created successfully!")
    print(graph_data)

    # Hybrid recommendation
    user_id = user_df['user_id'].iloc[0]  # Dummy user ID from dataset
    recommendations = hybrid_recommend(user_id, business_df, review_df)

    print("Recommended Restaurants:")
    print(recommendations[['name', 'stars']])

if __name__ == "__main__":
    main()
