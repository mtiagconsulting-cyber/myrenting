import { ChevronDown } from "lucide-react";

export function FAQ({ items }: { items: Array<{ question: string; answer: string }> }) {
  return (
    <section aria-labelledby="preguntas-frecuentes">
      <h2 id="preguntas-frecuentes" className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Preguntas frecuentes</h2>
      <div className="mt-6 divide-y divide-line border-y border-line">
        {items.map((item) => <details key={item.question} className="group"><summary className="flex cursor-pointer list-none items-center justify-between gap-5 py-5 text-sm font-bold text-ink">{item.question}<ChevronDown size={18} className="shrink-0 transition-transform group-open:rotate-180" aria-hidden="true" /></summary><p className="max-w-3xl pb-5 text-sm leading-6 text-muted">{item.answer}</p></details>)}
      </div>
    </section>
  );
}
