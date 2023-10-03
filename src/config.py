from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str

    DB_PORT: str

    DB_NAME: str

    DB_USER: str

    DB_PASS: str

    MONGO_HOST: str

    MONGO_PORT: str

    MONGO_DATABASE: str

    SECRET_KEY: str

    @property
    def db_url_postgresql(self) -> str:
        """Product db url."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def db_url_mongo(self) -> str:
        """Product db url."""
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"


class Config:
    env_file = ".env"


settings = Settings()
