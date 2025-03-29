import os

DATABASE = {
    'dbname': 'movie-recommendation',
    'user': 'postgres',
    'password': '02112004',
    'host': 'localhost',
    'port': 5432
}

# Kết nối dưới dạng URL (cho SQLAlchemy)
DATABASE_URL = f"postgresql://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['dbname']}"

