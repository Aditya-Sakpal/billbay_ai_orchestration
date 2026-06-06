import asyncio
import csv
from collections import Counter
from pathlib import Path

from sqlalchemy import text

from app.config import get_settings
from app.database import AsyncSessionLocal

UPSERT_SQL = text(
    """
    INSERT INTO catalog_reports (
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
    ) VALUES (
        :id,
        :report_name,
        :group,
        :sql_table_name,
        :base_sql,
        :filters_raw,
        :user_id_col,
        :after_where,
        :access_level,
        :active
    )
    ON CONFLICT (id) DO UPDATE SET
        report_name = EXCLUDED.report_name,
        "group" = EXCLUDED."group",
        sql_table_name = EXCLUDED.sql_table_name,
        base_sql = EXCLUDED.base_sql,
        filters_raw = EXCLUDED.filters_raw,
        user_id_col = EXCLUDED.user_id_col,
        after_where = EXCLUDED.after_where,
        access_level = EXCLUDED.access_level,
        active = EXCLUDED.active
    """
)


def read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def normalize_row(row: dict[str, str]) -> dict:
    return {
        "id": int(row["id"]),
        "report_name": row["report_name"],
        "group": row["group"],
        "sql_table_name": row["sql_table_name"],
        "base_sql": row["base_sql"],
        "filters_raw": row.get("filters_raw", ""),
        "user_id_col": row.get("user_id_col", "user_id"),
        "after_where": row.get("after_where", ""),
        "access_level": int(row.get("access_level", 0)),
        "active": row.get("active", "Y"),
    }


async def ingest_catalog(csv_path: Path) -> None:
    rows = read_csv_rows(csv_path)
    if not rows:
        print("No rows found in CSV.")
        return

    async with AsyncSessionLocal() as session:
        for row in rows:
            await session.execute(UPSERT_SQL, normalize_row(row))
        await session.commit()

    total = len(rows)
    active = sum(1 for row in rows if row.get("active", "Y") == "Y")
    groups = Counter(row["group"] for row in rows)

    print(f"Total rows ingested: {total}")
    print(f"Active rows: {active}")
    print("Rows per group:")
    for group_name, count in sorted(groups.items()):
        print(f"  {group_name}: {count}")


def main() -> None:
    settings = get_settings()
    csv_path = Path(settings.catalog_csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Catalog CSV not found: {csv_path}")

    asyncio.run(ingest_catalog(csv_path))


if __name__ == "__main__":
    main()
