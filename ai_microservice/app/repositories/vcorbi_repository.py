import asyncio
import re
from abc import ABC, abstractmethod

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.vcorbi import get_vcorbi_session

QUERY_TIMEOUT_SECONDS = 5


class QueryTimeoutError(Exception):
    pass


class AbstractVCORBIRepository(ABC):
    @abstractmethod
    async def execute_report(
        self,
        base_sql: str,
        bound_filters: dict,
        after_where: str | None,
        user_id: int,
        user_id_col: str | None,
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


class MockVCORBIRepository(AbstractVCORBIRepository):
    def _execute_report_sync(
        self,
        base_sql: str,
        bound_filters: dict,
        after_where: str | None,
        user_id: int,
        user_id_col: str | None,
        access_level: int,
    ) -> list[dict]:
        sql = base_sql.strip().rstrip(";")
        conditions: list[str] = []
        params: dict = {}

        for key, value in bound_filters.items():
            clean_key = key.split(".")[-1]
            param_key = f"filter_{clean_key}"
            conditions.append(f"`{clean_key}` = :{param_key}")
            params[param_key] = value

        if user_id_col:
            conditions.append(f"`{user_id_col}` = :user_id")
            params["user_id"] = user_id

        if after_where:
            conditions.append(f"({after_where})")

        if conditions:
            has_where = bool(re.search(r"\bwhere\b", sql, re.IGNORECASE))
            connector = " AND " if has_where else " WHERE "
            sql = f"{sql}{connector}{' AND '.join(conditions)}"

        session = get_vcorbi_session()
        try:
            result = session.execute(
                text(sql),
                params,
                execution_options={"timeout": QUERY_TIMEOUT_SECONDS},
            )
            return [dict(row) for row in result.mappings().all()]
        finally:
            session.close()

    def _get_lookup_values_sync(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        sql = text(
            f"""
            SELECT DISTINCT `{column}` AS value
            FROM `{table}`
            WHERE user_id = :user_id
            ORDER BY `{column}`
            """
        )
        session = get_vcorbi_session()
        try:
            result = session.execute(sql, {"user_id": user_id})
            return [str(row["value"]) for row in result.mappings().all()]
        finally:
            session.close()

    async def execute_report(
        self,
        base_sql: str,
        bound_filters: dict,
        after_where: str | None,
        user_id: int,
        user_id_col: str | None,
        access_level: int,
    ) -> list[dict]:
        del access_level
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(
                    self._execute_report_sync,
                    base_sql,
                    bound_filters,
                    after_where,
                    user_id,
                    user_id_col,
                ),
                timeout=QUERY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            raise QueryTimeoutError(
                f"VCORBI query exceeded {QUERY_TIMEOUT_SECONDS}s timeout"
            ) from exc
        except SQLAlchemyError as exc:
            if "timeout" in str(exc).lower():
                raise QueryTimeoutError(str(exc)) from exc
            raise

    async def get_lookup_values(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(
                    self._get_lookup_values_sync,
                    table,
                    column,
                    user_id,
                ),
                timeout=QUERY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            raise QueryTimeoutError(
                f"VCORBI lookup exceeded {QUERY_TIMEOUT_SECONDS}s timeout"
            ) from exc
        except SQLAlchemyError as exc:
            if "timeout" in str(exc).lower():
                raise QueryTimeoutError(str(exc)) from exc
            raise


class RealVCORBIRepository(AbstractVCORBIRepository):
    async def execute_report(
        self,
        base_sql: str,
        bound_filters: dict,
        after_where: str | None,
        user_id: int,
        user_id_col: str | None,
        access_level: int,
    ) -> list[dict]:
        raise NotImplementedError("RealVCORBI not connected yet")

    async def get_lookup_values(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        raise NotImplementedError("RealVCORBI not connected yet")


def get_vcorbi_repository() -> AbstractVCORBIRepository:
    settings = get_settings()
    if settings.vcorbi_mode == "real":
        return RealVCORBIRepository()
    return MockVCORBIRepository()
