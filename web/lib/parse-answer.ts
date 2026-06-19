const SOURCE_MARKER = "**Source data:**";

export interface ParsedAnswer {
  summary: string;
  tableMarkdown: string | null;
}

/** Remove pipe-style markdown tables from narrative text. */
export function stripMarkdownTables(text: string): string {
  const lines = text.split("\n");
  const kept: string[] = [];
  let index = 0;

  while (index < lines.length) {
    const trimmed = lines[index].trim();
    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      index += 1;
      while (index < lines.length && lines[index].trim().startsWith("|")) {
        index += 1;
      }
      continue;
    }
    kept.push(lines[index]);
    index += 1;
  }

  return kept.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

export function parseAssistantAnswer(answer: string): ParsedAnswer {
  const idx = answer.indexOf(SOURCE_MARKER);
  if (idx === -1) {
    return { summary: answer.trim(), tableMarkdown: null };
  }

  const summary = stripMarkdownTables(answer.slice(0, idx).trim());
  const tableMarkdown = answer.slice(idx + SOURCE_MARKER.length).trim();
  return { summary, tableMarkdown: tableMarkdown || null };
}

export function classifyAnswerTone(answer: string, isError?: boolean) {
  if (isError || answer.includes("Something went wrong")) {
    return "error" as const;
  }
  if (
    answer.includes("You do not have permission") ||
    answer.includes("I could not find a report") ||
    answer.includes("I can only answer questions about")
  ) {
    return "warning" as const;
  }
  if (answer.includes("No data found")) {
    return "info" as const;
  }
  return "success" as const;
}
