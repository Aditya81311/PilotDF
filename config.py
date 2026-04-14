import os
from dotenv import load_dotenv

load_dotenv(".key")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

    SQLALCHEMY_DATABASE_URI = os.getenv("SUPABASE_DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = False  # we'll handle expiry later