import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, CheckCircle2, Info } from "lucide-react";
import { FAQ } from "@/components/seo/FAQ";
import { AnswerSummary } from "@/components/seo/AnswerSummary";
import { Schema, vehicleSchema } from "@/components/seo/Schema";
import { SourceStatus } from "@/components/seo/SourceStatus";
import { VehicleDetail } from "@/components/vehicles/VehicleDetail";
import { VehicleSpecs } from "@/components/vehicles/VehicleSpecs";
import { offers } from "@/data/offers";
import { getVehicleEditorial } from "@/data/vehicle-details";
import { vehicles } from "@/data/vehicles";
import { fuelPages } from "@/lib/catalog-taxonomy";
import { contentSlug } from "@/lib/content-slug";
import { recommendVehicles } from "@/lib/recommendations";
import { canonicalVehicle, canonicalVehicles, representativeVehicle, vehicleGroupKey, vehicleModelKey, vehiclePublicPath, vehiclePublicSlug, vehiclesInSameGroup } from "@/lib/vehicle-groups";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() { return canonicalVehicles(vehicles).map((vehicle) => ({ slug: vehiclePublicSlug(vehicle) })); }

function findRequestedVehicle(slug: string) {
  return vehicles.find((item) => item.slug === slug || vehiclePublicSlug(canonicalVehicle(item, vehicles)) === slug);
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const requestedVehicle = findRequestedVehicle(slug);
  if (!requestedVehicle) return {};
  const vehicle = canonicalVehicle(requestedVehicle, vehicles);
  const groupedIds = new Set(vehiclesInSameGroup(vehicle, vehicles).map((item) => item.id));
  const offer = offers
    .filter((item) => groupedIds.has(item.vehicleId))
    .reduce<(typeof offers)[number] | undefined>((cheapest, item) => !cheapest || item.monthlyPrice < cheapest.monthlyPrice ? item : cheapest, undefined);
  const price = offer?.monthlyPrice.toLocaleString("es-ES", { minimumFractionDigits: offer.monthlyPrice % 1 ? 2 : 0, maximumFractionDigits: 2 }) ?? "--";
  const audience = offer?.audience === "autonomo" ? "autónomos" : offer?.audience === "empresa" ? "empresas" : "particulares";
  const vat = offer?.priceIncludesVat ? "IVA incluido" : "más IVA";
  const title = `${vehicle.brand} ${vehicle.model} de renting para ${audience} desde ${price} €/mes`;
  const description = `${vehicle.brand} ${vehicle.model} para ${audience} desde ${price} €/mes, ${vat}. ${offer?.duration ?? "—"} meses y ${offer?.kilometers.toLocaleString("es-ES") ?? "—"} km/año.`;
  const canonical = vehiclePublicPath(vehicle);
  return { title, description, alternates: { canonical }, openGraph: { type: "website", title, description, url: canonical, ...(vehicle.images ? { images: [{ url: vehicle.images.hero, alt: `${vehicle.brand} ${vehicle.model}` }] } : {}) } };
}

