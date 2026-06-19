const NUMERIC_PATTERN = /^-?\d+(\.\d+)?$/;

const CURRENCY_HINT_HEADERS = new Set([
  "total",
  "totaldue",
  "total due",
  "creditlimit",
  "credit limit",
  "invoice_amount",
  "amount_paid",
  "amount_due",
  "account_balance",
  "so_invoiced",
  "so_uninvoiced",
  "so_total",
  "avg_sales_3",
  "avg_paid_3",
]);

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

function parseNumeric(value: string): number | null {
  const cleaned = value.replace(/[$,\s]/g, "");
  if (!NUMERIC_PATTERN.test(cleaned)) {
    return null;
  }
  return Number(cleaned);
}

export function columnLooksNumeric(
  header: string,
  columnValues: string[],
): boolean {
  const lowerHeader = header.toLowerCase();
  if (
    MONTH_HEADERS.has(lowerHeader) ||
    CURRENCY_HINT_HEADERS.has(lowerHeader) ||
    lowerHeader.includes("amount") ||
    lowerHeader.includes("total") ||
    lowerHeader.includes("limit") ||
    lowerHeader.includes("balance") ||
    lowerHeader.includes("invoiced") ||
    lowerHeader.includes("aging") ||
    lowerHeader.includes("quota")
  ) {
    return columnValues.some((value) => parseNumeric(value) !== null);
  }

  const numericCount = columnValues.filter(
    (value) => parseNumeric(value) !== null,
  ).length;
  return numericCount > 0 && numericCount >= columnValues.length * 0.6;
}

export function shouldFormatAsCurrency(
  header: string,
  columnValues: string[],
): boolean {
  const lowerHeader = header.toLowerCase();
  if (
    MONTH_HEADERS.has(lowerHeader) ||
    CURRENCY_HINT_HEADERS.has(lowerHeader) ||
    lowerHeader.includes("amount") ||
    lowerHeader.includes("total") ||
    lowerHeader.includes("limit") ||
    lowerHeader.includes("balance") ||
    lowerHeader.includes("invoiced") ||
    lowerHeader.includes("due") ||
    lowerHeader.includes("revenue") ||
    lowerHeader.includes("margin") ||
    lowerHeader.includes("sales") ||
    lowerHeader.includes("paid")
  ) {
    return columnLooksNumeric(header, columnValues);
  }
  return false;
}

export function formatCellValue(
  value: string,
  header: string,
  columnValues: string[],
): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return "—";
  }

  const num = parseNumeric(trimmed);
  if (num === null) {
    return trimmed;
  }

  if (shouldFormatAsCurrency(header, columnValues)) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: num % 1 === 0 ? 0 : 2,
    }).format(num);
  }

  if (Number.isInteger(num)) {
    return new Intl.NumberFormat("en-US").format(num);
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(num);
}

export function isLabelColumn(header: string, index: number): boolean {
  if (index === 0) {
    return true;
  }
  const lower = header.toLowerCase();
  return (
    lower.includes("department") ||
    lower.includes("salesperson") ||
    lower.includes("customer") ||
    lower.includes("partner") ||
    lower.includes("name")
  );
}

export function isNumericColumn(
  header: string,
  columnValues: string[],
): boolean {
  return columnLooksNumeric(header, columnValues);
}
