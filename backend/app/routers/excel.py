import logging
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.excel import excel_service
from app.excel.excel_service import ExcelServiceError
from app.models import SessionResponse, UpdateExcelRequest

logger = logging.getLogger("excel_router")
router = APIRouter(prefix="/api/excel", tags=["excel"])

ALLOWED_EXTENSIONS = {".xlsx"}


@router.post("/new", response_model=SessionResponse)
def new_session() -> SessionResponse:
    session_id = excel_service.create_session()
    return SessionResponse(session_id=session_id, rows=[])


@router.post("/upload", response_model=SessionResponse)
async def upload_excel(file: UploadFile = File(...)) -> SessionResponse:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        session_id = excel_service.create_session(upload_path=tmp_path)
        rows = excel_service.get_rows(session_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Could not read workbook: {exc}") from exc
    finally:
        os.remove(tmp_path)

    return SessionResponse(session_id=session_id, rows=rows)


@router.get("/{session_id}/rows", response_model=SessionResponse)
def get_rows(session_id: str) -> SessionResponse:
    try:
        rows = excel_service.get_rows(session_id)
    except ExcelServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SessionResponse(session_id=session_id, rows=rows)


@router.post("/update", response_model=SessionResponse)
def update_excel(request: UpdateExcelRequest) -> SessionResponse:
    try:
        rows = excel_service.upsert_product(request.session_id, request.product)
    except ExcelServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SessionResponse(session_id=request.session_id, rows=rows)


@router.get("/{session_id}/download")
def download_excel(session_id: str):
    try:
        path = excel_service.get_file_path(session_id)
    except ExcelServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="bbw_price_tracker.xlsx",
    )
