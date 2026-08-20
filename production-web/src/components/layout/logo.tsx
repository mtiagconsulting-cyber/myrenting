import Link from "next/link";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      className={cn("group inline-flex min-h-11 items-center gap-2.5 text-ink", className)}
      aria-label="MyRenting, inicio"
    >
      <span
        aria-hidden="true"
        className="grid size-8 place-items-center rounded-lg bg-brand font-data text-sm font-semibold text-white"
      >
        M
      </span>
      <span className="font-display text-xl font-semibold tracking-[-0.045em] text-ink">
        My<span className="text-brand">Renting</span>
      </span>
    </Link>
  );
}
