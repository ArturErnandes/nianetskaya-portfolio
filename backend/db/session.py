from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..config import DbConfig

engine = create_async_engine(
    f"postgresql+asyncpg://{DbConfig.admin}:{DbConfig.password}@{DbConfig.host}:{DbConfig.port}/{DbConfig.db_name}"
)

new_session = async_sessionmaker(engine, expire_on_commit=False)
