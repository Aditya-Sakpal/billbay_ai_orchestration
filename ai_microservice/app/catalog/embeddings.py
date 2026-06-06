import asyncio

from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.embeddings import embed_text


async def embed_catalog() -> None:
    async with AsyncSessionLocal() as session:
        total_result = await session.execute(
            text("SELECT COUNT(*) AS cnt FROM catalog_reports WHERE active = 'Y'")
        )
        total_active = total_result.scalar_one()

        pending_result = await session.execute(
            text(
                """
                SELECT id, report_name
                FROM catalog_reports
                WHERE active = 'Y'
                  AND name_embedding IS NULL
                ORDER BY id
                """
            )
        )
        pending_rows = pending_result.mappings().all()

        if not pending_rows:
            print("All active catalog reports already have embeddings.")
            return

        already_embedded = total_active - len(pending_rows)
        for offset, row in enumerate(pending_rows, start=1):
            embedding = await embed_text(row["report_name"])
            embedding_literal = "[" + ",".join(str(value) for value in embedding) + "]"

            await session.execute(
                text(
                    """
                    UPDATE catalog_reports
                    SET name_embedding = CAST(:embedding AS vector)
                    WHERE id = :report_id
                    """
                ),
                {
                    "embedding": embedding_literal,
                    "report_id": row["id"],
                },
            )
            await session.commit()

            progress = already_embedded + offset
            print(f"Embedded {progress}/{total_active}: {row['report_name']}")


def main() -> None:
    asyncio.run(embed_catalog())


if __name__ == "__main__":
    main()
