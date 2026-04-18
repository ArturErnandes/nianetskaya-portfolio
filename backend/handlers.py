from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from .auth import has_admin_access
from .classes import ProjectCreateSchema, ProjectImageCreateSchema, WorkCreateSchema
from .database import create_project_db, create_work_db
from .exceptions import ProjectCreateError, WorkCreateError
from .image_tools import create_thumbnail

UPLOAD_CHUNK_SIZE = 1024 * 1024


def serve_protected_admin_page(request: Request, file_name: str, fallback_heading: str, frontend_html_dir: Path):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    html_path = frontend_html_dir / file_name
    if html_path.exists():
        return FileResponse(html_path)

    return HTMLResponse(f"<h1>{fallback_heading}</h1>")


def create_work_image_name(filename: Optional[str]) -> str:
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


async def create_work_handler(data: WorkCreateSchema, image: UploadFile, works_assets_dir: Path) -> int:
    if not image.filename:
        raise HTTPException(status_code=400, detail="image_required")

    image_name = create_work_image_name(image.filename)

    works_assets_dir.mkdir(parents=True, exist_ok=True)
    image_path = works_assets_dir / image_name
    thumbnail_path: Optional[Path] = None

    try:
        await write_upload_stream(image, image_path)
        thumbnail_path = create_thumbnail(image_path, works_assets_dir)
        persisted_work = WorkCreateSchema(
            section_name=data.section_name,
            title=data.title,
            caption=data.caption,
            description=data.description,
            img_name=image_name,
        )
        return await create_work_db(persisted_work)
    except WorkCreateError:
        if thumbnail_path and thumbnail_path.exists():
            thumbnail_path.unlink()
        if image_path.exists():
            image_path.unlink()
        raise
    except OSError as error:
        if thumbnail_path and thumbnail_path.exists():
            thumbnail_path.unlink()
        if image_path.exists():
            image_path.unlink()
        raise WorkCreateError from error


def get_project_create_data(
    section_name: str = Form(...),
    title: str = Form(...),
    caption: str = Form(...),
    description: str = Form(...),
) -> ProjectCreateSchema:
    return ProjectCreateSchema(
        section_name=section_name.strip(),
        title=title.strip(),
        caption=caption.strip(),
        description=description.strip(),
        images=[],
    )


async def create_project_handler(
    data: ProjectCreateSchema,
    cover_image: UploadFile,
    gallery_images: list[UploadFile],
    gallery_descriptions: list[str],
    works_assets_dir: Path,
) -> int:
    if not cover_image.filename:
        raise HTTPException(status_code=400, detail="cover_image_required")

    if len(gallery_images) != len(gallery_descriptions):
        raise HTTPException(status_code=400, detail="gallery_mismatch")

    saved_paths: list[Path] = []

    async def save_image(upload: UploadFile) -> str:
        if not upload.filename:
            raise HTTPException(status_code=400, detail="image_required")

        image_name = create_work_image_name(upload.filename)

        works_assets_dir.mkdir(parents=True, exist_ok=True)
        image_path = works_assets_dir / image_name
        await write_upload_stream(upload, image_path)
        saved_paths.append(image_path)
        saved_paths.append(create_thumbnail(image_path, works_assets_dir))
        return image_name

    try:
        cover_img_name = await save_image(cover_image)
        images: list[ProjectImageCreateSchema] = []

        for index, (image, description) in enumerate(zip(gallery_images, gallery_descriptions, strict=False), start=1):
            img_name = await save_image(image)
            images.append(
                ProjectImageCreateSchema(
                    img_name=img_name,
                    description=description.strip() or None,
                    order_index=index,
                ),
            )

        persisted_project = ProjectCreateSchema(
            section_name=data.section_name,
            title=data.title,
            caption=data.caption,
            description=data.description,
            cover_img_name=cover_img_name,
            images=images,
        )
        return await create_project_db(persisted_project)
    except ProjectCreateError:
        for path in saved_paths:
            if path.exists():
                path.unlink()
        raise
    except OSError as error:
        for path in saved_paths:
            if path.exists():
                path.unlink()
        raise ProjectCreateError from error
