from fastapi import FastAPI

from logger import get_logger


logger = get_logger(__name__)

app = FastAPI()