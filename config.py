import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-super-secure-change-me')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///legal_ai.db')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

