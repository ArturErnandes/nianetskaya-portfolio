from fastapi import APIRouter, Request

from ...services.content import serve_protected_admin_page
from ..router_constants import FRONTEND_HTML_DIR

router = APIRouter()


@router.get("/admin/create-entity", tags=["Admin"], summary="Защищенная страница выбора типа сущности")
async def admin_create_entity_page(request: Request):
    return serve_protected_admin_page(request, "create-entity.html", "Admin Create Entity", FRONTEND_HTML_DIR)


@router.get("/admin/create-work", tags=["Admin"], summary="Защищенная страница создания работы")
async def admin_create_work_page(request: Request):
    return serve_protected_admin_page(request, "admin-create-work.html", "Admin Create Work", FRONTEND_HTML_DIR)


@router.get("/admin/create-project", tags=["Admin"], summary="Защищенная страница создания проекта")
async def admin_create_project_page(request: Request):
    return serve_protected_admin_page(request, "admin-create-project.html", "Admin Create Project", FRONTEND_HTML_DIR)


@router.get("/admin/manage", tags=["Admin"], summary="Защищенная страница управления сущностями")
async def admin_manage_page(request: Request):
    return serve_protected_admin_page(request, "admin-manage.html", "Admin Manage", FRONTEND_HTML_DIR)


@router.get("/admin/edit-work/{work_id}", tags=["Admin"], summary="Защищенная страница редактирования работы")
async def admin_edit_work_page(request: Request, work_id: int):
    return serve_protected_admin_page(request, "admin-edit-work.html", "Admin Edit Work", FRONTEND_HTML_DIR)


@router.get("/admin/edit-project/{project_id}", tags=["Admin"], summary="Защищенная страница редактирования проекта")
async def admin_edit_project_page(request: Request, project_id: int):
    return serve_protected_admin_page(request, "admin-edit-project.html", "Admin Edit Project", FRONTEND_HTML_DIR)
