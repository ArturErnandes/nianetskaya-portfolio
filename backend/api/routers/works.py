from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from ...auth import has_admin_access
from ...db.repositories import get_random_works_list_db, get_work_db, get_works_list_db
from ...exceptions import WorkCreateError, WorkLoadError, WorkNotFoundError
from ...schemas.content import WorkCreateSchema
from ...services.content import create_work_handler, get_work_create_data
from ..router_constants import WORKS_ASSETS_DIR

router = APIRouter()


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
