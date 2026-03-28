from sqlalchemy.ext.asyncio import AsyncSession
from Src.Repository.user_repository import UserRepository
from Src.Utilities.password_utils import hash_password, verify_password
from Src.Utilities.token_utils import create_access_token
from Src.Error_Codes.exceptions import AuthException, ErrorCode
from Src.DTO.auth_dto import UserResponse, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self._repo = UserRepository(db)

    async def register(self, username: str, email: str, password: str) -> UserResponse:
        existing = await self._repo.get_by_email(email)
        if existing:
            raise AuthException(ErrorCode.USER_ALREADY_EXISTS, "Email already registered")
        user = await self._repo.create(username, email, hash_password(password))
        return UserResponse(id=user.id, username=user.username, email=user.email)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthException(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")
        token = create_access_token(user.id)
        return TokenResponse(access_token=token)
