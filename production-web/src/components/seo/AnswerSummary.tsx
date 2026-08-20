import type { ReactNode } from "react";

interface Fact {
  label: string;
  value: ReactNode;
}

export function AnswerSummary({ title = "Resumen rápido", answer, facts }: { title?: string; answer: string; facts: Fact[] }) {
  return (
    <section aria-labelledby="resumen-rapido" className="rounded-xl border border-line bg-surface p-5 sm:p-7">
      <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Respuesta directa</p>
      <h2 id="resumen-rapido" className="font-display mt-3 text-2xl font-semibold tracking-[-0.04em] text-ink">{title}</h2>
      <p className="mt-3 max-w-4xl text-sm leading-6 text-copy">{answer}</p>
      <dl className="mt-6 grid gap-4 border-t border-line pt-5 sm:grid-cols-3">
        {facts.map((fact) => <div key={fact.label}><dt className="text-[0.625rem] font-bold tracking-[0.08em] text-muted uppercase">{fact.label}</dt><dd className="mt-2 text-sm font-semibold text-ink">{fact.value}</dd></div>)}
      </dl>
    </section>
  );
}
