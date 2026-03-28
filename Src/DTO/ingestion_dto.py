from pydantic import BaseModel


class IngestionResponse(BaseModel):
    message: str
    chunks_stored: int
    document_name: str
