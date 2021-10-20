import subprocess
import shlex
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import status, HTTPException, Header

from configs.settings import MONGO_CLIENT, DB_NAME


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


def get_secret_key():
    cmd = "openssl rand -hex 16"
    completed_process = subprocess.run(shlex.split(cmd), capture_output=True)
    return completed_process.stdout.decode(encoding='utf-8').strip('\n')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, secret_key=None):
    """Return JWT and it's secret key for decoding
    Args:
        data (dict): data to be encoded
        expires_delta (timedelta): Specify if there's limited time for token life
        secret_key (str): secret_key for encoding/decoding JWT token
    Returns:
        tuple: contains encoded_jwt, SECRET_KEY
    """
    SECRET_KEY = get_secret_key()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    if not secret_key:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt, secret_key


def is_expired(encode_jwt, SECRET_KEY):
    """Check if token is expired or not
    Args:
        encode_jwt (str): JWT token for checking
        SECRET_KEY (str): Key for decoding JWT token
    Returns:
        bool: True if not expired, False otherwise
    """
    try:
        jwt.decode(encode_jwt, SECRET_KEY, algorithms=ALGORITHM)
    except Exception:
        return True
    return False


def get_data_from_access_token(encode_jwt, SECRET_KEY):
    """Check if token is expired or not
        Args:
            encode_jwt (str): JWT token for checking
            SECRET_KEY (str): Key for decoding JWT token
        Returns:
            dict: data from access token
    """
    return jwt.decode(encode_jwt, SECRET_KEY, algorithms=ALGORITHM)


async def valid_access_token(
        Authorization: str = Header(...,
                                    description='access_token return by login'),
        s_key: str = Header(..., description='secret_key return by login'),
):
    """Check if access token valid for accessing api
    Args:
        Bearer (str): Bearer token
        s_key (str): Secret key
    Returns:
        dict: Containing keys value which relevant to security session
    Examples:
        return {
            'encode_jwt': token,
            'type': bearer,
            's_key': s_key
        }
    Raises:
        HTTPException: if token is not valid
    """
    try:
        bearer, access_token = Authorization.split(' ')
        if not is_expired(encode_jwt=access_token, SECRET_KEY=s_key):
            data = get_data_from_access_token(
                encode_jwt=access_token, SECRET_KEY=s_key)
            email = data.get('email')
            user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
                {'email': {'$eq': email}})
            for _token in user.get('tokens'):
                if _token.get('access_token') == access_token:
                    token_type = _token.get('token_type')
                    if token_type != bearer:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, detail='Token type is not valid')
                    return {
                        'encode_jwt': access_token,
                        'type': bearer,
                        's_key': s_key
                    }
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Token is not valid')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Token type is expired')
