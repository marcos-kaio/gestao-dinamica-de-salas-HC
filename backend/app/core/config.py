from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "GDS"
    
    # Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Credenciais Admin
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Cria uma instância em cache para não ler o arquivo a cada request
@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()