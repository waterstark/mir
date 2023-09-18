from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    TEST_DB_HOST: str
    DB_PORT: str
    TEST_DB_PORT: str
    DB_NAME: str
    TEST_DB_NAME: str
    DB_USER: str
    TEST_DB_USER: str
    DB_PASS: str
    TEST_DB_PASS: str
    SECRET_KEY: str

    @property
    def db_url(self) -> str:
        """Product db url."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def test_db_url(self) -> str:
        """Product db url."""
        return (
            f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@"
            f"{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
