import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { findSeoLanding, getLandingPairs, indexableSeoLandings, landingVehicles, offerMatchesLanding, preparedNoindexLandings, seoConsolidationDestination } from "@/lib/seo-landing-engine";
import { contentSlug } from "@/lib/content-slug";
import { generateGeoFacts } from "@/lib/geo-facts";
import { formatMonthlyPrice } from "@/lib/offer-pricing";

type Props = { params: Promise<{ segments?: string[] }> };

const priorityLandingCopy: Record<string, {
  title: (minimumExVat: string) => string;
  description: (offerCount: number, minimumExVat: string, minimumIncVat: string) => string;
  summary: (offerCount: number, modelCount: number, minimumExVat: string, minimumIncVat: string) => string;
  faqs: Array<{ question: string; answer: (minimumExVat: string, minimumIncVat: string) => string }>;
  links: Array<{ label: string; href: string }>;
}> = {
  "/renting": {
    title: (price) => `Renting coches desde ${price} €/mes | Comparador`,
    description: (offers, price, vat) => `Compara ${offers} ofertas de renting de coches desde ${price} €/mes sin IVA y ${vat} €/mes con IVA. Filtra por modelo, cuota, plazo y kilómetros.`,
    summary: (offers, models, price, vat) => `Compara ${offers} ofertas activas de ${models} modelos de coches de renting. Consulta cuotas desde ${price} €/mes sin IVA y ${vat} €/mes con IVA, sin mezclar condiciones distintas.`,
    faqs: [
      { question: "¿Cómo comparar coches de renting?", answer: () => "Compara siempre el mismo perfil de cliente, duración, kilometraje, entrada e IVA. Después revisa la versión, disponibilidad y servicios incluidos por el proveedor." },
      { question: "¿Las cuotas de renting incluyen IVA?", answer: (price, vat) => `Mostramos ambos importes para evitar confusiones: la oferta más baja parte de ${price} €/mes sin IVA y ${vat} €/mes con IVA.` },
    ],
    links: [{ label: "Renting Kia Niro", href: "/renting/kia/niro" }, { label: "Renting Peugeot 208", href: "/renting/peugeot/208" }, { label: "Renting SUV", href: "/renting/suv" }, { label: "Guía de renting barato", href: "/blog/renting-barato-2026.html" }],
  },
  "/renting/kia/niro": {
    title: (price) => `Renting Kia Niro desde ${price} €/mes sin entrada`,
    description: (offers, price, vat) => `Compara ${offers} ofertas de renting Kia Niro híbrido desde ${price} €/mes sin IVA y ${vat} €/mes con IVA. Versiones, plazo, km y disponibilidad.`,
    summary: (offers, _models, price, vat) => `Compara ${offers} ofertas activas del Kia Niro, con motorizaciones y condiciones diferenciadas. Precios desde ${price} €/mes sin IVA y ${vat} €/mes con IVA; revisa versión, plazo, kilómetros y entrada.`,
    faqs: [
      { question: "¿Qué Kia Niro de renting estoy comparando?", answer: () => "Cada oferta identifica su versión, motorización, potencia y cambio cuando el proveedor los ha confirmado. Las variantes diferentes se mantienen separadas para no mezclar precios." },
      { question: "¿Hay Kia Niro de renting sin entrada?", answer: () => "La entrada figura en cada condición publicada. Usa el importe inicial junto con la cuota, plazo y kilometraje para comparar el coste real entre ofertas." },
    ],
    links: [{ label: "Renting de coches híbridos", href: "/renting/hibridos" }, { label: "Renting SUV", href: "/renting/suv" }, { label: "Todos los Kia", href: "/renting/kia" }],
  },
  "/renting/peugeot/208": {
    title: (price) => `Renting Peugeot 208 desde ${price} €/mes | Ofertas`,
    description: (offers, price, vat) => `Compara ${offers} ofertas de renting Peugeot 208 desde ${price} €/mes sin IVA y ${vat} €/mes con IVA. Consulta versión, cambio, plazo, km y entrada.`,
    summary: (offers, _models, price, vat) => `Compara ${offers} ofertas activas del Peugeot 208 sin duplicar el mismo modelo en el listado. Precios desde ${price} €/mes sin IVA y ${vat} €/mes con IVA, con versión y condiciones visibles.`,
    faqs: [
      { question: "¿Por qué cambia el precio del Peugeot 208 de renting?", answer: () => "La cuota puede cambiar por versión, perfil de cliente, plazo, kilometraje, entrada, IVA y proveedor. Compara esas condiciones antes de elegir la oferta más baja." },
      { question: "¿El Peugeot 208 aparece duplicado?", answer: () => "El listado muestra una sola tarjeta por modelo y conserva dentro de su página las ofertas o motorizaciones realmente distintas para poder compararlas." },
    ],
    links: [{ label: "Coches de renting baratos", href: "/renting/baratos" }, { label: "Guía de renting barato", href: "/blog/renting-barato-2026.html" }, { label: "Todos los Peugeot", href: "/renting/peugeot" }],
  },
  "/renting/suv": {
    title: (price) => `Renting SUV desde ${price} €/mes | Ofertas 2026`,
    description: (offers, price, vat) => `Compara ${offers} ofertas de renting SUV desde ${price} €/mes sin IVA y ${vat} €/mes con IVA. Híbridos, gasolina y eléctricos por cuota y tamaño.`,
    summary: (offers, models, price, vat) => `Compara ${offers} ofertas activas de ${models} modelos SUV de renting. Precios desde ${price} €/mes sin IVA y ${vat} €/mes con IVA, con combustible, plazo, kilómetros y entrada visibles.`,
    faqs: [
      { question: "¿Qué SUV de renting conviene para ciudad?", answer: () => "Para ciudad suele interesar comparar tamaño, consumo y etiqueta ambiental. Un SUV híbrido o eléctrico puede encajar mejor si tienes acceso a carga o restricciones de circulación." },
      { question: "¿Cómo encontrar un SUV de renting barato?", answer: () => "Ordena por cuota y comprueba que las ofertas tengan el mismo IVA, entrada, duración y kilometraje. Revisa también combustible, maletero y disponibilidad." },
    ],
    links: [{ label: "Mejores SUV de renting", href: "/blog/mejores-suv-renting-2026.html" }, { label: "Renting Kia Niro", href: "/renting/kia/niro" }, { label: "SUV híbridos", href: "/renting/hibridos" }],
  },
};

