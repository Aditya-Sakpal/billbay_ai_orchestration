import { SUGGESTED_PROMPTS } from "@/data/suggested-prompts";

export interface PromptCategory {
  id: string;
  label: string;
  icon: "performance" | "collections" | "finance";
  prompts: string[];
}

export const PROMPT_CATEGORIES: PromptCategory[] = [
  {
    id: "performance",
    label: "Performance",
    icon: "performance",
    prompts: [
      "Show me sales performance for all salespersons this year",
      "Show me sales for Aelina Senitro",
      "How is sales quota tracking against target this month?",
    ],
  },
  {
    id: "collections",
    label: "Collections",
    icon: "collections",
    prompts: [
      "Which customers have overdue accounts?",
      "Show me outstanding invoices for Karen Ku",
    ],
  },
  {
    id: "finance",
    label: "Finance",
    icon: "finance",
    prompts: ["What is the gross margin analysis for this year?"],
  },
];

export { SUGGESTED_PROMPTS };
