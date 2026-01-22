# AI Detection API v2.0 Enhanced
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .aware_analyzer import analyze_document
from .parsers import parse_document_bytes, parse_text_content


app = FastAPI(title="AWARE AI Content Detection")

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@app.get("/")
def index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    return JSONResponse({"error": "Frontend not found."}, status_code=404)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    original_file: Optional[UploadFile] = File(None),
):
    if file is not None:
        data = await file.read()
        if len(data) > MAX_UPLOAD_BYTES:
            return JSONResponse({"error": "File exceeds 10 MB limit."}, status_code=400)
        doc_data = parse_document_bytes(data, file.filename or "upload")
    elif text:
        doc_data = parse_text_content(text, "pasted.txt")
    else:
        return JSONResponse({"error": "No input provided."}, status_code=400)

    original_doc = None
    if original_file is not None:
        original_data = await original_file.read()
        if len(original_data) > MAX_UPLOAD_BYTES:
            return JSONResponse({"error": "Original file exceeds 10 MB limit."}, status_code=400)
        original_doc = parse_document_bytes(original_data, original_file.filename or "original")

    result = analyze_document(doc_data, original_doc)
    return JSONResponse(result)
