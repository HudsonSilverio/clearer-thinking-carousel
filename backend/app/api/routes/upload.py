import os
import uuid
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/upload", tags=["upload"])

_ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

UPLOAD_DIR = Path(os.getenv("GENERATED_DIR", str(Path(__file__).resolve().parents[5] / "generated_carousels"))) / "uploads"


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    ct = (file.content_type or "").split(";")[0].strip()
    if ct not in _ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ct!r}")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    raw_name = file.filename or "upload"
    ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = UPLOAD_DIR / filename
    dest.write_bytes(await file.read())

    return {
        "url": f"/generated_carousels/uploads/{filename}",
        "path": str(dest),
    }
