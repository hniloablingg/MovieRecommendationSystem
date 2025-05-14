# import os

# class Config:
#     SQLALCHEMY_DATABASE_URI = os.getenv(
#         "DATABASE_URL",
#         "postgresql://gautoi:12345678@localhost:5432/moviedb"
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
