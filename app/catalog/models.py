from typing import Literal, Optional

from pydantic import BaseModel

FilterType = Literal["L", "T", "M", "DF", "DT", "GT", "LT"]


class FilterSpec(BaseModel):
    field_name: str
    filter_type: FilterType
    default_value: Optional[str] = None


class CatalogReport(BaseModel):
    id: int
    report_name: str
    group: str
    sql_table_name: str
    base_sql: str
    filters_raw: str
    filters_parsed: list[FilterSpec]
    user_id_col: str
    after_where: str
    access_level: int
    active: str


def parse_filters(filters_raw: str | None) -> list[FilterSpec]:
    if not filters_raw or not filters_raw.strip():
        return []

    specs: list[FilterSpec] = []
    for part in filters_raw.split(","):
        part = part.strip()
        if not part:
            continue

        tokens = [token.strip() for token in part.split("~")]
        if len(tokens) < 2:
            continue

        field_name, filter_type = tokens[0], tokens[1]
        default_value = tokens[2] if len(tokens) > 2 else None
        specs.append(
            FilterSpec(
                field_name=field_name,
                filter_type=filter_type,  # type: ignore[arg-type]
                default_value=default_value or None,
            )
        )

    return specs
