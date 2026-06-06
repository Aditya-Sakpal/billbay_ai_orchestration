from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import CatalogReport
from app.repositories.catalog_repository import CatalogRepository


async def load_catalog(db: AsyncSession) -> list[CatalogReport]:
    repo = CatalogRepository(db)
    return await repo.get_all_active()
