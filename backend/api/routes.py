from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from ..auth import clear_admin_session_cookie, has_admin_access, set_admin_session_cookie, verify_admin_password
from ..classes import AdminAuthResponse, AdminLoginRequest, ProjectCreateSchema, WorkCreateSchema
from ..config import AdminConfig
from ..db.repositories import get_project_db, get_projects_list_db, get_random_works_list_db, get_work_db, get_works_list_db
from ..exceptions import ProjectCreateError, WorkCreateError, WorkLoadError, WorkNotFoundError
from ..services.content import (
    create_project_handler,
    create_work_handler,
    get_project_create_data,
    get_work_create_data,
    serve_protected_admin_page,
)

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_HTML_DIR = PROJECT_ROOT / "frontend" / "html"
WORKS_ASSETS_DIR = PROJECT_ROOT / "assets" / "works"


@router.get("/api/works", tags=["Works"], summary="Получение списка работ указанной категории")
async def get_works_list(section_name: str):
    try:
        return await get_works_list_db(section_name)
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@router.get("/api/random_works", tags=["Works"], summary="Получение случайного списка работ")
async def get_random_works():
    try:
        return await get_random_works_list_db()
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@router.get("/api/works/{work_id}", tags=["Works"], summary="Получение данных указанной работы")
async def get_work(work_id: int):
    try:
        return await get_work_db(work_id)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


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


@router.post("/api/admin/login", tags=["Admin"], summary="Авторизация администратора")
async def admin_login(login_request: AdminLoginRequest):
    if not verify_admin_password(login_request.password, AdminConfig.password_hash):
        raise HTTPException(status_code=401, detail="unauthorized")

    response = JSONResponse(asdict(AdminAuthResponse(ok=True)))
    set_admin_session_cookie(response)
    return response


@router.post("/api/admin/logout", tags=["Admin"], summary="Выход администратора")
async def admin_logout():
    response = JSONResponse(asdict(AdminAuthResponse(ok=True)))
    clear_admin_session_cookie(response)
    return response


@router.post("/api/works/create", tags=["Works"], summary="Создание новой работы")
async def create_work(
    request: Request,
    data: WorkCreateSchema = Depends(get_work_create_data),
    image: UploadFile = File(...),
):
    if not has_admin_access(request):
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        created_work_id = await create_work_handler(data, image, WORKS_ASSETS_DIR)
    except WorkCreateError:
        raise HTTPException(status_code=500, detail="create_error")

    return JSONResponse({"id": created_work_id}, status_code=201)


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


@router.get("/admin/create-entity", tags=["Admin"], summary="Защищенная страница выбора типа сущности")
async def admin_create_entity_page(request: Request):
    return serve_protected_admin_page(request, "create-entity.html", "Admin Create Entity", FRONTEND_HTML_DIR)


@router.get("/admin/create-work", tags=["Admin"], summary="Защищенная страница создания работы")
async def admin_create_work_page(request: Request):
    return serve_protected_admin_page(request, "admin-create-work.html", "Admin Create Work", FRONTEND_HTML_DIR)


@router.get("/admin/create-project", tags=["Admin"], summary="Защищенная страница создания проекта")
async def admin_create_project_page(request: Request):
    return serve_protected_admin_page(request, "admin-create-project.html", "Admin Create Project", FRONTEND_HTML_DIR)
