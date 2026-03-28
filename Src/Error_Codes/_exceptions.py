from enum import Enum


class ErrorCode(str, Enum):
    # Auth
    INVALID_CREDENTIALS = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002"
    UNAUTHORIZED = "AUTH_003"
    USER_ALREADY_EXISTS = "AUTH_004"

    # Ingestion
    INGESTION_FAILED = "ING_001"
    UNSUPPORTED_FILE_TYPE = "ING_002"
    DOCUMENT_NOT_FOUND = "ING_003"

    # Embedding
    EMBEDDING_FAILED = "EMB_001"

    # Chat
    CHAT_FAILED = "CHAT_001"
    CONVERSATION_NOT_FOUND = "CHAT_002"

    # Vector Store
    VECTOR_STORE_ERROR = "VEC_001"

    # General
    INTERNAL_ERROR = "GEN_001"
    VALIDATION_ERROR = "GEN_002"


class AppException(Exception):
    def __init__(self, error_code: ErrorCode, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthException(AppException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status_code=401)


class NotFoundException(AppException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status_code=404)


class IngestionException(AppException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status_code=422)


class EmbeddingException(AppException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status_code=500)


class VectorStoreException(AppException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status_code=500)


class ChatException(AppException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status_code=500)
