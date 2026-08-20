import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "brand" | "positive";
};

const tones = {
  neutral: "bg-slate-100 text-copy",
  brand: "bg-orange-50 text-brand",
  positive: "bg-emerald-50 text-positive",
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex min-h-7 items-center rounded-md px-2.5 py-1 text-[0.6875rem] font-bold tracking-[0.04em] uppercase",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
