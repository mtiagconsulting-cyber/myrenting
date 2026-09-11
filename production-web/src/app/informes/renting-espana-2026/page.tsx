import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumb } from "@/components/seo/Breadcrumb";
import { Schema, editorialSchema } from "@/components/seo/Schema";
import { inventoryUpdatedAt, offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import snapshots from "@/data/market-snapshots.json";
import { offerPriceExVat } from "@/lib/offer-pricing";

export const metadata: Metadata = {
  title: "Informe de precios de renting en España 2026",
  description: `Datos propios de ${vehicles.length} vehículos y ${offers.length.toLocaleString("es-ES")} ofertas de renting por perfil, combustible, marca y proveedor.`,
  alternates: { canonical: "/informes/renting-espana-2026" },
  openGraph: { type: "article", title: "Informe de precios de renting en España 2026", description: "Índice mensual reproducible de cuotas publicadas de renting.", url: "/informes/renting-espana-2026", modifiedTime: inventoryUpdatedAt },
};

const audienceLabels = { particular: "Particulares", autonomo: "Autónomos", empresa: "Empresas" } as const;

export default function RentingReport() {
  const latest = snapshots.snapshots.at(-1)!;
  const previous = snapshots.snapshots.at(-2);
  const providerNames = [...new Set(offers.map((offer) => offer.provider.replace(/\s+—\s+.+$/, "")))].sort((a, b) => a.localeCompare(b, "es"));
  const fuels = [...new Set(vehicles.map((vehicle) => vehicle.fuel))].map((fuel) => {
    const ids = new Set(vehicles.filter((vehicle) => vehicle.fuel === fuel).map((vehicle) => vehicle.id));
    return { fuel, ...stats(offers.filter((offer) => ids.has(offer.vehicleId)).map(offerPriceExVat)) };
  }).sort((a, b) => a.median - b.median);
  const article = editorialSchema({ type: "Report", path: "/informes/renting-espana-2026", title: "Informe de precios de renting en España 2026", description: `Análisis propio de ${latest.vehicles} vehículos y ${latest.offers.toLocaleString("es-ES")} ofertas de renting.`, dateModified: inventoryUpdatedAt });
  const monthLabel = new Intl.DateTimeFormat("es-ES", { month: "long", year: "numeric", timeZone: "UTC" }).format(new Date(`${latest.period}-01T00:00:00Z`));

  return <main id="contenido-principal" className="mx-auto max-w-6xl px-5 py-8 sm:px-8 sm:py-12">
    <Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: "Informes", path: "/informes/renting-espana-2026" }]} />
    <Schema data={article} />
    <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Datos propios · {monthLabel}</p>
    <h1 className="font-display mt-3 max-w-5xl text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Índice de precios de renting en España</h1>
    <p className="mt-5 max-w-3xl text-base leading-7 text-muted">Análisis reproducible del inventario disponible en MyRenting. Incluye campañas de {providerNames.join(", ")} y no representa el conjunto completo del mercado español.</p>

    <dl className="mt-10 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-3"><Metric label="Vehículos" value={latest.vehicles} /><Metric label="Ofertas" value={latest.offers.toLocaleString("es-ES")} /><Metric label="Marcas" value={latest.brands.length} /></dl>

    <section className="mt-14"><h2 className="font-display text-3xl font-semibold">Cuota publicada por tipo de cliente</h2><p className="mt-3 text-sm leading-6 text-muted">Las cifras respetan cómo publica cada proveedor: particulares normalmente con IVA; autónomos y empresas normalmente sin IVA. No deben compararse directamente entre perfiles.</p><div className="mt-6 overflow-x-auto"><table className="w-full border-collapse text-left text-sm"><thead><tr className="border-b border-line text-xs text-muted"><th className="py-3">Perfil</th><th>Ofertas</th><th>Mínima</th><th>Mediana</th><th>Máxima</th></tr></thead><tbody>{Object.entries(audienceLabels).map(([audience, label]) => { const item = latest.audiences[audience as keyof typeof audienceLabels]; return <tr key={audience} className="border-b border-line"><th className="py-4">{label}</th><td>{item.offers.toLocaleString("es-ES")}</td><td>{money(item.minimum)}</td><td>{money(item.median)}</td><td>{money(item.maximum)}</td></tr>; })}</tbody></table></div></section>

    <section className="mt-14"><h2 className="font-display text-3xl font-semibold">Cuota mediana por combustible</h2><p className="mt-3 text-sm text-muted">Comparación normalizada sin IVA para evitar mezclar perfiles con distinto tratamiento fiscal.</p><div className="mt-6 grid gap-3 sm:grid-cols-2">{fuels.map((item) => <article key={item.fuel} className="flex items-end justify-between rounded-xl border border-line bg-surface p-5"><div><h3 className="font-bold">{item.fuel}</h3><p className="mt-1 text-xs text-muted">{item.count.toLocaleString("es-ES")} ofertas</p></div><p className="font-data text-2xl font-semibold">{money(item.median)} <span className="font-sans text-xs text-muted">sin IVA</span></p></article>)}</div></section>

    <section className="mt-14"><div className="flex flex-wrap items-end justify-between gap-4"><div><h2 className="font-display text-3xl font-semibold">Índice mensual por marca</h2><p className="mt-3 max-w-3xl text-sm text-muted">Mínimo y mediana sobre las cuotas publicadas, sin ponderar por ventas.</p></div><div className="flex flex-wrap gap-2"><a href="/informes/renting-espana-2026/datos.csv" className="rounded-lg border border-line bg-surface px-4 py-2 text-xs font-bold text-copy">Descargar CSV</a><a href="/informes/renting-espana-2026/datos.json" className="rounded-lg border border-line bg-surface px-4 py-2 text-xs font-bold text-copy">Abrir JSON</a></div></div><div className="mt-6 overflow-x-auto"><table className="w-full border-collapse text-left text-sm"><thead><tr className="border-b border-line text-xs text-muted"><th className="py-3">Marca</th><th>Ofertas</th><th>Mínima</th><th>Mediana</th></tr></thead><tbody>{latest.brands.slice(0, 20).map((item) => <tr key={item.brand} className="border-b border-line"><th className="py-4"><Link href={`/renting/${slug(item.brand)}`} className="hover:text-brand">{item.brand}</Link></th><td>{item.offers.toLocaleString("es-ES")}</td><td>{money(item.minimum)}</td><td>{money(item.median)}</td></tr>)}</tbody></table></div></section>

    <section className="mt-14 grid gap-5 sm:grid-cols-2"><article className="rounded-xl border border-line bg-surface p-6"><h2 className="font-display text-2xl font-semibold">Evolución del inventario</h2><p className="font-data mt-5 text-4xl font-semibold">{previous ? signed(latest.offers - previous.offers) : latest.offers.toLocaleString("es-ES")}</p><p className="mt-2 text-sm text-muted">ofertas frente al corte anterior. La serie se conserva para poder citar cambios reales.</p></article><article className="rounded-xl border border-line bg-surface p-6"><h2 className="font-display text-2xl font-semibold">Ofertas sin entrada</h2><p className="font-data mt-5 text-4xl font-semibold">{Math.round(latest.entry.withoutEntry / latest.offers * 100)} %</p><p className="mt-2 text-sm text-muted">del inventario del corte declara una entrada inicial de 0 €.</p></article></section>

    <section className="mt-14 rounded-xl bg-ink p-7 text-white"><h2 className="font-display text-2xl font-semibold">Metodología y reutilización</h2><p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">Las medianas se calculan sobre ofertas activas, sin ponderar por ventas. Puedes citar los datos indicando “MyRenting, Índice de cuotas publicadas, {latest.period}” y enlazando esta página.</p><Link href="/metodologia" className="mt-5 inline-block font-bold text-orange-400">Consultar metodología completa →</Link></section>
  </main>;
}

function stats(values: number[]) { const sorted = [...values].sort((a, b) => a - b); return { count: sorted.length, median: sorted.length ? sorted[Math.floor(sorted.length / 2)] : 0 }; }
function money(value: number) { return `${value.toLocaleString("es-ES", { maximumFractionDigits: 2 })} €/mes`; }
function signed(value: number) { return `${value > 0 ? "+" : ""}${value.toLocaleString("es-ES")}`; }
function slug(value: string) { return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
function Metric({ label, value }: { label: string; value: string | number }) { return <div className="bg-surface p-6"><dt className="text-xs font-bold uppercase text-muted">{label}</dt><dd className="font-data mt-2 text-3xl font-semibold text-ink">{value}</dd></div>; }
