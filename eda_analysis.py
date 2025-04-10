import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from itertools import chain

# Load dataset
df = pd.read_csv("E:\\my_projects\\yelp_dataset\\final_dataset.csv")

# Handle Missing Values
df['name'] = df['name'].fillna("Unknown")

columns_to_fill = ['business_stars', 'business_review_count', 'latitude', 'longitude', 'user_review_count']
for col in columns_to_fill:
    df[col] = df[col].fillna(df[col].mean())

df['categories'] = df['categories'].fillna('Unknown')

# Histogram for Business Ratings
plt.figure(figsize=(12, 5))
sns.histplot(df['business_stars'], bins=20, kde=True, color='blue')
plt.xlabel("Ratings")
plt.ylabel("Frequency")
plt.title("Distribution of Business Ratings")
plt.savefig("E:/my_projects/rating_distribution.png") 
plt.show()

# 1️⃣ Average Rating
avg_rating = df['business_stars'].mean()
print(f"⭐ Average Rating for all businesses: {avg_rating:.2f}")

# 2️⃣ Top 10 Categories
if 'categories' in df.columns:
    all_categories = df['categories'].dropna().str.split(', ')
    flattened_categories = list(chain.from_iterable(all_categories))
    category_counts = Counter(flattened_categories)

    category_df = pd.DataFrame(category_counts.items(), columns=['Category', 'Count'])
    category_df = category_df.sort_values(by='Count', ascending=False).head(10)

    plt.figure(figsize=(12,6))
    sns.barplot(data=category_df, x='Category', y='Count', hue='Category', legend=False, palette='magma')  
    plt.xticks(rotation=45)
    plt.xlabel("Restaurant Category")
    plt.ylabel("Count")
    plt.title("Top 10 Most Common Restaurant Categories")
    plt.savefig("E:/my_projects/top_categories.png")
    plt.show()
else:
    print("❌ Column 'categories' not found in dataset!")

# 3️⃣ Statistics & Data Types
print("\n📊 Basic statistics:")
print(df.describe())

print("\n📝 Data types:")
print(df.dtypes)

# 4️⃣ Correlation Matrix
if {'business_stars', 'business_review_count', 'user_review_count', 'latitude', 'longitude'}.issubset(df.columns):
    correlation_matrix = df[['business_stars', 'business_review_count', 'user_review_count', 'latitude', 'longitude']].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=1, linecolor='black')
    plt.title("Correlation Heatmap")

    heatmap_path = "E:\\my_projects\\correlation_heatmap.png"
    plt.savefig(heatmap_path)
    print(f"✅ Correlation Heatmap saved at: {heatmap_path}")

    plt.show()

# 5️⃣ Convert 'date' column (if exists)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    print(f"🗓 Date column converted: {df['date'].dtype}")
else:
    print("❌ Column 'date' not found!")

# Save cleaned dataset
df.to_csv("E:\\my_projects\\yelp_dataset\\cleaned_dataset.csv", index=False)
print("✅ Cleaned dataset saved!")
