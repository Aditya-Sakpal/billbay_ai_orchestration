from app.agent.pipeline_log import log_exception, log_stage
from app.agent.state import AgentState
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.dashboard_api_repository import DashboardApiError
from app.repositories.data_source import QueryTimeoutError, get_data_source


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

    data_source = get_data_source()
    settings = get_settings()
    log_stage(
        "executor",
        report_id=report_id,
        report_name=report.report_name,
        sql_table=report.sql_table_name,
        data_source_mode=settings.data_source_mode,
        bound_filters=state.get("bound_filters", {}),
        base_sql=report.base_sql if settings.data_source_mode != "dashboard_api" else "N/A (dashboard HTML)",
    )
    try:
        rows = await data_source.execute_report(
            report=report,
            bound_filters=state.get("bound_filters", {}),
            user_id=state["user_id"],
            access_level=state["access_level"],
        )
        log_stage(
            "executor",
            report_id=report_id,
            rows_returned=len(rows),
            data_source_mode=settings.data_source_mode,
        )
        return {"query_result": rows}
    except DashboardApiError as exc:
        log_stage("executor", error=str(exc), report_id=report_id)
        return {"error": str(exc), "query_result": []}
    except QueryTimeoutError as exc:
        log_stage("executor", error=str(exc), report_id=report_id)
        return {"error": str(exc), "query_result": []}
    except Exception as exc:
        log_exception("executor", exc, report_id=report_id)
        return {"error": f"Query failed: {exc}", "query_result": []}
