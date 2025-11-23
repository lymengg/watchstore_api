import os

# JWT/config settings pulled from environment variables with safe defaults.
# In production, set these via environment or a .env file loaded by your process manager.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_me_access_secret")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "change_me_refresh_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
JWT_REFRESH_EXPIRE_MINUTES = int(os.getenv("JWT_REFRESH_EXPIRE_MINUTES", str(60 * 24 * 7)))  # 7 days
