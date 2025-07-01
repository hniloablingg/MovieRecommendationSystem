import pandas as pd

# Đọc danh sách userId hợp lệ
users = pd.read_csv('backend/data/users.csv')
valid_user_ids = set(users['userId'])

# Đọc ratings và lọc
ratings = pd.read_csv('backend/data/ratings.csv')
filtered_ratings = ratings[ratings['userId'].isin(valid_user_ids)]

# Lưu ra file mới
filtered_ratings.to_csv('backend/data/ratings_filtered.csv', index=False)
print(f"Đã lọc xong! Số dòng còn lại: {len(filtered_ratings)}")

