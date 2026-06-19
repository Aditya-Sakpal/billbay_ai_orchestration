"use client";

import {
  columnLooksNumeric,
  formatCellValue,
  isLabelColumn,
} from "@/lib/format-cell";
import {
  parseMarkdownTable,
  trimZeroMonthColumns,
  type ParsedTable,
} from "@/lib/parse-markdown-table";
import { cn } from "@/lib/utils";

interface DataTableProps {
  markdown: string;
  className?: string;
}

function prepareTable(markdown: string): ParsedTable | null {
  const parsed = parseMarkdownTable(markdown);
  if (!parsed) {
    return null;
  }
  return trimZeroMonthColumns(parsed);
}

export function DataTable({ markdown, className }: DataTableProps) {
  const table = prepareTable(markdown);
  if (!table) {
    return null;
  }

  const columnValues = table.headers.map((_, colIndex) =>
    table.rows.map((row) => row[colIndex] ?? ""),
  );

  return (
    <div className={cn("table-scroll-fade relative", className)}>
      <div className="max-h-80 overflow-auto rounded-xl border border-slate-200/80">
        <table className="w-full min-w-max border-collapse text-sm">
          <thead className="sticky top-0 z-20 bg-slate-100/95 backdrop-blur-sm">
            <tr>
              {table.headers.map((header, index) => (
                <th
                  key={`${header}-${index}`}
                  className={cn(
                    "border-b border-slate-200 px-3 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 whitespace-nowrap",
                    index === 0 &&
                      "sticky left-0 z-30 bg-slate-100/95 backdrop-blur-sm",
                    columnLooksNumeric(header, columnValues[index]) &&
                      "text-right",
                  )}
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="group transition-colors hover:bg-teal-50/40"
              >
                {row.map((cell, colIndex) => {
                  const header = table.headers[colIndex];
                  const formatted = formatCellValue(
                    cell,
                    header,
                    columnValues[colIndex],
                  );
                  const numeric = columnLooksNumeric(
                    header,
                    columnValues[colIndex],
                  );

                  return (
                    <td
                      key={colIndex}
                      className={cn(
                        "border-b border-slate-100 px-3 py-2 text-slate-700 whitespace-nowrap tabular-nums",
                        colIndex === 0 &&
                          "sticky left-0 z-10 bg-white font-medium text-slate-900 group-hover:bg-teal-50/40",
                        numeric && "text-right",
                        isLabelColumn(header, colIndex) &&
                          colIndex !== 0 &&
                          "text-left font-normal",
                      )}
                    >
                      {formatted}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function getTableRowCount(markdown: string): number | null {
  const table = prepareTable(markdown);
  return table?.rows.length ?? null;
}

export function tableToPlainText(markdown: string): string | null {
  const table = prepareTable(markdown);
  if (!table) {
    return null;
  }

  const columnValues = table.headers.map((_, colIndex) =>
    table.rows.map((row) => row[colIndex] ?? ""),
  );

  const headerLine = table.headers.join("\t");
  const bodyLines = table.rows.map((row) =>
    row
      .map((cell, index) =>
        formatCellValue(cell, table.headers[index], columnValues[index]),
      )
      .join("\t"),
  );
  return [headerLine, ...bodyLines].join("\n");
}
