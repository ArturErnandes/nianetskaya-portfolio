from pathlib import Path
from typing import Optional

from fastapi import Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from ..auth import has_admin_access
from ..db.project_repositories import (
    create_project_db,
    create_project_image_db,
    delete_project_image_db,
    update_project_db,
    update_project_image_db,
)
from ..db.work_repositories import create_work_db, update_work_db
from ..exceptions import (
    ProjectCreateError,
    ProjectImageDeleteError,
    ProjectImageUpdateError,
    ProjectUpdateError,
    WorkCreateError,
    WorkNotFoundError,
    WorkUpdateError,
)
from ..image_tools import get_thumbnail_path
from ..schemas.content import (
    ProjectCreateSchema,
    ProjectImageCreateSchema,
    ProjectImageUpdateSchema,
    ProjectUpdateSchema,
    WorkCreateSchema,
    WorkUpdateSchema,
)
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


def get_work_update_data(
    section_name: str = Form(...),
    title: str = Form(...),
    caption: str = Form(...),
    description: str = Form(...),
) -> WorkUpdateSchema:
    return WorkUpdateSchema(
        section_name=section_name.strip(),
        title=title.strip(),
        caption=caption.strip(),
        description=description.strip(),
    )


def _remove_if_exists(path: Path):
    if path.exists():
        path.unlink()


def _has_upload_file(upload: UploadFile | None) -> bool:
    return upload is not None and bool(upload.filename)


def _remove_media_files(image_name: str | None, works_assets_dir: Path):
    if image_name is None:
        return

    image_path = works_assets_dir / image_name
    thumbnail_path = get_thumbnail_path(image_path, works_assets_dir)

    _remove_if_exists(thumbnail_path)
    _remove_if_exists(image_path)


async def _save_optional_uploaded_image(upload: UploadFile | None, works_assets_dir: Path) -> tuple[str | None, Path | None, Path | None]:
    if not _has_upload_file(upload):
        return None, None, None

    try:
        return await save_uploaded_image(upload, works_assets_dir)
    except HTTPException as error:
        if error.detail == "image_required":
            return None, None, None
        raise


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


async def update_work_handler(
    work_id: int,
    data: WorkUpdateSchema,
    image: UploadFile | None,
    works_assets_dir: Path,
) -> None:
    image_path: Optional[Path] = None
    thumbnail_path: Optional[Path] = None
    image_name: Optional[str] = None
    old_image_name: Optional[str] = None

    try:
        image_name, image_path, thumbnail_path = await _save_optional_uploaded_image(image, works_assets_dir)

        persisted_work = WorkUpdateSchema(
            section_name=data.section_name,
            title=data.title,
            caption=data.caption,
            description=data.description,
            img_name=image_name,
        )
        old_image_name = await update_work_db(work_id, persisted_work)
    except (WorkUpdateError, WorkNotFoundError):
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
        raise WorkUpdateError from error

    try:
        _remove_media_files(old_image_name, works_assets_dir)
    except OSError as error:
        raise WorkUpdateError from error


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


def get_project_update_data(
    section_name: str = Form(...),
    title: str = Form(...),
    caption: str = Form(...),
    description: str = Form(...),
) -> ProjectUpdateSchema:
    return ProjectUpdateSchema(
        section_name=section_name.strip(),
        title=title.strip(),
        caption=caption.strip(),
        description=description.strip(),
    )


def get_project_image_update_data(
    description: str | None = Form(None),
    order_index: int = Form(...),
) -> ProjectImageUpdateSchema:
    return ProjectImageUpdateSchema(
        description=description.strip() or None if description is not None else None,
        order_index=order_index,
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


async def update_project_handler(
    project_id: int,
    data: ProjectUpdateSchema,
    cover_image: UploadFile | None,
    works_assets_dir: Path,
) -> None:
    image_path: Optional[Path] = None
    thumbnail_path: Optional[Path] = None
    cover_img_name: Optional[str] = None
    old_cover_img_name: Optional[str] = None

    try:
        cover_img_name, image_path, thumbnail_path = await _save_optional_uploaded_image(cover_image, works_assets_dir)

        persisted_project = ProjectUpdateSchema(
            section_name=data.section_name,
            title=data.title,
            caption=data.caption,
            description=data.description,
            cover_img_name=cover_img_name,
        )
        old_cover_img_name = await update_project_db(project_id, persisted_project)
    except (ProjectUpdateError, WorkNotFoundError):
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
        raise ProjectUpdateError from error

    try:
        _remove_media_files(old_cover_img_name, works_assets_dir)
    except OSError as error:
        raise ProjectUpdateError from error


async def add_project_image_handler(
    project_id: int,
    image: UploadFile,
    description: str | None,
    order_index: int,
    works_assets_dir: Path,
) -> int:
    image_path: Optional[Path] = None
    thumbnail_path: Optional[Path] = None

    try:
        img_name, image_path, thumbnail_path = await save_uploaded_image(image, works_assets_dir)
        persisted_image = ProjectImageCreateSchema(
            img_name=img_name,
            description=description.strip() or None if description is not None else None,
            order_index=order_index,
        )
        return await create_project_image_db(project_id, persisted_image)
    except (ProjectImageUpdateError, WorkNotFoundError):
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
        raise ProjectImageUpdateError from error


async def update_project_image_handler(image_id: int, data: ProjectImageUpdateSchema) -> None:
    await update_project_image_db(image_id, data)


async def delete_project_image_handler(image_id: int, works_assets_dir: Path) -> None:
    try:
        image_name = await delete_project_image_db(image_id)
        _remove_media_files(image_name, works_assets_dir)
    except WorkNotFoundError:
        raise
    except OSError as error:
        raise ProjectImageDeleteError from error
