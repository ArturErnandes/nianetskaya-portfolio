from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .config import DbConfig
from .classes import (
    ClosedEntitySchema,
    OpenedProjectSchema,
    OpenedWorkSchema,
    ProjectCreateSchema,
    ProjectImageSchema,
    WorkCreateSchema,
)
from .exceptions import ProjectCreateError, WorkCreateError, WorkLoadError, WorkNotFoundError
from.logger import get_logger


logger = get_logger(__name__)

engine = create_async_engine(
    f'postgresql+asyncpg://{DbConfig.admin}:{DbConfig.password}@{DbConfig.host}:{DbConfig.port}/{DbConfig.db_name}')

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_works_list_db(section_name: str) -> list[ClosedEntitySchema]:
    query = text("SELECT work_id, title, caption, img_name FROM works WHERE section_name = :section_name ORDER BY work_id")

    try:
        async with new_session() as session:
            result = await session.execute(query, {"section_name": section_name})
            works_rows = result.mappings().all()

            return [
                ClosedEntitySchema(
                    id=row["work_id"],
                    title=row["title"],
                    caption=row["caption"],
                    img_name=row["img_name"],
                )
                for row in works_rows
            ]

    except Exception as e:
        logger.error(f"Ошибка при получении работ категории {section_name}: {str(e)}")
        raise WorkLoadError from e


async def get_random_works_list_db() -> list[ClosedEntitySchema]:
    query = text("SELECT work_id, title, caption, img_name FROM works ORDER BY RANDOM() LIMIT 20")

    try:
        async with new_session() as session:
            result = await session.execute(query)
            works_rows = result.mappings().all()

            return [
                ClosedEntitySchema(
                    id=row["work_id"],
                    title=row["title"],
                    caption=row["caption"],
                    img_name=row["img_name"],
                )
                for row in works_rows
            ]

    except Exception as e:
        logger.error(f"Ошибка при получении случайного списка работ: {str(e)}")
        raise WorkLoadError from e


async def get_work_db(work_id: int) -> OpenedWorkSchema:
    query = text("SELECT section_name, title, description, img_name FROM works WHERE work_id = :work_id")

    try:
        async with new_session() as session:
            result = await session.execute(query, {"work_id": work_id})
            work_data = result.mappings().first()

            if work_data is None:
                raise WorkNotFoundError

            return OpenedWorkSchema(
                section_name=work_data["section_name"],
                title=work_data["title"],
                description=work_data["description"],
                img_name=work_data["img_name"],
            )

    except WorkNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении работы | id: {work_id} | Ошибка: {str(e)}")
        raise WorkLoadError from e


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

    except Exception as e:
        logger.error(f"Ошибка при получении проектов категории {section_name}: {str(e)}")
        raise WorkLoadError from e


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

    except Exception as e:
        logger.error(f"Ошибка при получении изображений проекта | id: {project_id} | Ошибка: {str(e)}")
        raise WorkLoadError from e


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
    except Exception as e:
        logger.error(f"Ошибка при получении проекта | id: {project_id} | Ошибка: {str(e)}")
        raise WorkLoadError from e


async def create_work_db(work: WorkCreateSchema) -> int:
    if work.img_name is None:
        raise WorkCreateError

    query = text(
        "INSERT INTO works (section_name, title, caption, description, img_name) "
        "VALUES (:section_name, :title, :caption, :description, :img_name) "
        "RETURNING work_id"
    )

    try:
        async with new_session() as session:
            result = await session.execute(
                query,
                {
                    "section_name": work.section_name,
                    "title": work.title,
                    "caption": work.caption,
                    "description": work.description,
                    "img_name": work.img_name,
                },
            )
            await session.commit()
            created_work_id = result.scalar_one()

            return int(created_work_id)

    except Exception as e:
        logger.error(f"Ошибка при создании работы | title: {work.title} | Ошибка: {str(e)}")
        raise WorkCreateError from e


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
    except Exception as e:
        logger.error(f"Ошибка при создании проекта | title: {project.title} | Ошибка: {str(e)}")
        raise ProjectCreateError from e
