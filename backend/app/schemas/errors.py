from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str = Field(examples=["http_error"])
    message: str = Field(examples=["Task not found"])
    details: list[dict] | None = Field(default=None, description="Only for validation errors")


class ErrorResponse(BaseModel):
    error: ErrorBody