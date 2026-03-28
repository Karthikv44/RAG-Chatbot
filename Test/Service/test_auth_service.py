import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from Src.Service.auth_service import AuthService
from Src.Error_Codes.exceptions import AuthException


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_register_success(mock_db):
    with patch("Src.Service.auth_service.UserRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.get_by_email = AsyncMock(return_value=None)
        repo.create = AsyncMock(return_value=MagicMock(id="u1", username="test", email="test@test.com"))

        service = AuthService(mock_db)
        result = await service.register("test", "test@test.com", "password123")
        assert result.email == "test@test.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(mock_db):
    with patch("Src.Service.auth_service.UserRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.get_by_email = AsyncMock(return_value=MagicMock())

        service = AuthService(mock_db)
        with pytest.raises(AuthException):
            await service.register("test", "test@test.com", "password123")


@pytest.mark.asyncio
async def test_login_invalid_credentials(mock_db):
    with patch("Src.Service.auth_service.UserRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.get_by_email = AsyncMock(return_value=None)

        service = AuthService(mock_db)
        with pytest.raises(AuthException):
            await service.login("test@test.com", "wrongpass")