export default async function VehiclePage({ params }: Props) {
  const { slug } = await params;
  const requestedVehicle = findRequestedVehicle(slug);
  if (!requestedVehicle) notFound();
  const vehicle = canonicalVehicle(requestedVehicle, vehicles);
  const groupedVehicles = vehiclesInSameGroup(vehicle, vehicles);
  const variantGroups = new Map<string, typeof vehicles>();
  for (const item of vehicles.filter((candidate) => vehicleModelKey(candidate) === vehicleModelKey(vehicle))) {
    const key = vehicleGroupKey(item);
    variantGroups.set(key, [...(variantGroups.get(key) ?? []), item]);
  }
  const variants = [...variantGroups.values()].map(representativeVehicle);
  const groupedIds = new Set(groupedVehicles.map((item) => item.id));
  const vehicleOffers = offers.filter((item) => groupedIds.has(item.vehicleId));
  const offer = vehicleOffers.sort((a, b) => a.monthlyPrice - b.monthlyPrice)[0];
  const editorial = getVehicleEditorial(slug, `${vehicle.brand} ${vehicle.model}`, vehicle.fuel, vehicle);
  if (!offer) notFound();
  const recommended = recommendVehicles(vehicle, offer, vehicles, offers);
  const alternatives = recommended.map((item) => item.vehicle);

  return (
    <main id="contenido-principal" className="mx-auto max-w-7xl px-5 py-7 sm:px-8 sm:py-10">
      <Schema data={vehicleSchema(vehicle, vehicleOffers, offer, editorial.summary, editorial.faqs)} />
      <nav aria-label="Migas de pan" className="mb-8 flex items-center gap-2 text-xs text-muted"><Link href="/" className="hover:text-ink">Inicio</Link><span>/</span><Link href={`/renting/${contentSlug(vehicle.brand)}`} className="hover:text-ink">{vehicle.brand}</Link><span>/</span><Link href={`/renting/${contentSlug(vehicle.brand)}/${contentSlug(vehicle.model)}`} className="hover:text-ink">{vehicle.model}</Link><span>/</span><span className="truncate text-copy">{vehicle.version}</span></nav>
      <VehicleDetail vehicle={vehicle} offer={offer} offers={vehicleOffers} variants={variants} summary={editorial.summary} />

      <div className="mt-8 space-y-3">
        <AnswerSummary
          answer={`${vehicle.brand} ${vehicle.model} es ${editorial.summary.toLowerCase()} La oferta mostrada parte de ${offer.monthlyPrice} € al mes durante ${offer.duration} meses.`}
          facts={[
            { label: "Precio habitual", value: `${offer.monthlyPrice} €/mes` },
            { label: "Ideal para", value: editorial.idealFor },
            { label: "Alternativas", value: alternatives.length ? alternatives.map((item) => `${item.brand} ${item.model}`).join(", ") : "Consulta el catálogo" },
          ]}
        />
        <SourceStatus />
        <p className="text-xs leading-5 text-muted">Fuente: {offer.sourceUrl ? <a href={offer.sourceUrl} target="_blank" rel="noreferrer noopener nofollow" className="font-bold text-copy underline">oferta publicada por {offer.provider}</a> : <span className="font-semibold text-copy">documentación facilitada por {offer.provider}</span>}.{offer.verifiedAt ? <> Verificada el <time dateTime={offer.verifiedAt}>{new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "long", year: "numeric" }).format(new Date(offer.verifiedAt))}</time>.</> : null}</p>
        <nav aria-label="Explorar vehículos relacionados" className="flex flex-wrap gap-2 pt-2"><Link href={`/renting/${contentSlug(vehicle.brand)}/${contentSlug(vehicle.model)}`} className="rounded-full border border-line px-4 py-2 text-xs font-bold text-copy">Todas las versiones</Link><Link href={`/renting/${contentSlug(vehicle.brand)}`} className="rounded-full border border-line px-4 py-2 text-xs font-bold text-copy">Más {vehicle.brand}</Link><Link href={vehicle.bodyType === "SUV" ? "/renting/suv" : vehicle.bodyType === "Furgoneta" ? "/renting/furgonetas" : vehicle.bodyType === "Compacto" ? "/renting/coches-pequenos" : "/renting/familiares"} className="rounded-full border border-line px-4 py-2 text-xs font-bold text-copy">Más {vehicle.bodyType}</Link>{fuelPages.filter((page) => page.fuel === vehicle.fuel).map((page) => <Link key={page.slug} href={`/renting/${page.slug}`} className="rounded-full border border-line px-4 py-2 text-xs font-bold text-copy">Más {page.label}</Link>)}</nav>
      </div>

      <div className="mt-14 space-y-16 sm:mt-20 sm:space-y-20">
        <VehicleSpecs vehicle={vehicle} />

        <section className="grid gap-5 lg:grid-cols-2">
          <div className="rounded-xl bg-ink p-6 text-white sm:p-8"><p className="text-xs font-bold tracking-[0.1em] text-orange-400 uppercase">Ayuda para decidir</p><h2 className="font-display mt-4 text-3xl font-semibold tracking-[-0.04em]">¿Para quién es este coche?</h2><p className="mt-5 text-sm leading-7 text-slate-300">{editorial.idealFor}</p><ul className="mt-6 space-y-3">{editorial.strengths.map((strength) => <li key={strength} className="flex items-center gap-3 text-sm font-semibold"><CheckCircle2 size={17} className="text-orange-400" aria-hidden="true" />{strength}</li>)}</ul></div>
          <div id="condiciones" className="rounded-xl border border-line bg-surface p-6 sm:p-8"><div className="flex items-center gap-3 text-brand"><Info size={20} aria-hidden="true" /><p className="text-xs font-bold tracking-[0.1em] uppercase">Ten en cuenta</p></div><p className="font-display mt-5 text-2xl font-semibold tracking-[-0.035em] text-ink">{editorial.consider}</p><p className="mt-5 text-sm leading-6 text-muted">Compara siempre entrada, duración y kilómetros. Una cuota menor no implica necesariamente un coste total inferior.</p><dl className="mt-6 grid grid-cols-2 gap-4 border-t border-line pt-6"><div><dt className="text-xs text-muted">Coste total estimado</dt><dd className="font-data mt-1 font-semibold text-ink">{(offer.monthlyPrice * offer.duration + offer.initialPayment).toLocaleString("es-ES")} €</dd></div><div><dt className="text-xs text-muted">Coste por km contratado</dt><dd className="font-data mt-1 font-semibold text-ink">{((offer.monthlyPrice * offer.duration + offer.initialPayment) / (offer.kilometers * offer.duration / 12)).toLocaleString("es-ES", { maximumFractionDigits: 2 })} €</dd></div></dl></div>
        </section>

        <section aria-labelledby="alternativas"><div className="flex items-end justify-between gap-5"><div><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Alternativas por precio y uso</p><h2 id="alternativas" className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink">Otros coches que encajan</h2></div><Link href="/coches" className="hidden items-center gap-2 text-sm font-bold text-ink sm:flex">Ver todos <ArrowRight size={16} aria-hidden="true" /></Link></div><div className="mt-6 grid gap-4 sm:grid-cols-3">{recommended.map(({ vehicle: item, offer: alternativeOffer }) => <Link key={item.id} href={`${vehiclePublicPath(canonicalVehicle(item, vehicles))}?publico=${alternativeOffer.audience}`} className="group overflow-hidden rounded-xl border border-line bg-surface shadow-card transition hover:border-slate-300 hover:shadow-lg">{item.images ? <div className="relative aspect-[16/9] overflow-hidden bg-slate-100"><Image src={item.images.card} alt={`${item.brand} ${item.model}`} fill sizes="(max-width: 640px) 100vw, 33vw" className="object-cover transition duration-500 group-hover:scale-[1.025]" /></div> : <div className="grid aspect-[16/9] place-items-center bg-slate-100 px-5 text-center font-display text-xl font-semibold text-slate-500">{item.brand} {item.model}</div>}<div className="p-5"><p className="text-xs font-bold text-muted">{item.brand}</p><h3 className="font-display mt-1 text-xl font-semibold text-ink">{item.model}</h3><p className="mt-2 text-[0.6875rem] text-muted">{item.bodyType} · {item.fuel}</p><div className="mt-5 flex items-end justify-between"><p className="font-data text-xl font-semibold text-ink">{alternativeOffer.monthlyPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 })} €<span className="font-sans text-xs text-muted">/mes</span></p><ArrowRight size={17} className="transition-transform group-hover:translate-x-1" aria-hidden="true" /></div></div></Link>)}</div></section>

        <FAQ items={editorial.faqs} />
      </div>
    </main>
  );
}
