from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from ...auth import has_admin_access
from ...db.project_repositories import get_admin_project_db, get_project_db, get_projects_list_db
from ...exceptions import (
    ProjectCreateError,
    ProjectImageDeleteError,
    ProjectImageUpdateError,
    ProjectUpdateError,
    WorkLoadError,
    WorkNotFoundError,
)
from ...schemas.content import ProjectCreateSchema, ProjectImageUpdateSchema, ProjectUpdateSchema
from ...services.content import (
    add_project_image_handler,
    create_project_handler,
    delete_project_image_handler,
    get_project_create_data,
    get_project_image_update_data,
    get_project_update_data,
    update_project_handler,
    update_project_image_handler,
)
from ..router_constants import WORKS_ASSETS_DIR

router = APIRouter()


@router.get("/api/projects", tags=["Projects"], summary="Получение списка проектов указанной категории")
async def get_projects(section_name: str):
    try:
        return await get_projects_list_db(section_name)
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@router.get("/api/projects/{project_id}", tags=["Projects"], summary="Получение данных указанного проекта")
async def get_project(project_id: int):
    try:
        return await get_project_db(project_id)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@router.post("/api/projects/create", tags=["Projects"], summary="Создание нового проекта")
async def create_project(
    request: Request,
    data: ProjectCreateSchema = Depends(get_project_create_data),
    cover_image: UploadFile = File(...),
    gallery_images: list[UploadFile] = File(default=[]),
    gallery_descriptions: list[str] = Form(default=[]),
):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        created_project_id = await create_project_handler(data, cover_image, gallery_images, gallery_descriptions, WORKS_ASSETS_DIR)
    except ProjectCreateError:
        raise HTTPException(status_code=500, detail="create_error")

    return JSONResponse({"id": created_project_id}, status_code=201)


@router.get("/api/admin/projects/{project_id}", tags=["Admin"], summary="Получение данных проекта для редактирования")
async def get_admin_project(request: Request, project_id: int):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        return await get_admin_project_db(project_id)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@router.patch("/api/admin/projects/{project_id}", tags=["Admin"], summary="Обновление проекта")
async def update_project(
    request: Request,
    project_id: int,
    data: ProjectUpdateSchema = Depends(get_project_update_data),
    cover_image: UploadFile | None = File(None),
):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        await update_project_handler(project_id, data, cover_image, WORKS_ASSETS_DIR)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except ProjectUpdateError:
        raise HTTPException(status_code=500, detail="update_error")

    return JSONResponse({"status": "ok"})


@router.post("/api/admin/projects/{project_id}/images", tags=["Admin"], summary="Добавление изображения проекта")
async def add_project_image(
    request: Request,
    project_id: int,
    image: UploadFile = File(...),
    description: str | None = Form(None),
    order_index: int = Form(...),
):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        created_image_id = await add_project_image_handler(project_id, image, description, order_index, WORKS_ASSETS_DIR)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except ProjectImageUpdateError:
        raise HTTPException(status_code=500, detail="update_error")

    return JSONResponse({"id": created_image_id}, status_code=201)


@router.patch("/api/admin/project-images/{image_id}", tags=["Admin"], summary="Обновление изображения проекта")
async def update_project_image(
    request: Request,
    image_id: int,
    data: ProjectImageUpdateSchema = Depends(get_project_image_update_data),
):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        await update_project_image_handler(image_id, data)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except ProjectImageUpdateError:
        raise HTTPException(status_code=500, detail="update_error")

    return JSONResponse({"status": "ok"})


@router.delete("/api/admin/project-images/{image_id}", tags=["Admin"], summary="Удаление изображения проекта")
async def delete_project_image(request: Request, image_id: int):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        await delete_project_image_handler(image_id, WORKS_ASSETS_DIR)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except ProjectImageDeleteError:
        raise HTTPException(status_code=500, detail="delete_error")

    return JSONResponse({"status": "ok"})
