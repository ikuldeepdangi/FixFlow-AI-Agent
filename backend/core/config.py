# core/config.py

import os

class Settings:
    APP_NAME = "FixFlow"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    DEBUG = True

settings = Settings()
