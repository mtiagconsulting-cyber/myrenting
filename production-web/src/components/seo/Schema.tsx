import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";
import { absoluteUrl } from "@/lib/seo";
import { vehiclePublicPath } from "@/lib/vehicle-groups";

type JsonLd = Record<string, unknown> | Array<Record<string, unknown>>;

const organizationId = `${absoluteUrl("/")}#organization`;
const websiteId = `${absoluteUrl("/")}#website`;

export function Schema({ data }: { data: JsonLd }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }} />;
}

export function OrganizationSchema() {
  return <Schema data={{ "@context": "https://schema.org", "@graph": [{ "@type": "Organization", "@id": organizationId, name: "MyRenting", legalName: "MTIAG Consulting, S.L.", taxID: "B62559976", url: absoluteUrl("/"), logo: absoluteUrl("/icon.svg"), email: "mtiagconsulting@gmail.com", telephone: "+34691766768", contactPoint: { "@type": "ContactPoint", contactType: "Atención comercial", telephone: "+34691766768", email: "mtiagconsulting@gmail.com", availableLanguage: ["es"] }, description: "Comparador independiente de renting de coches para particulares, autónomos y empresas en España.", areaServed: { "@type": "Country", name: "España" } }, { "@type": "WebSite", "@id": websiteId, url: absoluteUrl("/"), name: "MyRenting", inLanguage: "es-ES", publisher: { "@id": organizationId }, potentialAction: { "@type": "SearchAction", target: `${absoluteUrl("/coches")}?marca={search_term_string}`, "query-input": "required name=search_term_string" } }] }} />;
}

export function editorialSchema({ type = "Article", path, title, description, datePublished, dateModified }: { type?: "Article" | "Report"; path: string; title: string; description: string; datePublished?: string; dateModified: string }) {
  const pageUrl = absoluteUrl(path);
  const webpageId = `${pageUrl}#webpage`;
  return { "@context": "https://schema.org", "@graph": [
    { "@type": "WebPage", "@id": webpageId, url: pageUrl, name: title, description, isPartOf: { "@id": websiteId }, publisher: { "@id": organizationId }, inLanguage: "es-ES" },
    { "@type": type, "@id": `${pageUrl}#${type.toLowerCase()}`, ...(type === "Article" ? { headline: title } : { name: title }), description, ...(datePublished ? { datePublished } : {}), dateModified, author: { "@id": organizationId }, publisher: { "@id": organizationId }, mainEntityOfPage: { "@id": webpageId }, inLanguage: "es-ES" },
  ] };
}

