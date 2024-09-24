from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True


    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

   

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
