"use client";

interface UserBubbleProps {
  content: string;
  timestamp: Date;
}

export function UserBubble({ content, timestamp }: UserBubbleProps) {
  return (
    <div className="flex justify-end message-enter">
      <div className="max-w-[88%] sm:max-w-[72%]">
        <div className="rounded-2xl rounded-br-md bg-gradient-to-br from-slate-800 to-slate-900 px-4 py-3.5 text-[15px] text-white shadow-md shadow-slate-900/15">
          <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
        <p className="mt-1.5 text-right text-[11px] text-muted-foreground">
          {timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}
