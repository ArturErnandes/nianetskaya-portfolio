from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .database import get_works_list_db, get_random_works_list_db, get_work_db, get_projects_list_db, get_project_db
from .config import AppConfig
from .exceptions import WorkCreateError, WorkLoadError, WorkNotFoundError
from .logger import get_logger
from .auth import (
    clear_admin_session_cookie,
    has_admin_access,
    set_admin_session_cookie,
    verify_admin_password,
)
from .classes import AdminAuthResponse, AdminLoginRequest, WorkCreateSchema
from .config import AdminConfig
from .handlers import create_work_handler, get_work_create_data, serve_protected_admin_page


logger = get_logger(__name__)


def app_run():
    try:
        logger.info("Запуск FastAPI app")
        uvicorn.run(app, host=AppConfig.host, port=AppConfig.port)

    except Exception as e:
        logger.error(f"Ошибка при запуске FastAPI app: {str(e)}")


app = FastAPI()
FRONTEND_HTML_DIR = Path(__file__).parent.parent / "frontend" / "html"
WORKS_ASSETS_DIR = Path(__file__).parent.parent / "assets" / "works"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/works", tags=["Works"], summary="Получение списка работ указанной категории")
async def get_works_list(section_name: str):
    try:
        return await get_works_list_db(section_name)
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@app.get("/api/random_works", tags=["Works"], summary="Получение случайного списка работ")
async def get_random_works():
    try:
        return await get_random_works_list_db()
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@app.get("/api/works/{work_id}", tags=["Works"], summary="Получение данных указанной работы")
async def get_work(work_id: int):
    try:
        return await get_work_db(work_id)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@app.get("/api/projects", tags=["Projects"], summary="Получение списка проектов указанной категории")
async def get_projects(section_name: str | None):
    try:
        return await get_projects_list_db(section_name)
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@app.get("/api/projects/{project_id}", tags=["Projects"], summary="Получение данных указанного проекта")
async def get_project(project_id: int):
    try:
        return await get_project_db(project_id)
    except WorkNotFoundError:
        raise HTTPException(status_code=404, detail="not_found")
    except WorkLoadError:
        raise HTTPException(status_code=500, detail="load_error")


@app.post("/api/admin/login", tags=["Admin"], summary="Авторизация администратора")
async def admin_login(login_request: AdminLoginRequest):
    if not verify_admin_password(login_request.password, AdminConfig.password_hash):
        raise HTTPException(status_code=401, detail="unauthorized")

    response = JSONResponse(asdict(AdminAuthResponse(ok=True)))
    set_admin_session_cookie(response)
    return response


@app.post("/api/admin/logout", tags=["Admin"], summary="Выход администратора")
async def admin_logout():
    response = JSONResponse(asdict(AdminAuthResponse(ok=True)))
    clear_admin_session_cookie(response)
    return response


@app.post("/api/works/create", tags=["Works"], summary="Создание новой работы")
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


@app.get("/admin/create-entity", tags=["Admin"], summary="Защищенная страница выбора типа сущности")
async def admin_create_entity_page(request: Request):
    return serve_protected_admin_page(request, "create-entity.html", "Admin Create Entity", FRONTEND_HTML_DIR)


@app.get("/admin/create-work", tags=["Admin"], summary="Защищенная страница создания работы")
async def admin_create_work_page(request: Request):
    return serve_protected_admin_page(request, "admin-create-work.html", "Admin Create Work", FRONTEND_HTML_DIR)
