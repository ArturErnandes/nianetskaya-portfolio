from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from ..image_tools import create_thumbnail

UPLOAD_CHUNK_SIZE = 1024 * 1024


def create_work_image_name(filename: Optional[str]) -> str:
    suffix = Path(filename or "").suffix.lower()
    safe_suffix = suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    return f"{uuid4().hex}{safe_suffix}"


async def write_upload_stream(upload: UploadFile, image_path: Path, chunk_size: int = UPLOAD_CHUNK_SIZE):
    bytes_written = 0

    with image_path.open("wb") as image_file:
        while True:
            chunk = await upload.read(chunk_size)
            if not chunk:
                break
            image_file.write(chunk)
            bytes_written += len(chunk)

    if bytes_written == 0:
        if image_path.exists():
            image_path.unlink()
        raise HTTPException(status_code=400, detail="image_required")


async def save_uploaded_image(upload: UploadFile, works_assets_dir: Path) -> tuple[str, Path, Path]:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="image_required")

    image_name = create_work_image_name(upload.filename)

    works_assets_dir.mkdir(parents=True, exist_ok=True)
    image_path = works_assets_dir / image_name

    await write_upload_stream(upload, image_path)
    thumbnail_path = create_thumbnail(image_path, works_assets_dir)

    return image_name, image_path, thumbnail_path
