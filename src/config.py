from pydantic import BaseSettings, root_validator


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_NAME: str
    DB_PASS: str
    SECRET_KEY: str

    @root_validator
    def get_database_url(cls, values: dict):  # noqa: N805
        values["DATABASE_URL"] = (
            f'postgresql+asyncpg://{values["DB_USER"]}:{values["DB_PASS"]}@'
            f'{values["DB_HOST"]}:{values["DB_PORT"]}/{values["DB_NAME"]}'
        )
        return values

    class Config:
        env_file = ".env"


settings = Settings()
