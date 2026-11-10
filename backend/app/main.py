from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.api.documents import router as documents_router

app = FastAPI(title="KI-Dokumentenassistent", version="0.1.0")
app.include_router(documents_router)


class HealthResponse(BaseModel):
    status: Literal["ok"]


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Zeigt, ob das Backend HTTP-Anfragen beantworten kann."""
    return HealthResponse(status="ok")
