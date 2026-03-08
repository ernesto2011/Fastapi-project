import os


class settings():
    JWT_SECRET = os.getenv("SECRET_KEY", "12334R332WE$%15^&@")
    JWT_ALGORITM="HS256"
    ACCESS_TOKEN_EXPIRES_IN = int(
        os.getenv("ACCESS_TOKEN_EXPIRES_IN", "30")
    )