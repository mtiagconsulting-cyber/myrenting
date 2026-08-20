import type { Metadata } from "next";
import { Breadcrumb } from "@/components/seo/Breadcrumb";
import { DATA_LAST_REVIEWED, DATA_LAST_REVIEWED_LABEL } from "@/data/freshness";

export const metadata: Metadata = { title: "Metodología de comparación", description: "Cómo recoge, normaliza y compara MyRenting las ofertas y datos de vehículos.", alternates: { canonical: "/metodologia" } };

const steps = [
  ["Recogida", "Cada oferta conserva su proveedor, cuota, entrada, duración, kilómetros y disponibilidad."],
  ["Normalización", "Mostramos los importes en euros y el kilometraje anual. No mezclamos ofertas con condiciones diferentes sin indicarlo."],
  ["Ordenación", "Por defecto ordenamos por la cuota mensual publicada de menor a mayor. Los filtros mantienen separado el perfil de particular, autónomo o empresa."],
  ["Qué significa «desde»", "Es la cuota mensual más baja encontrada entre las configuraciones activas de la selección. Puede corresponder a una duración, kilometraje y tipo de cliente concretos."],
  ["Cálculo", "El precio mínimo, máximo y medio se calculan exclusivamente sobre las cuotas activas. El coste total estimado suma la entrada y todas las cuotas del contrato."],
  ["IVA", "Indicamos en cada oferta si la cuota incluye IVA. Las tarifas de particulares suelen incluirlo; las de autónomos y empresas pueden mostrarse sin IVA y no deben compararse directamente."],
  ["Entrega inmediata", "Significa que el proveedor comunicó disponibilidad para esa campaña. No equivale a una fecha contractual garantizada: debe confirmarse antes de contratar."],
  ["Revisión", "Las fechas de revisión se publican junto a los datos. Una oferta desactualizada debe retirarse o marcarse como pendiente de verificación."],
];

export default function MethodologyPage() {
  return <main id="contenido-principal" className="mx-auto max-w-4xl px-5 py-7 sm:px-8 sm:py-10"><Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: "Metodología", path: "/metodologia" }]} /><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Transparencia</p><h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Cómo compara MyRenting</h1><p className="mt-5 max-w-3xl text-base leading-7 text-muted">El objetivo es que dos ofertas puedan compararse con las mismas unidades y que cada cifra pueda rastrearse hasta su fuente. El inventario actual procede de M‑Renting, Quadis y la oferta adicional de Kia.</p><p className="mt-5 text-xs text-muted">Última revisión metodológica: <time dateTime={DATA_LAST_REVIEWED}>{DATA_LAST_REVIEWED_LABEL}</time>.</p><div className="mt-10 divide-y divide-line border-y border-line">{steps.map(([title, text]) => <section key={title} className="grid gap-3 py-6 sm:grid-cols-[10rem_1fr]"><h2 className="font-display text-xl font-semibold text-ink">{title}</h2><p className="text-sm leading-6 text-copy">{text}</p></section>)}</div><section className="mt-12 rounded-xl bg-ink p-6 text-white sm:p-8"><h2 className="font-display text-2xl font-semibold">Qué no hacemos</h2><ul className="mt-5 space-y-3 text-sm leading-6 text-slate-300"><li>No creamos puntuaciones sin una metodología verificable.</li><li>No presentamos una cuota sin mostrar entrada, duración y kilómetros.</li><li>No publicamos contenido patrocinado como recomendación independiente.</li><li>No ocultamos si una cuota incluye IVA o debe sumarse.</li></ul></section></main>;
}
