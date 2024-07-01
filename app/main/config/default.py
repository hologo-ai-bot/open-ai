import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    OPENAI_API_TOKEN = os.environ.get('OPENAI_API_TOKEN')
    ASSISTANT_ID = os.environ.get('ASSISTANT_ID')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL')
    
    #DB config
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017/openai'
    }