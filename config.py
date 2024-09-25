from decouple import config 

class Config:
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = config('SQLALCHEMY_TRACK_MODIFICATIONS', cast = bool)
    

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_DATABASE_URI')
    # DEBUG = True
    DB_USERNAME= config('DB_USERNAME')
    DB_PASSWORD= config('DB_PASSWORD')
    DB_HOST= config('DB_HOST')
    DB_PORT=3306
    DB_NAME= config('DB_NAME')
    SQLALCHEMY_ECHO = False 
    CONSUMER_KEY = config('CONSUMER_KEY')
    CONSUMER_SECRET = config('CONSUMER_SECRET')
    PASSKEY = config('PASSKEY')
    CALLBACK_URL = config('CALLBACK_ENDPOINT')


class ProdConfig(Config):
    pass

class TestConfig(Config):
    pass