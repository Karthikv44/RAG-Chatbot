import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Src.Database.database import get_db
from Src.Service.ingestion_service import IngestionService
from Src.Middleware.auth_middleware import get_current_user_id
from Src.DTO.ingestion_dto import IngestionResponse
from Src.Error_Codes.exceptions import IngestionException

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

UPLOAD_DIR = "data/documents"


@router.post("/", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = await IngestionService(db, user_id).ingest_file(file_path)
        return IngestionResponse(message="Ingestion successful", **result)
    except IngestionException as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.error_code, "message": e.message})
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
