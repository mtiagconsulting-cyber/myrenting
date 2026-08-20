import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type DataPointProps = HTMLAttributes<HTMLDivElement> & {
  label: string;
  value: ReactNode;
  detail?: string;
};

export function DataPoint({ className, label, value, detail, ...props }: DataPointProps) {
  return (
    <div className={cn("min-w-0 py-1", className)} {...props}>
      <p className="mb-2 text-[0.6875rem] font-bold tracking-[0.08em] text-muted uppercase">
        {label}
      </p>
      <p className="font-data text-xl font-semibold tracking-[-0.04em] text-ink tabular-nums">
        {value}
      </p>
      {detail ? <p className="mt-1 text-xs text-muted">{detail}</p> : null}
    </div>
  );
}
