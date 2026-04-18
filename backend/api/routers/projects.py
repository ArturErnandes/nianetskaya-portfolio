from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from ...auth import has_admin_access
from ...db.repositories import get_project_db, get_projects_list_db
from ...exceptions import ProjectCreateError, WorkLoadError, WorkNotFoundError
from ...schemas.content import ProjectCreateSchema
from ...services.content import create_project_handler, get_project_create_data
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
