from flask import Flask, request, jsonify
import requests
from recomm_system.recommendation import get_recommendations
from recomm_system.gnn_model import GNNRecommender
from flask_cors import CORS
import pandas as pd
from geopy.distance import geodesic

GEOAPIFY_API_KEY = "bb2c0822aea848d1a17483b7cb7c893e"
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

csv_path = r"E:\\my_projects\\yelp_dataset\\business.csv"
df = pd.read_csv(csv_path)
print("CSV rows:", len(df))
print(df[['name', 'categories', 'latitude', 'longitude']].head(1000))

@app.route('/')
def home():
    return "🍔 Welcome to the Restaurant Recommender API!"

@app.route('/search', methods=['GET'])
def search_restaurants():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    query = request.args.get('query', type=str)

    geo_url = f"https://api.geoapify.com/v2/places?categories=catering.restaurant&filter=circle:{lng},{lat},5000&bias=proximity:{lng},{lat}&name={query}&limit=20&apiKey={GEOAPIFY_API_KEY}"

    response = requests.get(geo_url)
    data = response.json()

    restaurants = []
    for feat in data.get("features", []):
        props = feat["properties"]
        restaurants.append({
            "name": props.get("name"),
            "latitude": feat["geometry"]["coordinates"][1],
            "longitude": feat["geometry"]["coordinates"][0],
            "distance": round(props.get("distance", 0) / 1000, 2),
        })

 
   
    print("📍 Lat:", lat, "Lng:", lng, "Query:", query)

    if lat is None or lng is None or not query:
        print("❌ Missing data")
        return jsonify({"error": "Latitude, Longitude, and Search query are required"}), 400

    nearby = []
    others = []

    for _, row in df.iterrows():
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
            name = str(row['name']).lower()
            categories = str(row.get('categories', '')).lower()

            if query.lower() in name or query.lower() in categories:
                distance = geodesic((lat, lng), (row['latitude'], row['longitude'])).km
                restaurant_info = {
                    "name": row['name'],
                    "latitude": row['latitude'],
                    "longitude": row['longitude'],
                    "stars": row['stars'],
                    "distance": round(distance, 2)
                }

                if distance <= 10:
                    nearby.append(restaurant_info)
                else:
                    others.append(restaurant_info)

    print("✅ Nearby Found:", len(nearby), "| Distant Found:", len(others))

    return jsonify({
        "nearby": nearby[:10],  # top 10 nearby
        "others": others[:10]   # top 10 distant
    })

@app.route('/recommend', methods=['GET'])
def recommend_restaurants():
    user_id = request.args.get('user_id', type=str)

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        recommendations = get_recommendations(user_id)  # GNN based function
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
