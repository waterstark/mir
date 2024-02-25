from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DEBUG: bool = True

    DB_HOST: str

    DB_PORT: str

    DB_NAME: str

    DB_USER: str

    DB_PASS: str

    TEST_DB_NAME: str

    MONGO_HOST: str

    MONGO_PORT: str

    MONGO_DATABASE: str

    REDIS_HOST: str

    REDIS_PORT: int

    SECRET_KEY: str

    PRIVATE_KEY_PATH: Path = BASE_DIR / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "jwt-public.pem"
    ALGORITHM: str

    COOKIE_ACCESS_TOKEN_KEY: str
    COOKIE_REFRESH_TOKEN_KEY: str

    ACCESS_TOKEN_EXPIRES_IN: int
    REFRESH_TOKEN_EXPIRES_IN: int

    class Config:
        env_file = ".env"

    @property
    def db_url_postgresql(self) -> str:
        """Product db url."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def test_db_url_postgresql(self) -> str:
        """Test db url.
        For local testing:
         - if you have TEST_DB_NAME, tests will use this db.
        For docker testing:
         - we do not need to provide TEST_DB_NAME, so that we do not need second
        docker-compose file. Postgres container can create DB by DB_NAME env var.
        The only difference in local and docker testing is one line in env file
        (hope, you have to copies of env file).
        """
        if self.TEST_DB_NAME:
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"
            )

        return self.db_url_postgresql

    @property
    def db_url_mongo(self) -> str:
        """Product db url."""
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"

    @property
    def db_url_redis(self) -> str:
        """Product db url."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()
