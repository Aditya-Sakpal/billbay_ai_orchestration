from app.agent.state import AgentState
from app.database import AsyncSessionLocal
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.vcorbi_repository import (
    QueryTimeoutError,
    get_vcorbi_repository,
)


async def executor_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}

    report_id = state.get("resolved_report_id")
    if not report_id:
        return {
            "error": "No report resolved. Cannot execute query.",
            "query_result": [],
        }

    async with AsyncSessionLocal() as db:
        repo = CatalogRepository(db)
        report = await repo.get_by_id(report_id)

    if not report:
        return {
            "error": f"Report id {report_id} not found in catalog.",
            "query_result": [],
        }

    vcorbi = get_vcorbi_repository()
    try:
        rows = await vcorbi.execute_report(
            base_sql=report.base_sql,
            bound_filters=state.get("bound_filters", {}),
            after_where=report.after_where,
            user_id=state["user_id"],
            user_id_col=report.user_id_col,
            access_level=state["access_level"],
        )
        return {"query_result": rows}
    except QueryTimeoutError as exc:
        return {"error": str(exc), "query_result": []}
    except Exception as exc:
        return {"error": f"Query failed: {exc}", "query_result": []}
