from sqlalchemy import text

from ..exceptions import WorkCreateError, WorkLoadError, WorkNotFoundError, WorkUpdateError
from ..logger import get_logger
from ..schemas.content import AdminWorkSchema, ClosedEntitySchema, OpenedWorkSchema, WorkCreateSchema, WorkUpdateSchema
from .session import new_session

logger = get_logger(__name__)


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

    except Exception as error:
        logger.error(f"Ошибка при получении работ категории {section_name}: {str(error)}")
        raise WorkLoadError from error


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

    except Exception as error:
        logger.error(f"Ошибка при получении случайного списка работ: {str(error)}")
        raise WorkLoadError from error


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
    except Exception as error:
        logger.error(f"Ошибка при получении работы | id: {work_id} | Ошибка: {str(error)}")
        raise WorkLoadError from error


async def get_admin_work_db(work_id: int) -> AdminWorkSchema:
    query = text("SELECT section_name, title, caption, description, img_name FROM works WHERE work_id = :work_id")

    try:
        async with new_session() as session:
            result = await session.execute(query, {"work_id": work_id})
            work_data = result.mappings().first()

            if work_data is None:
                raise WorkNotFoundError

            return AdminWorkSchema(
                section_name=work_data["section_name"],
                title=work_data["title"],
                caption=work_data["caption"],
                description=work_data["description"],
                img_name=work_data["img_name"],
            )

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при получении работы для редактирования | id: {work_id} | Ошибка: {str(error)}")
        raise WorkLoadError from error


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

    except Exception as error:
        logger.error(f"Ошибка при создании работы | title: {work.title} | Ошибка: {str(error)}")
        raise WorkCreateError from error


async def update_work_db(work_id: int, work: WorkUpdateSchema) -> str | None:
    select_query = text("SELECT img_name FROM works WHERE work_id = :work_id")
    update_text_query = text(
        "UPDATE works SET section_name = :section_name, title = :title, caption = :caption, description = :description "
        "WHERE work_id = :work_id"
    )
    update_image_query = text(
        "UPDATE works SET section_name = :section_name, title = :title, caption = :caption, "
        "description = :description, img_name = :img_name WHERE work_id = :work_id"
    )

    try:
        async with new_session() as session:
            current_result = await session.execute(select_query, {"work_id": work_id})
            current_work = current_result.mappings().first()

            if current_work is None:
                raise WorkNotFoundError

            query = update_image_query if work.img_name is not None else update_text_query
            params = {
                "work_id": work_id,
                "section_name": work.section_name,
                "title": work.title,
                "caption": work.caption,
                "description": work.description,
            }

            if work.img_name is not None:
                params["img_name"] = work.img_name

            await session.execute(query, params)
            await session.commit()

            return current_work["img_name"] if work.img_name is not None else None

    except WorkNotFoundError:
        raise
    except Exception as error:
        logger.error(f"Ошибка при обновлении работы | id: {work_id} | title: {work.title} | Ошибка: {str(error)}")
        raise WorkUpdateError from error
