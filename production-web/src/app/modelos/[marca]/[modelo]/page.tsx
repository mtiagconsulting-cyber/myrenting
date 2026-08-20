import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumb } from "@/components/seo/Breadcrumb";
import { FAQ } from "@/components/seo/FAQ";
import { Schema, faqSchema, itemListSchema } from "@/components/seo/Schema";
import { SourceStatus } from "@/components/seo/SourceStatus";
import { VehicleGrid } from "@/components/vehicles/VehicleGrid";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { audienceLabels, modelPath } from "@/lib/catalog-taxonomy";
import { contentSlug } from "@/lib/content-slug";
import { canonicalVehicles, vehiclesInSameGroup } from "@/lib/vehicle-groups";

type Props = { params: Promise<{ marca: string; modelo: string }> };
const groups = [...new Map(vehicles.map((vehicle) => [`${contentSlug(vehicle.brand)}/${contentSlug(vehicle.model)}`, { brand: vehicle.brand, model: vehicle.model }])).values()];

export function generateStaticParams() { return groups.map(({ brand, model }) => ({ marca: contentSlug(brand), modelo: contentSlug(model) })); }
function findGroup(marca: string, modelo: string) { return groups.find((group) => contentSlug(group.brand) === marca && contentSlug(group.model) === modelo); }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { marca, modelo } = await params; const group = findGroup(marca, modelo); if (!group) return {};
  const related = vehicles.filter((vehicle) => vehicle.brand === group.brand && vehicle.model === group.model);
  const ids = new Set(related.map((vehicle) => vehicle.id)); const prices = offers.filter((offer) => ids.has(offer.vehicleId)).map((offer) => offer.monthlyPrice);
  const minimum = prices.length ? Math.min(...prices).toLocaleString("es-ES", { maximumFractionDigits: 2 }) : "—";
  const title = `Renting ${group.brand} ${group.model} desde ${minimum} €/mes`;
  const description = `Compara versiones y ofertas del ${group.brand} ${group.model} para particulares, autónomos y empresas, con plazo, kilómetros e IVA visibles.`;
  const url = modelPath(group.brand, group.model);
  return { title, description, alternates: { canonical: url }, openGraph: { type: "website", title, description, url } };
}

export default async function ModelPage({ params }: Props) {
  const { marca, modelo } = await params; const group = findGroup(marca, modelo); if (!group) notFound();
  const items = vehicles.filter((vehicle) => vehicle.brand === group.brand && vehicle.model === group.model);
  const ids = new Set(items.map((vehicle) => vehicle.id)); const modelOffers = offers.filter((offer) => ids.has(offer.vehicleId));
  const listings = canonicalVehicles(items).flatMap((vehicle) => { const groupedIds = new Set(vehiclesInSameGroup(vehicle, items).map((item) => item.id)); const available = modelOffers.filter((offer) => groupedIds.has(offer.vehicleId)); const best = available.sort((a, b) => a.monthlyPrice - b.monthlyPrice)[0]; return best ? [{ vehicle, offer: best }] : []; }).sort((a, b) => a.offer.monthlyPrice - b.offer.monthlyPrice);
  const minimum = listings[0]?.offer.monthlyPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const profiles = [...new Set(modelOffers.map((offer) => audienceLabels[offer.audience]))].join(", ");
  const canonical = modelPath(group.brand, group.model);
  const faqs = [{ question: `¿Cuánto cuesta el renting del ${group.brand} ${group.model}?`, answer: minimum ? `Las cuotas publicadas en el inventario actual parten de ${minimum} €/mes. El importe cambia según perfil, versión, plazo, kilómetros e IVA.` : "No hay una cuota activa confirmada." }, { question: "¿Por qué aparecen varias versiones?", answer: "Agrupamos en esta página las motorizaciones, acabados, proveedores y tipos de cliente del mismo modelo para poder compararlos sin mezclar sus condiciones." }];
  return <main id="contenido-principal" className="mx-auto max-w-7xl px-5 py-7 sm:px-8 sm:py-10">
    <Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: group.brand, path: `/marcas/${marca}` }, { name: group.model, path: canonical }]} />
    <Schema data={[itemListSchema(`${group.brand} ${group.model}`, items), faqSchema(faqs)]} />
    <header className="border-b border-line pb-8"><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Modelo y versiones</p><h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Renting {group.brand} {group.model}</h1><p className="mt-5 max-w-3xl text-base leading-7 text-muted">Comparamos {items.length} {items.length === 1 ? "ficha activa" : "fichas activas"} y {modelOffers.length} combinaciones para {profiles}. {minimum ? `La cuota publicada más baja parte de ${minimum} €/mes.` : "Consulta disponibilidad."}</p><div className="mt-5"><SourceStatus /></div></header>
    <section className="py-12"><h2 className="font-display mb-6 text-3xl font-semibold text-ink">Versiones y ofertas disponibles</h2><VehicleGrid items={listings} /></section>
    <section className="mb-12 rounded-xl border border-line bg-surface p-6"><h2 className="font-display text-2xl font-semibold">Explora la marca</h2><Link href={`/marcas/${marca}`} className="mt-3 inline-block text-sm font-bold text-brand underline">Ver todos los modelos {group.brand}</Link></section>
    <FAQ items={faqs} />
  </main>;
}
