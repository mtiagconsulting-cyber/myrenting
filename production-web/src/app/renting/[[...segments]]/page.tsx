import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { findSeoLanding, getLandingPairs, indexableSeoLandings, landingVehicles, offerMatchesLanding, preparedNoindexLandings, seoConsolidationDestination } from "@/lib/seo-landing-engine";
import { contentSlug } from "@/lib/content-slug";
import { generateGeoFacts } from "@/lib/geo-facts";

type Props = { params: Promise<{ segments?: string[] }> };

export function generateStaticParams() {
  return [...indexableSeoLandings, ...preparedNoindexLandings.filter((landing) => landing.type === "city")].map((landing) => ({ segments: landing.slug.replace(/^\/renting\/?/, "").split("/").filter(Boolean) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { segments } = await params;
  const landing = findSeoLanding(segments);
  if (!landing) return {};
  if (landing.type === "model") {
    const pairs = getLandingPairs(landing);
    const cheapest = [...pairs].sort((a, b) => a.offer.monthlyPrice - b.offer.monthlyPrice)[0];
    const cheapestParticular = pairs.filter(({ offer }) => offer.audience === "particular").sort((a, b) => a.offer.monthlyPrice - b.offer.monthlyPrice)[0];
    const name = `${landing.dimensions.brand} ${landing.dimensions.model}`;
    const minimum = cheapest?.offer.monthlyPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 }) ?? "—";
    const particular = cheapestParticular?.offer.monthlyPriceIncVat?.toLocaleString("es-ES", { maximumFractionDigits: 2 }) ?? cheapestParticular?.offer.monthlyPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
    const title = `Renting ${name} desde ${minimum} €/mes | ${pairs.length} ofertas`;
    const description = `Compara ${pairs.length} ofertas de renting ${name} desde ${minimum} €/mes sin IVA${particular ? ` y para particulares desde ${particular} €/mes con IVA` : ""}. Versiones, km, plazos y proveedores.`;
    return { title, description, alternates: { canonical: landing.canonical }, robots: landing.indexable ? { index: true, follow: true } : { index: false, follow: true }, openGraph: { type: "website", title, description, url: landing.canonical } };
  }
  return {
    title: landing.title,
    description: landing.description,
    alternates: { canonical: landing.canonical },
    robots: landing.indexable ? { index: true, follow: true } : { index: false, follow: true },
    openGraph: { type: "website", title: landing.title, description: landing.description, url: landing.canonical },
  };
}

export default async function ProgrammaticRentingPage({ params }: Props) {
  const { segments } = await params;
  const landing = findSeoLanding(segments);
  if (!landing) notFound();
  const consolidationDestination = seoConsolidationDestination(landing);
  if (consolidationDestination) permanentRedirect(consolidationDestination);
  const stats = landing.stats;
  const geoFacts = landing.indexable ? generateGeoFacts(landing) : null;
  const minimum = stats?.minimumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 }) ?? "—";
  const entityName = [landing.dimensions.brand, landing.dimensions.model].filter(Boolean).join(" ") || landing.h1.toLowerCase();
  const faqs = stats && geoFacts ? [
    { question: `¿Cuánto cuesta ${landing.type === "brand" || landing.type === "model" ? `un ${entityName} de renting` : landing.h1.toLowerCase()}?`, answer: `Las configuraciones publicadas van desde ${minimum} hasta ${stats.maximumPrice.toLocaleString("es-ES")} €/mes. La cuota depende del cliente, duración, kilometraje e IVA.` },
    { question: `¿Cuál es la opción más barata en ${landing.h1.toLowerCase()}?`, answer: `Actualmente, ${stats.cheapestVehicle} es la opción con menor cuota dentro de esta selección, desde ${minimum} €/mes. La vigencia y disponibilidad deben confirmarse antes de contratar.` },
    { question: "¿Cuántas ofertas y modelos hay disponibles?", answer: `El inventario actual reúne ${stats.offerCount} configuraciones correspondientes a ${stats.vehicleCount} vehículos y ${stats.modelCount} modelos.` },
    { question: "¿Hay opciones sin entrada o con entrega disponible?", answer: `${geoFacts.noEntryCount} configuraciones tienen entrada inicial de 0 € y ${geoFacts.immediateDeliveryCount} figuran como disponibles. La fecha efectiva de entrega debe confirmarse con el proveedor.` },
    { question: "¿Qué duración y kilometraje puedo contratar?", answer: `En esta selección existen plazos de ${stats.durations.join(", ")} meses y kilometrajes de ${stats.kilometers.map((value) => value.toLocaleString("es-ES")).join(", ")} km/año. No todas las combinaciones tienen el mismo precio.` },
  ] : [{ question: "¿Hay ofertas disponibles?", answer: "Todavía no existe inventario suficiente y verificable para publicar esta selección en buscadores." }];
  const brand = typeof landing.dimensions.brand === "string" ? landing.dimensions.brand : undefined;
  const model = typeof landing.dimensions.model === "string" ? landing.dimensions.model : undefined;
  const items = landing.type === "model"
    ? [...new Map(getLandingPairs(landing).map(({ vehicle }) => [vehicle.id, vehicle])).values()]
    : landingVehicles(landing);
  const baseEntityPath = model ? `/renting/${contentSlug(brand!)}/${contentSlug(model)}` : brand ? `/renting/${contentSlug(brand)}` : "/renting";
  const breadcrumbs = [{ name: "Inicio", path: "/" }, { name: "Renting", path: "/renting" }, ...(brand ? [{ name: brand, path: `/renting/${contentSlug(brand)}` }] : []), ...(model ? [{ name: model, path: baseEntityPath }] : []), ...(landing.canonical !== baseEntityPath ? [{ name: landing.h1, path: landing.canonical }] : [])];
  const contextualLinks = indexableSeoLandings.filter((candidate) => candidate.canonical !== landing.canonical && ((brand && candidate.dimensions.brand === brand && (!model || candidate.dimensions.model === model)) || (!brand && landing.dimensions.body && candidate.dimensions.body === landing.dimensions.body) || (!brand && landing.dimensions.fuel && candidate.dimensions.fuel === landing.dimensions.fuel))).slice(0, 12).map((candidate) => ({ label: candidate.h1, href: candidate.canonical }));
  return <SeoListingPage
    heading={landing.h1}
    summary={landing.summary}
    idealFor={landing.idealFor}
    canonical={landing.canonical}
    items={items}
    faqs={faqs}
    audience={landing.filters.audience}
    offerFilter={(offer) => offerMatchesLanding(offer, landing.filters)}
    stats={stats}
    landing={landing}
    geoFacts={geoFacts}
    breadcrumbs={breadcrumbs}
    relatedLinks={[...contextualLinks, { label: "Todos los coches", href: "/renting" }, { label: "Renting sin entrada", href: "/renting/sin-entrada" }, { label: "Entrega inmediata", href: "/renting/entrega-inmediata" }, { label: "Renting barato", href: "/renting/baratos" }]}
  />;
}
