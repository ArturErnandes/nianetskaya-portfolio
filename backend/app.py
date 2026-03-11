from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .database import get_works_list_db
from .config import AppConfig
from .logger import get_logger


logger = get_logger(__name__)


def app_run():
    try:
        logger.info("Запуск FastAPI app")
        uvicorn.run(app, host=AppConfig.host, port=AppConfig.port)

    except Exception as e:
        logger.error(f"Ошибка при запуске FastAPI app: {str(e)}")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get_works_list", tags=["Works"], summary="Получение списка работ указанной категории")
async def get_works_list(section_name: str):
    try:
        return await get_works_list_db(section_name)
    except RuntimeError:
        raise HTTPException(status_code=500, detail="load_error")