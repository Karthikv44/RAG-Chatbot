"""JWT token creation and verification utilities."""
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from Src.Config.config import get_settings
from Src.Error_Codes.exceptions import AuthException, ErrorCode

settings = get_settings()


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Returns user_id from token or raises AuthException."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            raise AuthException(ErrorCode.UNAUTHORIZED, "Invalid token payload")
        return user_id
    except JWTError:
        raise AuthException(ErrorCode.TOKEN_EXPIRED, "Token expired or invalid")
