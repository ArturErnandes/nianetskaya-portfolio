from sqlalchemy import text

from ..exceptions import (
    ProjectCreateError,
    ProjectImageDeleteError,
    ProjectImageUpdateError,
    ProjectUpdateError,
    WorkLoadError,
    WorkNotFoundError,
)
from ..logger import get_logger
from ..schemas.content import (
    AdminProjectImageSchema,
    AdminProjectSchema,
    ClosedEntitySchema,
    OpenedProjectSchema,
    ProjectCreateSchema,
    ProjectImageCreateSchema,
    ProjectImageSchema,
    ProjectImageUpdateSchema,
    ProjectUpdateSchema,
)
from .session import new_session

logger = get_logger(__name__)


async def get_projects_list_db(section_name: str) -> list[ClosedEntitySchema]:
    query = text(
        "SELECT project_id, title, caption, cover_img_name FROM projects "
        "WHERE section_name = :section_name "
        "ORDER BY project_id"
    )

    try:
        async with new_session() as session:
            result = await session.execute(query, {"section_name": section_name})
            projects_rows = result.mappings().all()

            return [
                ClosedEntitySchema(
                    id=row["project_id"],
                    title=row["title"],
                    caption=row["caption"],
                    img_name=row["cover_img_name"],
                )
                for row in projects_rows
            ]

    except Exception as error:
        logger.error(f"Ошибка при получении проектов категории {section_name}: {str(error)}")
        raise WorkLoadError from error


async def get_project_images_db(project_id: int) -> list[ProjectImageSchema]:
    query = text(
        "SELECT img_name, description FROM project_images "
        "WHERE project_id = :project_id ORDER BY order_index"
    )

    try:
        async with new_session() as session:
            result = await session.execute(query, {"project_id": project_id})
            images_rows = result.mappings().all()

            return [
                ProjectImageSchema(
                    img_name=row["img_name"],
                    description=row["description"],
                )
                for row in images_rows
            ]

    except Exception as error:
        logger.error(f"Ошибка при получении изображений проекта | id: {project_id} | Ошибка: {str(error)}")
        raise WorkLoadError from error


async def get_admin_project_images_db(project_id: int) -> list[AdminProjectImageSchema]:
    query = text(
        "SELECT image_id, img_name, description, order_index FROM project_images "
        "WHERE project_id = :project_id ORDER BY order_index"
    )

    try:
        async with new_session() as session:
            result = await session.execute(query, {"project_id": project_id})
            images_rows = result.mappings().all()

            return [
                AdminProjectImageSchema(
                    image_id=row["image_id"],
                    img_name=row["img_name"],
                    description=row["description"],
                    order_index=row["order_index"],
                )
                for row in images_rows
            ]

    except Exception as error:
        logger.error(f"Ошибка при получении изображений проекта для редактирования | id: {project_id} | Ошибка: {str(error)}")
        raise WorkLoadError from error


async def get_project_db(project_id: int) -> OpenedProjectSchema:
    project_query = text(
        "SELECT section_name, title, description, cover_img_name "
        "FROM projects WHERE project_id = :project_id"
    )

    try:
        async with new_session() as session:
            project_result = await session.execute(project_query, {"project_id": project_id})
            project_data = project_result.mappings().first()

            if project_data is None:
                raise WorkNotFoundError

            images = await get_project_images_db(project_id)

            return OpenedProjectSchema(
                section_name=project_data["section_name"],
                title=project_data["title"],
                description=project_data["description"],
                cover_img_name=project_data["cover_img_name"],
                images=images,
            )

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при получении проекта | id: {project_id} | Ошибка: {str(error)}")
        raise WorkLoadError from error


async def get_admin_project_db(project_id: int) -> AdminProjectSchema:
    project_query = text(
        "SELECT section_name, title, caption, description, cover_img_name "
        "FROM projects WHERE project_id = :project_id"
    )

    try:
        async with new_session() as session:
            project_result = await session.execute(project_query, {"project_id": project_id})
            project_data = project_result.mappings().first()

            if project_data is None:
                raise WorkNotFoundError

            images = await get_admin_project_images_db(project_id)

            return AdminProjectSchema(
                section_name=project_data["section_name"],
                title=project_data["title"],
                caption=project_data["caption"],
                description=project_data["description"],
                cover_img_name=project_data["cover_img_name"],
                images=images,
            )

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при получении проекта для редактирования | id: {project_id} | Ошибка: {str(error)}")
        raise WorkLoadError from error


