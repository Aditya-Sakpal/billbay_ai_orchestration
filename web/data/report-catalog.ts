export interface ReportCatalogEntry {
  id: number;
  name: string;
  group: string;
  accessLevel: number;
}

export const REPORT_CATALOG: ReportCatalogEntry[] = [
  {
    id: 1,
    name: "Monthly Sales Performance (SO)",
    group: "Performance",
    accessLevel: 50,
  },
  {
    id: 2,
    name: "Gross Margin Analysis (YoY)",
    group: "Finance",
    accessLevel: 30,
  },
  {
    id: 3,
    name: "Overdue Accounts",
    group: "Collections",
    accessLevel: 50,
  },
  {
    id: 4,
    name: "Outstanding Invoices",
    group: "Collections",
    accessLevel: 50,
  },
  {
    id: 5,
    name: "Customer Payment Terms",
    group: "Collections",
    accessLevel: 50,
  },
  {
    id: 6,
    name: "Sales Quota vs Target",
    group: "Performance",
    accessLevel: 50,
  },
  {
    id: 7,
    name: "Key Account Performance",
    group: "Performance",
    accessLevel: 50,
  },
];

export const REPORT_GROUPS = Array.from(
  new Set(REPORT_CATALOG.map((r) => r.group)),
);