export function generateStaticParams() {
  return [...indexableSeoLandings, ...preparedNoindexLandings.filter((landing) => landing.type === "city")].map((landing) => ({ segments: landing.slug.replace(/^\/renting\/?/, "").split("/").filter(Boolean) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { segments } = await params;
  const landing = findSeoLanding(segments);
  if (!landing) return {};
  const priority = priorityLandingCopy[landing.canonical];
  if (priority && landing.stats) {
    const minimumExVat = formatMonthlyPrice(landing.stats.minimumPriceExVat);
    const minimumIncVat = formatMonthlyPrice(landing.stats.minimumPriceIncVat);
    const title = priority.title(minimumExVat);
    const description = priority.description(landing.stats.offerCount, minimumExVat, minimumIncVat);
    return { title, description, alternates: { canonical: landing.canonical }, robots: landing.indexable ? { index: true, follow: true } : { index: false, follow: true }, openGraph: { type: "website", title, description, url: landing.canonical } };
  }
  if (landing.type === "model") {
    const pairs = getLandingPairs(landing);
    const name = `${landing.dimensions.brand} ${landing.dimensions.model}`;
    const minimumExVat = landing.stats ? formatMonthlyPrice(landing.stats.minimumPriceExVat) : "—";
    const minimumIncVat = landing.stats ? formatMonthlyPrice(landing.stats.minimumPriceIncVat) : "—";
    const title = `Renting ${name} desde ${minimumExVat} €/mes sin IVA`;
    const description = `Compara ${pairs.length} ofertas de renting ${name}: desde ${minimumExVat} €/mes sin IVA y ${minimumIncVat} €/mes con IVA. Versiones, plazos, km y proveedores.`;
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
  const minimum = stats ? formatMonthlyPrice(stats.minimumPriceExVat) : "—";
  const minimumWithVat = stats ? formatMonthlyPrice(stats.minimumPriceIncVat) : "—";
  const entityName = [landing.dimensions.brand, landing.dimensions.model].filter(Boolean).join(" ") || landing.h1.toLowerCase();
  const priority = priorityLandingCopy[landing.canonical];
  const priorityFaqs = priority ? priority.faqs.map((faq) => ({ question: faq.question, answer: faq.answer(minimum, minimumWithVat) })) : [];
  const faqs = stats && geoFacts ? [
    { question: `¿Cuánto cuesta ${landing.type === "brand" || landing.type === "model" ? `un ${entityName} de renting` : landing.h1.toLowerCase()}?`, answer: `Las ofertas parten de ${minimum} €/mes sin IVA y ${minimumWithVat} €/mes con IVA. La cuota depende del cliente, duración, kilometraje y entrada.` },
    { question: `¿Cuál es la opción más barata en ${landing.h1.toLowerCase()}?`, answer: `Actualmente, ${stats.cheapestVehicle} es la opción con menor cuota dentro de esta selección, desde ${minimum} €/mes. La vigencia y disponibilidad deben confirmarse antes de contratar.` },
    { question: "¿Cuántas ofertas, modelos y proveedores hay disponibles?", answer: `El inventario actual reúne ${stats.offerCount} ofertas correspondientes a ${stats.vehicleCount} vehículos, ${stats.modelCount} modelos y ${stats.providers.length} proveedores.` },
    { question: "¿Hay opciones sin entrada o con entrega disponible?", answer: `${geoFacts.noEntryCount} configuraciones tienen entrada inicial de 0 € y ${geoFacts.immediateDeliveryCount} figuran como disponibles. La fecha efectiva de entrega debe confirmarse con el proveedor.` },
    { question: "¿Qué duración y kilometraje puedo contratar?", answer: `En esta selección existen plazos de ${stats.durations.join(", ")} meses y kilometrajes de ${stats.kilometers.map((value) => value.toLocaleString("es-ES")).join(", ")} km/año. No todas las combinaciones tienen el mismo precio.` },
    ...priorityFaqs,
  ] : [{ question: "¿Hay ofertas disponibles?", answer: "Todavía no existe inventario suficiente y verificable para publicar esta selección en buscadores." }];
  const brand = typeof landing.dimensions.brand === "string" ? landing.dimensions.brand : undefined;
  const model = typeof landing.dimensions.model === "string" ? landing.dimensions.model : undefined;
  const items = landing.type === "model"
    ? [...new Map(getLandingPairs(landing).map(({ vehicle }) => [vehicle.id, vehicle])).values()]
    : landingVehicles(landing);
  const baseEntityPath = model ? `/renting/${contentSlug(brand!)}/${contentSlug(model)}` : brand ? `/renting/${contentSlug(brand)}` : "/renting";
  const breadcrumbs = [{ name: "Inicio", path: "/" }, { name: "Renting", path: "/renting" }, ...(brand ? [{ name: brand, path: `/renting/${contentSlug(brand)}` }] : []), ...(model ? [{ name: model, path: baseEntityPath }] : []), ...(landing.canonical !== baseEntityPath ? [{ name: landing.h1, path: landing.canonical }] : [])];
  const opportunityPaths = ["/renting/kia/niro", "/renting/peugeot/208", "/renting/bmw/serie-1", "/renting/hyundai/tucson", "/renting/volkswagen/t-roc", "/renting/nissan/qashqai", "/renting/baratos", "/renting/hibridos"];
  const contextualLinks = indexableSeoLandings.filter((candidate) => candidate.canonical !== landing.canonical && ((brand && candidate.dimensions.brand === brand && (!model || candidate.type === "model")) || (!brand && landing.dimensions.body && candidate.dimensions.body === landing.dimensions.body) || (!brand && landing.dimensions.fuel && candidate.dimensions.fuel === landing.dimensions.fuel) || (landing.type === "root" && opportunityPaths.includes(candidate.canonical)))).slice(0, 12).map((candidate) => ({ label: candidate.h1, href: candidate.canonical }));
  return <SeoListingPage
    heading={landing.h1}
    summary={priority && stats ? priority.summary(stats.offerCount, stats.modelCount, minimum, minimumWithVat) : landing.summary}
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
    relatedLinks={[...(priority?.links ?? []), ...contextualLinks, { label: "Todos los coches", href: "/renting" }, { label: "Renting sin entrada", href: "/renting/sin-entrada" }, { label: "Entrega inmediata", href: "/renting/entrega-inmediata" }, { label: "Renting barato", href: "/renting/baratos" }]}
  />;
}