async def create_project_db(project: ProjectCreateSchema) -> int:
    if project.cover_img_name is None:
        raise ProjectCreateError

    project_query = text(
        "INSERT INTO projects (section_name, title, caption, cover_img_name, description) "
        "VALUES (:section_name, :title, :caption, :cover_img_name, :description) "
        "RETURNING project_id"
    )
    image_query = text(
        "INSERT INTO project_images (project_id, description, img_name, order_index) "
        "VALUES (:project_id, :description, :img_name, :order_index)"
    )

    try:
        async with new_session() as session:
            project_result = await session.execute(
                project_query,
                {
                    "section_name": project.section_name,
                    "title": project.title,
                    "caption": project.caption,
                    "cover_img_name": project.cover_img_name,
                    "description": project.description,
                },
            )
            created_project_id = int(project_result.scalar_one())

            for image in project.images or []:
                if image.img_name is None:
                    raise ProjectCreateError

                await session.execute(
                    image_query,
                    {
                        "project_id": created_project_id,
                        "description": image.description,
                        "img_name": image.img_name,
                        "order_index": image.order_index,
                    },
                )

            await session.commit()
            return created_project_id

    except ProjectCreateError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при создании проекта | title: {project.title} | Ошибка: {str(error)}")
        raise ProjectCreateError from error


async def update_project_db(project_id: int, project: ProjectUpdateSchema) -> str | None:
    select_query = text("SELECT cover_img_name FROM projects WHERE project_id = :project_id")
    update_text_query = text(
        "UPDATE projects SET section_name = :section_name, title = :title, caption = :caption, description = :description "
        "WHERE project_id = :project_id"
    )
    update_cover_query = text(
        "UPDATE projects SET section_name = :section_name, title = :title, caption = :caption, "
        "description = :description, cover_img_name = :cover_img_name WHERE project_id = :project_id"
    )

    try:
        async with new_session() as session:
            current_result = await session.execute(select_query, {"project_id": project_id})
            current_project = current_result.mappings().first()

            if current_project is None:
                raise WorkNotFoundError

            query = update_cover_query if project.cover_img_name is not None else update_text_query
            params = {
                "project_id": project_id,
                "section_name": project.section_name,
                "title": project.title,
                "caption": project.caption,
                "description": project.description,
            }

            if project.cover_img_name is not None:
                params["cover_img_name"] = project.cover_img_name

            await session.execute(query, params)
            await session.commit()

            return current_project["cover_img_name"] if project.cover_img_name is not None else None

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при обновлении проекта | id: {project_id} | title: {project.title} | Ошибка: {str(error)}")
        raise ProjectUpdateError from error


async def create_project_image_db(project_id: int, image: ProjectImageCreateSchema) -> int:
    if image.img_name is None:
        raise ProjectImageUpdateError

    project_query = text("SELECT project_id FROM projects WHERE project_id = :project_id")
    image_query = text(
        "INSERT INTO project_images (project_id, description, img_name, order_index) "
        "VALUES (:project_id, :description, :img_name, :order_index) RETURNING image_id"
    )

    try:
        async with new_session() as session:
            project_result = await session.execute(project_query, {"project_id": project_id})

            if project_result.mappings().first() is None:
                raise WorkNotFoundError

            image_result = await session.execute(
                image_query,
                {
                    "project_id": project_id,
                    "description": image.description,
                    "img_name": image.img_name,
                    "order_index": image.order_index,
                },
            )
            await session.commit()
            created_image_id = image_result.scalar_one()

            return int(created_image_id)

    except WorkNotFoundError:
        raise
    except ProjectImageUpdateError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при создании изображения проекта | id: {project_id} | Ошибка: {str(error)}")
        raise ProjectImageUpdateError from error


async def update_project_image_db(image_id: int, image: ProjectImageUpdateSchema) -> None:
    query = text(
        "UPDATE project_images SET description = :description, order_index = :order_index "
        "WHERE image_id = :image_id RETURNING image_id"
    )

    try:
        async with new_session() as session:
            result = await session.execute(
                query,
                {
                    "image_id": image_id,
                    "description": image.description,
                    "order_index": image.order_index,
                },
            )

            if result.mappings().first() is None:
                raise WorkNotFoundError

            await session.commit()

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при обновлении изображения проекта | id: {image_id} | Ошибка: {str(error)}")
        raise ProjectImageUpdateError from error


async def delete_project_image_db(image_id: int) -> str:
    query = text("DELETE FROM project_images WHERE image_id = :image_id RETURNING img_name")

    try:
        async with new_session() as session:
            result = await session.execute(query, {"image_id": image_id})
            image_data = result.mappings().first()

            if image_data is None:
                raise WorkNotFoundError

            await session.commit()
            return image_data["img_name"]

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при удалении изображения проекта | id: {image_id} | Ошибка: {str(error)}")
        raise ProjectImageDeleteError from error
