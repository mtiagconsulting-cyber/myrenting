import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { ComparisonSelector } from "@/components/comparison/ComparisonSelector";
import { getComparison, popularComparisonSlugs } from "@/lib/comparison";

export const metadata: Metadata = { title: "Comparar coches de renting", description: "Elige dos coches y compara cuota, entrada, kilómetros, consumo, maletero y servicios incluidos.", alternates: { canonical: "/comparar" } };

export default function ComparePage() {
  return <main id="contenido-principal" className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-16"><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Comparador MyRenting</p><h1 className="font-display mt-3 max-w-3xl text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Compara coches, no solo cuotas</h1><p className="mt-5 max-w-2xl text-base leading-7 text-muted">Pon dos modelos frente a frente y revisa el coste total, las condiciones y las diferencias que afectan a tu decisión.</p><section className="mt-9 rounded-xl border border-line bg-surface p-5 shadow-card sm:p-7"><ComparisonSelector /></section><section className="mt-14"><h2 className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Comparativas populares</h2><div className="mt-6 divide-y divide-line border-y border-line">{popularComparisonSlugs.map((slug) => { const comparison = getComparison(slug); if (!comparison) return null; return <Link key={slug} href={`/comparar/${slug}`} className="group grid grid-cols-[1fr_auto_1fr_auto] items-center gap-3 py-5 text-sm font-bold text-ink"><span>{comparison.first.vehicle.brand} {comparison.first.vehicle.model}</span><span className="font-data text-[0.625rem] text-muted">VS</span><span>{comparison.second.vehicle.brand} {comparison.second.vehicle.model}</span><ArrowRight size={17} className="transition-transform group-hover:translate-x-1" aria-hidden="true" /></Link>; })}</div></section></main>;
}
