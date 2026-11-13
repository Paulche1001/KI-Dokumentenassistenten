from pydantic import BaseModel
from app.schemas.chunks import DocumentChunk


class DocumentPage(BaseModel):
    page_number: int
    text: str


class DocumentExtraction(BaseModel):
    filename: str
    page_count: int
    pages: list[DocumentPage]
    warnings: list[str]
    chunks: list[DocumentChunk]