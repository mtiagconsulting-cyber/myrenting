import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Breadcrumb } from "@/components/seo/Breadcrumb";

export const metadata: Metadata = { title: "Guías de renting", description: "Conceptos y criterios para comparar ofertas de renting y elegir mejor.", alternates: { canonical: "/guias" } };

const guides = [
  { title: "Cómo comparar dos ofertas", text: "Iguala duración y kilometraje, suma la entrada y calcula el coste total.", href: "/comparar" },
  { title: "Elegir combustible", text: "Valora recorridos, acceso a carga y uso urbano antes de decidir entre híbrido y eléctrico.", href: "/renting/hibridos" },
  { title: "Entender una cuota", text: "Una cuota solo tiene sentido junto a entrada, kilómetros y servicios incluidos.", href: "/metodologia" },
];

export default function GuidesPage() {
  return <main id="contenido-principal" className="mx-auto max-w-5xl px-5 py-7 sm:px-8 sm:py-10"><Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: "Guías", path: "/guias" }]} /><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Decidir mejor</p><h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Guías de renting</h1><p className="mt-5 max-w-2xl text-base leading-7 text-muted">Criterios prácticos para leer ofertas, comparar condiciones y elegir un coche adecuado para tu uso.</p><div className="mt-10 grid gap-4 sm:grid-cols-3">{guides.map((guide) => <Link key={guide.title} href={guide.href} className="group flex min-h-56 flex-col rounded-xl border border-line bg-surface p-6"><h2 className="font-display text-2xl font-semibold tracking-[-0.04em] text-ink">{guide.title}</h2><p className="mt-4 text-sm leading-6 text-muted">{guide.text}</p><span className="mt-auto flex items-center gap-2 pt-6 text-sm font-bold text-brand">Seguir leyendo <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" aria-hidden="true" /></span></Link>)}</div></main>;
}
