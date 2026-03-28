from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Src.Database.database import get_db
from Src.Service.chat_service import ChatService
from Src.Middleware.auth_middleware import get_current_user_id
from Src.DTO.chat_dto import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from Src.Error_Codes.exceptions import AppException

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ChatService(db).chat(
            question=payload.question,
            user_id=user_id,
            conversation_id=payload.conversation_id,
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.error_code, "message": e.message})


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    convs = await ChatService(db).list_conversations(user_id)
    return [
        ConversationResponse(id=c.id, title=c.title, created_at=c.created_at.isoformat())
        for c in convs
    ]


@router.get("/conversations/{conversation_id}", response_model=list[MessageResponse])
async def get_conversation_history(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        conv = await ChatService(db).get_history(conversation_id, user_id)
        return [
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=m.sources,
                created_at=m.created_at.isoformat(),
            )
            for m in conv.messages
        ]
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.error_code, "message": e.message})
