import hashlib
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from typing import Optional
import logging
import hmac
from app.core.config import settings
import urllib

logger = logging.getLogger(__name__)


def verify_tg_init_data(init_data: str) -> bool:
    try:
        if not init_data or not isinstance(init_data, str):
            logger.error(f'Invalid init_data: {init_data}')
            return False

        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error('Invalid bot_token')
            return False

        decoded_data = urllib.parse.unquote(init_data)
        pars = decoded_data.split('&')
        data_dict = {}
        hash_value = None

        for pair in pars:
            if '=' not in pair:
                continue

            key, value = pair.split('=', 1)

            if key == 'hash':
                hash_value = value
            else:
                data_dict[key] = value

        if not hash_value:
            logger.error('No hash in init_data')
            return False

        sorted_keys = sorted(data_dict.keys())
        data_check_parts = []

        for key in sorted_keys:
            value = data_dict[key]
            data_check_parts.append(f'{key}={value}')

        data_check_string = '\n'.join(data_check_parts)

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.TELEGRAM_BOT_TOKEN.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        computed_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        result = hmac.compare_digest(computed_hash, hash_value)
        return result

    except Exception as e:
        logger.error(f'Error verifying init_data: {e}', exc_info=True)
        return False


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        return None
