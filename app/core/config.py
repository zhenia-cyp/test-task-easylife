from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    This class defines the application settings
    and loads them from the environment"""
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    ALGORITHM: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    TOKEN_KEY: str


    @property
    def DATABASE_URL(self) -> str:
        """returns the database connection URL using the defined postgresql settings"""
        return "postgresql+asyncpg://" \
               f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" \
               f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/" \
               f"{self.POSTGRES_DB}"


    class Config:
        """this class defines environment file settings"""
        # pylint: disable=R0903
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
