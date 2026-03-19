import os
from dotenv import load_dotenv

load_dotenv(".key")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(os.getcwd(), "flask_session")
    SESSION_PERMANENT = False
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}