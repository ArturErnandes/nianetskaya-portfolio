from fastapi import FastAPI

from database import get_works_list_db
from logger import get_logger


logger = get_logger(__name__)

app = FastAPI()



@app.get("/get_works_list")
async def get_works_list(section_name):
    return await get_works_list_db(section_name)