from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .config import DbConfig
from .classes import ClosedWorkSchema, OpenedWorkSchema
from .exceptions import WorkLoadError, WorkNotFoundError
from.logger import get_logger


logger = get_logger(__name__)

engine = create_async_engine(
    f'postgresql+asyncpg://{DbConfig.admin}:{DbConfig.password}@{DbConfig.host}:{DbConfig.port}/{DbConfig.db_name}')

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_works_list_db(section_name: str) -> list[ClosedWorkSchema]:
    query = text("SELECT work_id, title, caption, img_name FROM works WHERE section_name = :section_name ORDER BY work_id")

    try:
        async with new_session() as session:
            result = await session.execute(query, {"section_name": section_name})
            works_rows = result.mappings().all()

            return [
                ClosedWorkSchema(
                    id=row["work_id"],
                    title=row["title"],
                    caption=row["caption"],
                    img_name=row["img_name"],
                )
                for row in works_rows
            ]

    except Exception as e:
        logger.exception(f"Ошибка при получении работ категории {section_name}: {str(e)}")
        raise WorkLoadError from e


async def get_random_works_list_db() -> list[ClosedWorkSchema]:
    query = text("SELECT work_id, title, caption, img_name FROM works ORDER BY RANDOM()")

    try:
        async with new_session() as session:
            result = await session.execute(query)
            works_rows = result.mappings().all()

            return [
                ClosedWorkSchema(
                    id=row["work_id"],
                    title=row["title"],
                    caption=row["caption"],
                    img_name=row["img_name"],
                )
                for row in works_rows
            ]

    except Exception as e:
        logger.exception(f"Ошибка при получении случайного списка работ: {str(e)}")
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
        logger.exception(f"Ошибка при получении работы | id: {work_id} | Ошибка: {str(e)}")
        raise WorkLoadError from e
