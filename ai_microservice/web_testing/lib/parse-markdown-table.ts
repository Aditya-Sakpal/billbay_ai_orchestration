export interface ParsedTable {
  headers: string[];
  rows: string[][];
}

export function parseMarkdownTable(markdown: string): ParsedTable | null {
  const lines = markdown
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("|") && line.endsWith("|"));

  if (lines.length < 2) {
    return null;
  }

  const parseRow = (line: string) =>
    line
      .slice(1, -1)
      .split("|")
      .map((cell) => cell.trim());

  const headers = parseRow(lines[0]);
  const separator = lines[1];
  if (!/^\|[\s\-:|]+\|$/.test(separator)) {
    return null;
  }

  const rows = lines.slice(2).map(parseRow).filter((row) => row.length === headers.length);
  if (rows.length === 0) {
    return null;
  }

  return { headers, rows };
}

const MONTH_HEADERS = new Set([
  "jan",
  "feb",
  "mar",
  "apr",
  "may",
  "jun",
  "jul",
  "aug",
  "sep",
  "oct",
  "nov",
  "dec",
]);

function isZeroValue(value: string): boolean {
  const normalized = value.replace(/[$,\s]/g, "");
  const num = Number(normalized);
  return !Number.isNaN(num) && num === 0;
}

/** Hide month columns where every row is zero. */
export function trimZeroMonthColumns(table: ParsedTable): ParsedTable {
  const columnsToKeep = table.headers.map((header, index) => {
    if (!MONTH_HEADERS.has(header.toLowerCase())) {
      return true;
    }
    return table.rows.some((row) => !isZeroValue(row[index] ?? ""));
  });

  if (columnsToKeep.every(Boolean)) {
    return table;
  }

  return {
    headers: table.headers.filter((_, index) => columnsToKeep[index]),
    rows: table.rows.map((row) =>
      row.filter((_, index) => columnsToKeep[index]),
    ),
  };
}
