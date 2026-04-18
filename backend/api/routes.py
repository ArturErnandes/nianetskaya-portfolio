from fastapi import APIRouter

from .routers.admin import router as admin_router
from .routers.auth import router as auth_router
from .routers.projects import router as projects_router
from .routers.works import router as works_router

router = APIRouter()

router.include_router(works_router)
router.include_router(projects_router)
router.include_router(auth_router)
router.include_router(admin_router)
