/**
 * Bloque GEO / AEO: "En resumen" — datos rápidos y citables por
 * buscadores de IA (AI Overviews, ChatGPT, Perplexity, Gemini).
 */
export type SummaryItem = { label: string; value: string };

export default function QuickSummary({
  items,
  idealFor,
}: {
  items: SummaryItem[];
  idealFor?: string;
}) {
  return (
    <div className="mt-4 rounded-xl2 border border-line border-l-[3px] border-l-orange bg-white p-5">
      <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-muted">En resumen</div>
      <dl className="grid gap-x-8 gap-y-2 sm:grid-cols-2">
        {items.map((it, i) => (
          <div key={i} className="flex justify-between gap-3 border-b border-line/70 pb-1.5 text-[14px]">
            <dt className="text-muted">{it.label}</dt>
            <dd className="text-right font-semibold text-ink">{it.value}</dd>
          </div>
        ))}
      </dl>
      {idealFor && (
        <p className="mt-3 text-[14px] text-body">
          <b className="text-ink">Ideal para:</b> {idealFor}
        </p>
      )}
    </div>
  );
}
