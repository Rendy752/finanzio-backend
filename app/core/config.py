import uuid
from pydantic_settings import BaseSettings

MOCK_USER_A_ID: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Define configuration settings, pulling values from environment variables
class Settings(BaseSettings):
    # --- Database Settings ---
    DB_USER: str = "shiruraizo"
    DB_PASS: str = "palembang01"
    DB_HOST: str = "172.31.4.134"
    DB_PORT: str = "5432"
    DB_NAME: str = "finanzio_db"
    
    # Construct the DSN (Data Source Name) dynamically
    # Note: Using 'asyncpg' driver for asynchronous PostgreSQL connection
    DATABASE_URL: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # --- Redis Settings (for Caching/Sessions) ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

    # --- Security Settings ---
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- MOCK & TESTING Settings ---
    MOCK_USER_A_EMAIL: str = "authenticated@finanzio.id"
    MOCK_USER_A_PASSWORD_HASH: str = "mock_hash_for_live_mode" # Digunakan untuk seeding DB
    
    class Config:
        # Load environment variables from a .env file if available
        env_file = ".env" 

settings = Settings()
