from pathlib import Path
from uuid import uuid4

from fastapi import Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from .auth import has_admin_access
from .classes import WorkCreateSchema
from .database import create_work_db
from .exceptions import WorkCreateError


def serve_protected_admin_page(request: Request, file_name: str, fallback_heading: str, frontend_html_dir: Path):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    html_path = frontend_html_dir / file_name
    if html_path.exists():
        return FileResponse(html_path)

    return HTMLResponse(f"<h1>{fallback_heading}</h1>")


def create_work_image_name(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    safe_suffix = suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"
    return f"{uuid4().hex}{safe_suffix}"


def get_work_create_data(
    section_name: str = Form(...),
    title: str = Form(...),
    caption: str = Form(...),
    description: str = Form(...),
) -> WorkCreateSchema:
    return WorkCreateSchema(
        section_name=section_name.strip(),
        title=title.strip(),
        caption=caption.strip(),
        description=description.strip(),
    )


async def create_work_handler(data: WorkCreateSchema, image: UploadFile, works_assets_dir: Path) -> int:
    if not image.filename:
        raise HTTPException(status_code=400, detail="image_required")

    image_name = create_work_image_name(image.filename)
    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="image_required")

    works_assets_dir.mkdir(parents=True, exist_ok=True)
    image_path = works_assets_dir / image_name

    try:
        image_path.write_bytes(image_bytes)
        persisted_work = WorkCreateSchema(
            section_name=data.section_name,
            title=data.title,
            caption=data.caption,
            description=data.description,
            img_name=image_name,
        )
        return await create_work_db(persisted_work)
    except WorkCreateError:
        if image_path.exists():
            image_path.unlink()
        raise
    except OSError as error:
        if image_path.exists():
            image_path.unlink()
        raise WorkCreateError from error
