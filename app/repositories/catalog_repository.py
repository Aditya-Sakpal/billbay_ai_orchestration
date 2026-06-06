from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import CatalogReport, parse_filters

_SELECT_COLUMNS = """
    SELECT
        id,
        report_name,
        "group",
        sql_table_name,
        base_sql,
        filters_raw,
        user_id_col,
        after_where,
        access_level,
        active
    FROM catalog_reports
"""


class CatalogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @staticmethod
    def _to_catalog_report(row) -> CatalogReport:
        return CatalogReport(
            **row,
            filters_parsed=parse_filters(row["filters_raw"]),
        )

    async def get_all_active(self) -> list[CatalogReport]:
        result = await self._db.execute(
            text(f"{_SELECT_COLUMNS} WHERE active = 'Y' ORDER BY id")
        )
        return [self._to_catalog_report(row) for row in result.mappings().all()]

    async def get_by_id(self, report_id: int) -> CatalogReport | None:
        result = await self._db.execute(
            text(f"{_SELECT_COLUMNS} WHERE id = :report_id AND active = 'Y'"),
            {"report_id": report_id},
        )
        row = result.mappings().first()
        if row is None:
            return None
        return self._to_catalog_report(row)

    async def get_by_group(self, group: str) -> list[CatalogReport]:
        result = await self._db.execute(
            text(
                f'{_SELECT_COLUMNS} WHERE "group" = :group AND active = \'Y\' ORDER BY id'
            ),
            {"group": group},
        )
        return [self._to_catalog_report(row) for row in result.mappings().all()]
