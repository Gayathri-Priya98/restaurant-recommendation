from recomm_system.gnn_model import GNNRecommender, create_graph
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import torch
import folium

def hybrid_recommend(user_id, business_df, review_df, user_df, model, graph_data):
    model.eval()
    """
    Hybrid recommendation combining GNN, content-based & popularity-based approaches.
    """
    if review_df is None or review_df.empty:
        print("❌ review_df is empty or not loaded!")
        return None
    
    user_ids = list(user_df['user_id'].unique())
    if user_id not in user_ids:
        print(f"❌ User {user_id} not found in dataset!")
        return None
    
    user_idx = user_ids.index(user_id)
    
    with torch.no_grad():
        user_embedding = model(graph_data.x, graph_data.edge_index)[user_idx].numpy().reshape(1, -1)
        print("✅ User Embedding Generated:", user_embedding.shape)
    
      # Get all embeddings from the GNN
    all_embeddings = model(graph_data.x, graph_data.edge_index)

    # Get business node embeddings (business nodes come after user nodes in the graph)
    offset = len(user_df)
    business_embeddings = all_embeddings[offset:].detach().numpy()

    # Compute cosine similarity between user and all businesses
    similarities = cosine_similarity(user_embedding, business_embeddings)

    top_indices = similarities.argsort()[0][-10:][::-1]
    content_based_recommendations = business_df.iloc[top_indices]

    popular_businesses = business_df.sort_values(by=["stars", "business_review_count"], ascending=[False, False]).head(10)
    hybrid_recommendations = pd.concat([content_based_recommendations, popular_businesses]).drop_duplicates().head(5)

    if "business_id" not in hybrid_recommendations.columns:
        print("❌ 'business_id' column missing in hybrid_recommendations!")
        return None
    recommended_df = business_df[business_df["business_id"].isin(hybrid_recommendations["business_id"])]
    recommended_df = recommended_df[["business_id", "name", "latitude", "longitude"]]
    recommended_df["name"] = recommended_df["name"].replace(0, "Unknown").fillna("Unknown")
    print("✅ Final Recommendations with Names:")
    print(recommended_df)
    
    if not recommended_df.empty:
        if "latitude" not in business_df.columns or "longitude" not in business_df.columns:
           print("❌ 'latitude' or 'longitude' columns not found in business_df!")
           return None
        valid_locations = recommended_df.dropna(subset=["latitude", "longitude"])
        valid_locations = valid_locations[(valid_locations["latitude"] != 0.0) & (valid_locations["longitude"] != 0.0)]
        if not valid_locations.empty:
            map_center = [valid_locations["latitude"].mean(), valid_locations["longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=12)

            for _, row in valid_locations.iterrows():
                lat, lon, name = row["latitude"], row["longitude"], row["name"]
                folium.Marker(
                    location=[lat, lon],
                    popup=name,
                    tooltip=name,
                    icon=folium.Icon(color="blue", icon="cutlery", prefix="fa")
                ).add_to(m)

            map_path = "recommended_restaurants_map.html"
            m.save(map_path)
            print(f"✅ Map Saved as {map_path}")
        else:
            print("❌ No valid restaurant locations found!")
    else:
        print("❌ No recommendations found!")

    return hybrid_recommendations

if __name__ == "__main__":
    from load_data import load_datasets

    business_df, review_df, user_df = load_datasets()
    graph_data = create_graph(business_df, review_df, user_df)

    input_dim = graph_data.x.shape[1]
    model = GNNRecommender(input_dim, hidden_dim=16, output_dim=16)
    model.load_state_dict(torch.load("E:/my_projects/web/gnn_recommender.pth"), strict=False)
 
    user_id = "oyogae7okpv6sygzt5g77q"
    recommendations = hybrid_recommend(user_id, business_df, review_df, user_df, model, graph_data)
    print(recommendations)
