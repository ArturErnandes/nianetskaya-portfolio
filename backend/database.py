from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import DbConfig
from classes import WorkSchema
from logger import get_logger


logger = get_logger(__name__)

engine = create_async_engine(
    f'postgresql+asyncpg://{DbConfig.admin}:{DbConfig.password}@{DbConfig.host}:{DbConfig.port}/{DbConfig.db_name}')

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_works_list_db(section_name: str) -> list[WorkSchema]:
    query = text("SELECT work_id, title, caption, img_name FROM works WHERE section_name = :section_name")

    try:
        async with new_session() as session:
            works = await session.execute(query, {"section_name": section_name})
            works_rows = works.mappings().all()

            return [
                WorkSchema(
                    id=row["work_id"],
                    title=row["title"],
                    text=row["caption"],
                    img_name=row["img_name"],
                )
                for row in works_rows
            ]

    except Exception as e:
        logger.exception(f"Ошибка при получении работ категории {section_name}: {str(e)}")
        raise RuntimeError("load_error") from e