from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Src.Database.database import get_db
from Src.Service.auth_service import AuthService
from Src.DTO.auth_dto import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(email=payload.email, password=payload.password)
