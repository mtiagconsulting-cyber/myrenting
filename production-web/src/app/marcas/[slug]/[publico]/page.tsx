import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { vehicles } from "@/data/vehicles";
import { audienceLabels } from "@/lib/catalog-taxonomy";
import { brandAudiencePages, brandAudiencePath, findBrandAudiencePage } from "@/lib/seo-indexability";

type Props = { params: Promise<{ slug: string; publico: string }> };

export function generateStaticParams() { return brandAudiencePages.map((page) => ({ slug: page.brandSlug, publico: page.audience })); }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug, publico } = await params;
  const page = findBrandAudiencePage(slug, publico);
  if (!page) return {};
  const profile = audienceLabels[page.audience];
  const price = page.minimumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const title = `Renting ${page.brand} para ${profile} desde ${price} €/mes`;
  const description = `${page.vehicleCount} vehículos y ${page.combinationCount} cuotas de renting ${page.brand} para ${profile}. Compara modelos, plazos, kilómetros, entrada e IVA.`;
  const url = brandAudiencePath(page);
  return { title, description, alternates: { canonical: url }, openGraph: { type: "website", title, description, url } };
}

export default async function BrandAudienceRoute({ params }: Props) {
  const { slug, publico } = await params;
  const page = findBrandAudiencePage(slug, publico);
  if (!page) notFound();
  const profile = audienceLabels[page.audience];
  const minimum = page.minimumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const maximum = page.maximumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const canonical = brandAudiencePath(page);
  const items = vehicles.filter((vehicle) => vehicle.brand === page.brand);
  const faqs = [
    { question: `¿Cuánto cuesta un ${page.brand} de renting para ${profile}?`, answer: `Las tarifas activas se sitúan actualmente entre ${minimum} y ${maximum} €/mes. El precio depende del modelo, plazo, kilometraje, entrada y tratamiento del IVA.` },
    { question: `¿Cuántos modelos ${page.brand} hay para ${profile}?`, answer: `El inventario actual reúne ${page.modelCount} ${page.modelCount === 1 ? "modelo" : "modelos"}, ${page.vehicleCount} ${page.vehicleCount === 1 ? "versión" : "versiones"} y ${page.combinationCount} configuraciones destinadas a ${profile}.` },
    { question: `¿Las cuotas ${page.brand} para ${profile} incluyen IVA?`, answer: page.audience === "particular" ? "En particulares mostramos si el IVA está incluido en el precio final de cada oferta." : "En tarifas profesionales indicamos expresamente si el IVA debe añadirse para evitar comparar importes diferentes." },
  ];
  return <SeoListingPage heading={`Renting ${page.brand} para ${profile}`} summary={`Selección actual de ${page.vehicleCount} vehículos ${page.brand}, pertenecientes a ${page.modelCount} modelos, con ${page.combinationCount} configuraciones específicas para ${profile}. Las cuotas parten de ${minimum} €/mes.`} idealFor={`Quien quiere comparar la gama de renting ${page.brand} disponible específicamente para ${profile}, sin mezclar precios de otros tipos de cliente.`} canonical={canonical} items={items} faqs={faqs} audience={page.audience} relatedLinks={[{ label: `Toda la gama ${page.brand}`, href: `/marcas/${page.brandSlug}` }, { label: `Comparar todos los coches`, href: `/coches?marca=${page.brandSlug}&publico=${page.audience}` }]} />;
}
