import { Breadcrumb } from "@/components/seo/Breadcrumb";
import { FAQ } from "@/components/seo/FAQ";
import { Schema, faqSchema, itemListSchema } from "@/components/seo/Schema";
import { SourceStatus } from "@/components/seo/SourceStatus";
import { GeoComparisonTable, GeoRanking, KeyFacts, ModelOfferComparison, QuickAnswer, type ModelOfferRow } from "@/components/seo/GeoAnswerBlocks";
import { VehicleGrid } from "@/components/vehicles/VehicleGrid";
import { offers } from "@/data/offers";
import type { Vehicle } from "@/types/vehicle";
import type { Offer, OfferAudience } from "@/types/offer";
import { canonicalVehicles, vehiclesInSameGroup } from "@/lib/vehicle-groups";
import type { BreadcrumbItem } from "@/components/seo/Breadcrumb";
import type { SeoLandingStats } from "@/lib/seo-landing-engine";
import type { SeoLanding } from "@/lib/seo-landing-engine";
import type { GeoFacts } from "@/lib/geo-facts";
import { inventoryUpdatedAt } from "@/data/offers";

interface Props {
  heading: string;
  summary: string;
  idealFor: string;
  canonical: string;
  items: Vehicle[];
  faqs: Array<{ question: string; answer: string }>;
  audience?: OfferAudience;
  offerFilter?: (offer: Offer) => boolean;
  relatedLinks?: Array<{ label: string; href: string }>;
  breadcrumbs?: BreadcrumbItem[];
  stats?: SeoLandingStats | null;
  landing?: SeoLanding;
  geoFacts?: GeoFacts | null;
}

export function SeoListingPage({ heading, summary, idealFor, canonical, items, faqs, audience, offerFilter, relatedLinks = [], breadcrumbs, stats, landing, geoFacts }: Props) {
  const listings = canonicalVehicles(items).flatMap((vehicle) => {
    const groupedIds = new Set(vehiclesInSameGroup(vehicle, items).map((item) => item.id));
    const offer = offers.filter((item) => groupedIds.has(item.vehicleId) && (!audience || item.audience === audience) && (!offerFilter || offerFilter(item))).sort((a, b) => a.monthlyPrice - b.monthlyPrice)[0];
    return offer ? [{ vehicle, offer }] : [];
  });
  const prices = listings.map(({ offer }) => offer.monthlyPrice);
  const modelOfferRows = (() => {
    if (landing?.type !== "model") return [];
    const rows: ModelOfferRow[] = [];
    for (const vehicle of items) {
      for (const profile of ["particular", "autonomo", "empresa"] as const) {
        const offer = offers.filter((item) => item.vehicleId === vehicle.id && item.audience === profile && (!offerFilter || offerFilter(item))).sort((a, b) => a.monthlyPrice - b.monthlyPrice)[0];
        if (offer) rows.push({ vehicle, offer });
      }
    }
    return rows.sort((first, second) => first.offer.monthlyPrice - second.offer.monthlyPrice);
  })();

  return (
    <main id="contenido-principal" className="mx-auto max-w-7xl px-5 py-7 sm:px-8 sm:py-10">
      <Breadcrumb items={breadcrumbs ?? [{ name: "Inicio", path: "/" }, { name: heading, path: canonical }]} />
      <Schema data={[itemListSchema(heading, listings.map(({ vehicle }) => vehicle)), faqSchema(faqs)]} />
      <section className="border-b border-line pb-8">
        <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Guía y ofertas</p>
        <h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">{heading}</h1>
        <p className="mt-5 max-w-3xl text-base leading-7 text-muted">{summary}</p>
        {landing && geoFacts ? <QuickAnswer landing={landing} facts={geoFacts} /> : null}
        <dl className="mt-7 grid max-w-2xl grid-cols-2 gap-4 sm:grid-cols-3">
          <div><dt className="text-xs text-muted">Ofertas disponibles</dt><dd className="font-data mt-1 text-xl font-semibold text-ink">{listings.length}</dd></div>
          <div><dt className="text-xs text-muted">Precio habitual</dt><dd className="font-data mt-1 text-xl font-semibold text-ink">{prices.length ? `${Math.min(...prices)}–${Math.max(...prices)} €` : "Sin ofertas"}</dd></div>
          <div className="col-span-2 sm:col-span-1"><dt className="text-xs text-muted">Ofertas actualizadas</dt><dd className="mt-1 text-sm font-bold text-ink"><time dateTime={inventoryUpdatedAt}>{new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "long", year: "numeric" }).format(new Date(inventoryUpdatedAt))}</time></dd></div>
        </dl>
        <div className="mt-6"><SourceStatus /></div>
        {stats ? <dl className="mt-7 grid gap-3 border-t border-line pt-6 sm:grid-cols-2 lg:grid-cols-4">
          <div><dt className="text-[0.625rem] font-bold tracking-wide text-muted uppercase">Oferta más barata</dt><dd className="mt-1 text-sm font-bold text-ink">{stats.cheapestVehicle}</dd></div>
          <div><dt className="text-[0.625rem] font-bold tracking-wide text-muted uppercase">Duraciones</dt><dd className="font-data mt-1 text-sm font-semibold text-ink">{stats.durations.map((value) => `${value} meses`).join(", ")}</dd></div>
          <div><dt className="text-[0.625rem] font-bold tracking-wide text-muted uppercase">Kilometrajes</dt><dd className="font-data mt-1 text-sm font-semibold text-ink">{stats.kilometers.map((value) => `${value.toLocaleString("es-ES")} km`).join(", ")}</dd></div>
          <div><dt className="text-[0.625rem] font-bold tracking-wide text-muted uppercase">Tecnologías</dt><dd className="mt-1 text-sm font-bold text-ink">{stats.fuels.join(", ")}</dd></div>
        </dl> : null}
        {relatedLinks.length ? <nav aria-label="Explorar esta selección" className="mt-6 flex flex-wrap gap-2">{relatedLinks.map((link) => <a key={link.href} href={link.href} className="rounded-full border border-line bg-surface px-4 py-2 text-xs font-bold text-copy hover:border-slate-300 hover:text-ink">{link.label}</a>)}</nav> : null}
        {geoFacts ? <KeyFacts facts={geoFacts} /> : null}
      </section>
      <section className="py-12">
        <div className="mb-6"><h2 className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Ofertas para comparar</h2><p className="mt-2 text-xs text-muted">Inventario recopilado de fuentes de proveedor y separado por tipo de cliente.</p></div>
        <VehicleGrid items={listings} />
      </section>
      {landing?.type === "model" && modelOfferRows.length ? <ModelOfferComparison brand={String(landing.dimensions.brand)} model={String(landing.dimensions.model)} rows={modelOfferRows} /> : geoFacts ? <GeoComparisonTable facts={geoFacts} /> : null}
      {landing?.type !== "model" && geoFacts ? <GeoRanking facts={geoFacts} heading={heading} /> : null}
      <section className="mb-14 grid gap-5 rounded-xl bg-ink p-6 text-white sm:p-8 lg:grid-cols-[0.45fr_1fr]"><p className="text-xs font-bold tracking-[0.1em] text-orange-400 uppercase">Ideal para</p><p className="font-display text-2xl font-semibold tracking-[-0.035em]">{idealFor}</p></section>
      <FAQ items={faqs} />
    </main>
  );
}
