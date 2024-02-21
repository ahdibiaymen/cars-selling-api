from decouple import config


class Settings:
    DB_URL = config('DB_URL', cast=str)
    DB_NAME = config('DB_NAME', cast=str)
    COLLECTION_NAME = config('COLLECTION_NAME', cast=str)
    PAGE_LIMIT = 25
    CORS_ORIGINS = ['*']
