import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumb } from "@/components/seo/Breadcrumb";
import { Schema } from "@/components/seo/Schema";
import snapshots from "@/data/market-snapshots.json";
import { absoluteUrl } from "@/lib/seo";

export const metadata: Metadata = { title: "Sala de prensa y datos de renting", description: "Datos propios, metodología y recursos citables de MyRenting sobre cuotas de renting en España.", alternates: { canonical: "/prensa" }, openGraph: { type: "website", title: "Datos de renting para prensa y analistas", description: "Índice mensual de cuotas y recursos citables de MyRenting.", url: "/prensa" } };

export default function PressPage() {
  const latest = snapshots.snapshots.at(-1)!;
  const facts = [`${latest.offers.toLocaleString("es-ES")} combinaciones de cuota analizadas`, `${latest.vehicles} vehículos activos`, `Mediana para particulares: ${latest.audiences.particular.median.toLocaleString("es-ES")} €/mes`, `Mediana para autónomos: ${latest.audiences.autonomo.median.toLocaleString("es-ES")} €/mes sin asumir IVA`, `El ${latest.entry.withoutEntry === latest.offers ? "100 %" : `${Math.round(latest.entry.withoutEntry / latest.offers * 100)} %`} del inventario publicado no exige entrada`];
  return <main id="contenido-principal" className="mx-auto max-w-5xl px-5 py-8 sm:px-8 sm:py-12">
    <Schema data={{ "@context": "https://schema.org", "@type": "CollectionPage", "@id": `${absoluteUrl("/prensa")}#webpage`, url: absoluteUrl("/prensa"), name: "Sala de prensa y datos de renting", description: "Datos propios y recursos citables de MyRenting.", publisher: { "@id": `${absoluteUrl("/")}#organization` }, inLanguage: "es-ES" }} />
    <Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: "Prensa y datos", path: "/prensa" }]} />
    <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Prensa · Datos · Investigación</p><h1 className="font-display mt-3 max-w-4xl text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Datos de renting listos para citar</h1><p className="mt-5 max-w-3xl text-base leading-7 text-muted">Publicamos cortes reproducibles del inventario que compara MyRenting. No representan todo el mercado español y nunca deben presentarse como datos de ventas.</p>
    <section className="mt-10 rounded-xl border border-line bg-surface p-6 sm:p-8"><h2 className="font-display text-2xl font-semibold">Corte {latest.period}</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-copy">{facts.map((fact) => <li key={fact}>— {fact}</li>)}</ul></section>
    <section className="mt-10 grid gap-5 sm:grid-cols-2"><article className="rounded-xl bg-ink p-6 text-white"><h2 className="font-display text-2xl font-semibold">Informe completo</h2><p className="mt-3 text-sm leading-6 text-slate-300">Tablas por perfil, combustible, marca, entrada y evolución mensual.</p><Link href="/informes/renting-espana-2026" className="mt-5 inline-block font-bold text-orange-400">Consultar informe →</Link></article><article className="rounded-xl border border-line bg-surface p-6"><h2 className="font-display text-2xl font-semibold">Dataset reutilizable</h2><p className="mt-3 text-sm leading-6 text-muted">JSON estructurado con alcance, metodología, licencia de cita y snapshots.</p><a href="/informes/renting-espana-2026/datos.json" className="mt-5 inline-block font-bold text-brand">Abrir datos JSON →</a></article></section>
    <section className="mt-10 border-y border-line py-8"><h2 className="font-display text-2xl font-semibold">Cómo citar</h2><p className="mt-4 text-sm leading-7 text-copy">Fuente sugerida: “MyRenting, Índice de cuotas publicadas, {latest.period}”. Incluye un enlace al <Link href="/informes/renting-espana-2026" className="font-bold underline">informe canónico</Link>. Para consultas: <a href="mailto:mtiagconsulting@gmail.com" className="font-bold text-brand">mtiagconsulting@gmail.com</a>.</p></section>
  </main>;
}
