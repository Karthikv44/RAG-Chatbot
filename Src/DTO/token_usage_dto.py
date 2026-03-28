from pydantic import BaseModel


class TokenUsageRecord(BaseModel):
    id: str
    model_type: str
    model_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    conversation_id: str | None
    created_at: str


class TokenUsageSummary(BaseModel):
    model_type: str
    model_id: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    call_count: int
