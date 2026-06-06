import asyncio
from pathlib import Path

from sqlalchemy import text

from app.config import get_settings
from app.database import AsyncSessionLocal


async def main() -> None:
    settings = get_settings()
    csv_path = Path(settings.catalog_csv_path)
    print(f"CATALOG_CSV_PATH: {settings.catalog_csv_path}")
    print(f"Resolved path: {csv_path.resolve()}")
    print(f"File exists: {csv_path.exists()}")
    if csv_path.exists():
        lines = csv_path.read_text(encoding="utf-8").splitlines()
        print(f"CSV lines (incl header): {len(lines)}")
        print(f"CSV data rows: {max(len(lines) - 1, 0)}")

    async with AsyncSessionLocal() as db:
        total = (await db.execute(text("SELECT COUNT(*) FROM catalog_reports"))).scalar_one()
        active = (
            await db.execute(
                text("SELECT COUNT(*) FROM catalog_reports WHERE active = 'Y'")
            )
        ).scalar_one()
        embedded = (
            await db.execute(
                text(
                    "SELECT COUNT(*) FROM catalog_reports "
                    "WHERE active = 'Y' AND name_embedding IS NOT NULL"
                )
            )
        ).scalar_one()
        print(f"DB total rows: {total}")
        print(f"DB active rows: {active}")
        print(f"DB active with embeddings: {embedded}")

        rows = (
            await db.execute(
                text(
                    "SELECT id, report_name, active FROM catalog_reports ORDER BY id"
                )
            )
        ).fetchall()
        print("Reports in DB:")
        for row in rows:
            print(f"  {row.id}: {row.report_name} ({row.active})")


if __name__ == "__main__":
    asyncio.run(main())
