CREATE TABLE IF NOT EXISTS catalog_reports (
    id              INTEGER PRIMARY KEY,
    report_name     TEXT NOT NULL,
    "group"         TEXT NOT NULL,
    sql_table_name  TEXT NOT NULL,
    base_sql        TEXT NOT NULL,
    filters_raw     TEXT NOT NULL DEFAULT '',
    user_id_col     TEXT NOT NULL DEFAULT 'user_id',
    after_where     TEXT NOT NULL DEFAULT '',
    access_level    INTEGER NOT NULL DEFAULT 0,
    active          CHAR(1) NOT NULL DEFAULT 'Y'
        CHECK (active IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_catalog_reports_active ON catalog_reports (active);
CREATE INDEX IF NOT EXISTS idx_catalog_reports_group ON catalog_reports ("group");
