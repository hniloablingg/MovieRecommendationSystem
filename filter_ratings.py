import pandas as pd

users = pd.read_csv('backend/data/users.csv')
valid_user_ids = set(users['userId'])

ratings = pd.read_csv('backend/data/ratings.csv')
filtered_ratings = ratings[ratings['userId'].isin(valid_user_ids)]
filtered_ratings.to_csv('backend/data/ratings_filtered.csv', index=False)
print(f"Đã lọc xong! Số dòng còn lại: {len(filtered_ratings)}") 