export function vehicleSchema(vehicle: Vehicle, allOffers: Offer[], offer: Offer, description: string, faqs: Array<{ question: string; answer: string }>) {
  const pagePath = vehiclePublicPath(vehicle);
  const pageUrl = absoluteUrl(pagePath);
  const imageUrl = vehicle.images ? absoluteUrl(vehicle.images.hero) : undefined;
  const webpageId = `${pageUrl}#webpage`;
  const vehicleId = `${pageUrl}#vehicle`;
  const productId = `${pageUrl}#product`;
  const prices = allOffers.map((item) => item.monthlyPrice);
  const structuredOffers = allOffers.map((item) => {
    const availability = item.availability === "Disponible" ? "https://schema.org/InStock" : item.availability === "Entrega próxima" ? "https://schema.org/PreOrder" : "https://schema.org/LimitedAvailability";
    return { "@type": "Offer", "@id": `${pageUrl}#offer-${item.id}`, price: item.monthlyPrice, priceCurrency: "EUR", url: `${pageUrl}?publico=${item.audience}`, availability, seller: { "@type": "Organization", name: item.provider }, eligibleDuration: { "@type": "QuantitativeValue", value: item.duration, unitCode: "MON" }, priceSpecification: { "@type": "UnitPriceSpecification", price: item.monthlyPrice, priceCurrency: "EUR", unitText: "mes", referenceQuantity: { "@type": "QuantitativeValue", value: 1, unitCode: "MON" } }, description: `Cuota para ${item.audience}: ${item.duration} meses, ${item.kilometers} km/año, entrada de ${item.initialPayment} €, ${item.priceIncludesVat ? "IVA incluido" : "IVA no incluido"}.` };
  });
  const technicalData = {
    ...(vehicle.power > 0 ? { vehicleEngine: { "@type": "EngineSpecification", enginePower: { "@type": "QuantitativeValue", value: vehicle.power, unitText: "CV" } } } : {}),
    ...(vehicle.trunk !== null && vehicle.trunk > 0 ? { cargoVolume: { "@type": "QuantitativeValue", value: vehicle.trunk, unitCode: "LTR" } } : {}),
    ...(vehicle.emissionsCo2Range ? { emissionsCO2: `${vehicle.emissionsCo2Range.min}–${vehicle.emissionsCo2Range.max} g/km` } : vehicle.emissionsCo2GKm !== null && vehicle.emissionsCo2GKm !== undefined ? { emissionsCO2: vehicle.emissionsCo2GKm } : {}),
  };
  return {
    "@context": "https://schema.org",
    "@graph": [
      { "@type": "WebPage", "@id": webpageId, url: pageUrl, name: `${vehicle.brand} ${vehicle.model} de renting`, isPartOf: { "@id": websiteId }, about: [{ "@id": vehicleId }, { "@id": productId }], publisher: { "@id": organizationId }, inLanguage: "es-ES" },
      { "@type": "Vehicle", "@id": vehicleId, name: `${vehicle.brand} ${vehicle.model}`, vehicleConfiguration: vehicle.version, fuelType: vehicle.fuel, ...technicalData, brand: { "@type": "Brand", name: vehicle.brand }, image: imageUrl, url: pageUrl, description, mainEntityOfPage: { "@id": webpageId } },
      { "@type": "Product", "@id": productId, name: `${vehicle.brand} ${vehicle.model} de renting`, description, image: imageUrl, sku: vehicle.id, category: "Renting de vehículos", brand: { "@type": "Brand", name: vehicle.brand }, mainEntityOfPage: { "@id": webpageId }, isRelatedTo: { "@id": vehicleId }, additionalProperty: [
        { "@type": "PropertyValue", name: "Tipo de cliente", value: offer.audience },
        { "@type": "PropertyValue", name: "Duración del contrato", value: offer.duration, unitText: "meses" },
        { "@type": "PropertyValue", name: "Kilómetros anuales", value: offer.kilometers, unitText: "km/año" },
        { "@type": "PropertyValue", name: "Entrada", value: offer.initialPayment, unitCode: "EUR" },
        { "@type": "PropertyValue", name: "Tratamiento del IVA", value: offer.priceIncludesVat ? "IVA incluido" : "IVA no incluido" },
      ], offers: { "@type": "AggregateOffer", lowPrice: Math.min(...prices), highPrice: Math.max(...prices), priceCurrency: "EUR", offerCount: allOffers.length, offers: structuredOffers } },
      breadcrumbSchema([{ name: "Inicio", path: "/" }, { name: "Coches", path: "/coches" }, { name: `${vehicle.brand} ${vehicle.model}`, path: pagePath }], false),
      { "@type": "FAQPage", "@id": `${pageUrl}#faq`, mainEntity: faqs.map((faq) => ({ "@type": "Question", name: faq.question, acceptedAnswer: { "@type": "Answer", text: faq.answer } })) },
    ],
  };
}

export function breadcrumbSchema(items: Array<{ name: string; path: string }>, includeContext = true) {
  return { ...(includeContext ? { "@context": "https://schema.org" } : {}), "@type": "BreadcrumbList", itemListElement: items.map((item, index) => ({ "@type": "ListItem", position: index + 1, name: item.name, item: absoluteUrl(item.path) })) };
}

export function itemListSchema(name: string, items: Vehicle[]) {
  return { "@context": "https://schema.org", "@type": "ItemList", name, numberOfItems: items.length, itemListElement: items.map((vehicle, index) => ({ "@type": "ListItem", position: index + 1, url: absoluteUrl(vehiclePublicPath(vehicle)), name: `${vehicle.brand} ${vehicle.model}` })) };
}

export function faqSchema(faqs: Array<{ question: string; answer: string }>) {
  return { "@context": "https://schema.org", "@type": "FAQPage", mainEntity: faqs.map((faq) => ({ "@type": "Question", name: faq.question, acceptedAnswer: { "@type": "Answer", text: faq.answer } })) };
}
