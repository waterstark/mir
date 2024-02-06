from datetime import datetime, timedelta

import bcrypt
import jwt

from src.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.PRIVATE_KEY_PATH.read_text(),  # noqa: B008
    algorithm: str = settings.ALGORITHM,
    expire_minutes: int = settings.ACCESS_TOKEN_EXPIRES_IN,
) -> str:
    """Кодировка данных в JWT токен."""
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
    )
    return jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.PUBLIC_KEY_PATH.read_text(),  #noqa: B008
    algorithm: str = settings.ALGORITHM,
) -> dict:
    """Декодировка JWT токена в данные."""
    return jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )


def hash_password(
    password: str,
) -> bytes:
    """Хеширование пароля."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password=password.encode(),
        salt=salt,
    )


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """Проверка на совпадение хэшированного и нехэшированного пароля."""
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
