import jwt
import bcrypt
from datetime import datetime, timedelta
from config import SECRET_KEY, TOKEN_EXPIRE_HOURS, ADMIN_USERNAME, ADMIN_PASSWORD

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(),bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    


def authenticate(username: str, password: str) -> str | None:
    if username != ADMIN_USERNAME:
        return None
    if not verify_password(password, hash_password(ADMIN_PASSWORD)):
        return None
    return create_token(username)

                             