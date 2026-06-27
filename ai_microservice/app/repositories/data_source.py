"""Unified data access: live Cornerstone dashboard API (Option A) or VCORBI MySQL."""

from abc import ABC, abstractmethod

from app.catalog.models import CatalogReport
from app.config import get_settings
from app.repositories.dashboard_api_repository import DashboardApiRepository
from app.repositories.vcorbi_repository import (
    AbstractVCORBIRepository,
    QueryTimeoutError,
    get_vcorbi_repository,
)


class DataSource(ABC):
    @abstractmethod
    async def execute_report(
        self,
        report: CatalogReport,
        bound_filters: dict,
        user_id: int,
        access_level: int,
    ) -> list[dict]:
        ...

    @abstractmethod
    async def get_lookup_values(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        ...


class VcorbiDataSource(DataSource):
    def __init__(self, repo: AbstractVCORBIRepository) -> None:
        self._repo = repo

    async def execute_report(
        self,
        report: CatalogReport,
        bound_filters: dict,
        user_id: int,
        access_level: int,
    ) -> list[dict]:
        return await self._repo.execute_report(
            base_sql=report.base_sql,
            bound_filters=bound_filters,
            after_where=report.after_where,
            user_id=user_id,
            user_id_col=report.user_id_col or None,
            access_level=access_level,
        )

    async def get_lookup_values(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        return await self._repo.get_lookup_values(table, column, user_id)


class DashboardApiDataSource(DataSource):
    def __init__(self) -> None:
        self._repo = DashboardApiRepository()

    async def execute_report(
        self,
        report: CatalogReport,
        bound_filters: dict,
        user_id: int,
        access_level: int,
    ) -> list[dict]:
        return await self._repo.execute_report(
            report_id=report.id,
            sql_table_name=report.sql_table_name,
            report_name=report.report_name,
            bound_filters=bound_filters,
            user_id=user_id,
            access_level=access_level,
        )

    async def get_lookup_values(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        return await self._repo.get_lookup_values(table, column, user_id)


def get_data_source() -> DataSource:
    settings = get_settings()
    if settings.data_source_mode == "dashboard_api":
        return DashboardApiDataSource()
    return VcorbiDataSource(get_vcorbi_repository())


__all__ = ["DataSource", "QueryTimeoutError", "get_data_source"]
