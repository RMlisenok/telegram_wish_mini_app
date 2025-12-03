from jose import JWTError, jwt
from datetime import datetime
from typing import Optional
import hashlib
import hmac

from app.core.config import settings


def verify_tg_init_data(init_data: str) -> bool:
    try:
        pars = init_data.split('&')
        data_dict = {}
        hash_value = None

        for pair in pars:
            key, value = pair.split('=')
            if key == 'hash':
                hash_value = value
            else:
                data_dict[key] = value

        if not hash_value:
            return False

        data_check = '\n'.join(
            f'{key}={data_dict[key]}'
            for key in sorted(data_dict.keys())
        )

        secret_key = hmac.new(
            key=settings.TELEGRAM_BOT_TOKEN,
            msg=b"WebAppData",
            digestmod=hashlib.sha256
        ).hexdigest()

        computed_hash = hmac.new(
            key=secret_key,
            msg=data_check.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return secret_key == computed_hash
    except Exception as e:
        print(f'Error: {e}')
        return False


def create_jwt_token(data: dict):
    to_encore = data.copy()

    expire = datetime.utcnow() + settings.ACCESS_TOKEN_EXPIRE_MINUTES

    to_encore.update({'exp': expire})

    encoder_jwt = jwt.encode(
        to_encore,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoder_jwt


def verify_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=settings.ALGORITHM
        )
        return payload
    except JWTError:
        return None
