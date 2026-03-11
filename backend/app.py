from fastapi import FastAPI, HTTPException

from database import get_works_list_db
from logger import get_logger


logger = get_logger(__name__)

app = FastAPI()


@app.get("/get_works_list", tags=["Works"], summary="Получение списка работ указанной категории")
async def get_works_list(section_name: str):
    try:
        return await get_works_list_db(section_name)
    except RuntimeError:
        raise HTTPException(status_code=500, detail="load_error")