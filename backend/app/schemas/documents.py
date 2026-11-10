from pydantic import BaseModel


class DocumentPage(BaseModel):
    page_number: int
    text: str


class DocumentExtraction(BaseModel):
    filename: str
    page_count: int
    pages: list[DocumentPage]
    warnings: list[str]
