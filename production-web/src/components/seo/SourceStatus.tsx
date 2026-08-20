import Link from "next/link";
import { DATA_LAST_REVIEWED, DATA_LAST_REVIEWED_LABEL } from "@/data/freshness";

export function SourceStatus({ compact = false }: { compact?: boolean }) {
  return <p className={`${compact ? "text-[0.6875rem]" : "text-xs"} leading-5 text-muted`}>Datos del proveedor revisados el <time dateTime={DATA_LAST_REVIEWED}>{DATA_LAST_REVIEWED_LABEL}</time>. Consulta <Link href="/metodologia" className="font-bold text-copy underline decoration-line underline-offset-2 hover:text-ink">cómo comparamos</Link>.</p>;
}
