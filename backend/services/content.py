from pathlib import Path
from typing import Optional

from fastapi import Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from ..auth import has_admin_access
from ..classes import ProjectCreateSchema, ProjectImageCreateSchema, WorkCreateSchema
from ..db.repositories import create_project_db, create_work_db
from ..exceptions import ProjectCreateError, WorkCreateError
from .media import save_uploaded_image


def serve_protected_admin_page(request: Request, file_name: str, fallback_heading: str, frontend_html_dir: Path):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    html_path = frontend_html_dir / file_name
    if html_path.exists():
        return FileResponse(html_path)

    return HTMLResponse(f"<h1>{fallback_heading}</h1>")


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


def _remove_if_exists(path: Path):
    if path.exists():
        path.unlink()


async def create_work_handler(data: WorkCreateSchema, image: UploadFile, works_assets_dir: Path) -> int:
    image_path: Optional[Path] = None
    thumbnail_path: Optional[Path] = None

    try:
        image_name, image_path, thumbnail_path = await save_uploaded_image(image, works_assets_dir)
        persisted_work = WorkCreateSchema(
            section_name=data.section_name,
            title=data.title,
            caption=data.caption,
            description=data.description,
            img_name=image_name,
        )
        return await create_work_db(persisted_work)
    except WorkCreateError:
        if thumbnail_path:
            _remove_if_exists(thumbnail_path)
        if image_path:
            _remove_if_exists(image_path)
        raise
    except OSError as error:
        if thumbnail_path:
            _remove_if_exists(thumbnail_path)
        if image_path:
            _remove_if_exists(image_path)
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
    if len(gallery_images) != len(gallery_descriptions):
        raise HTTPException(status_code=400, detail="gallery_mismatch")

    saved_paths: list[Path] = []

    async def save_image(upload: UploadFile) -> str:
        image_name, image_path, thumbnail_path = await save_uploaded_image(upload, works_assets_dir)
        saved_paths.extend([image_path, thumbnail_path])
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
            _remove_if_exists(path)
        raise
    except OSError as error:
        for path in saved_paths:
            _remove_if_exists(path)
        raise ProjectCreateError from error
