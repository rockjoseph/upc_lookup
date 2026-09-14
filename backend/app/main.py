import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import SESSION_TTL_SECONDS
from app.excel.excel_service import cleanup_expired_sessions
from app.routers import excel, product, batch_lookup

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="BBW Price Tracker API",
    description="Look up Bath & Body Works product prices and sync them to an Excel workbook.",
    version="1.0.0",
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product.router)
app.include_router(excel.router)
app.include_router(batch_lookup.router)


@app.on_event("startup")
def startup() -> None:
    removed = cleanup_expired_sessions(SESSION_TTL_SECONDS)
    if removed:
        logging.getLogger("startup").info("Cleaned up %s expired session workbook(s)", removed)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
