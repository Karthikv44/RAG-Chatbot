"""
Payload encryption/decryption middleware using Fernet symmetric encryption.
Encrypts response body and decrypts request body for sensitive endpoints.
Can be toggled via APP_ENV.
"""
import base64
from cryptography.fernet import Fernet
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from Src.Config.config import get_settings

settings = get_settings()

# Derive a Fernet key from JWT secret (32 url-safe base64 bytes)
_raw = settings.jwt_secret_key.encode().ljust(32)[:32]
FERNET_KEY = base64.urlsafe_b64encode(_raw)
_fernet = Fernet(FERNET_KEY)


class EncryptionMiddleware(BaseHTTPMiddleware):
    """Only active when APP_ENV != local."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if settings.app_env == "local":
            return await call_next(request)

        # Decrypt incoming body
        body = await request.body()
        if body:
            try:
                body = _fernet.decrypt(body)
            except Exception:
                return Response(content="Invalid encrypted payload", status_code=400)

        async def receive():
            return {"type": "http.request", "body": body}

        request = Request(request.scope, receive)
        response = await call_next(request)

        # Encrypt outgoing body
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        encrypted = _fernet.encrypt(resp_body)
        return Response(
            content=encrypted,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type="application/octet-stream",
        )
