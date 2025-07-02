import os

# Абсолютный путь к корню проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class Config:
    # Путь к SQLite-файлу /..../data/noto.db
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'noto.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
