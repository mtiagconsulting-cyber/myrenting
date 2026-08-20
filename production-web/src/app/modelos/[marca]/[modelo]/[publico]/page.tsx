import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { vehicles } from "@/data/vehicles";
import { audienceLabels, modelPath } from "@/lib/catalog-taxonomy";
import { findModelAudiencePage, modelAudiencePages, modelAudiencePath } from "@/lib/seo-indexability";

type Props = { params: Promise<{ marca: string; modelo: string; publico: string }> };

export function generateStaticParams() {
  return modelAudiencePages.map((page) => ({ marca: page.brandSlug, modelo: page.modelSlug, publico: page.audience }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { marca, modelo, publico } = await params;
  const page = findModelAudiencePage(marca, modelo, publico);
  if (!page) return {};
  const profile = audienceLabels[page.audience];
  const price = page.minimumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const title = `Renting ${page.brand} ${page.model} para ${profile} desde ${price} €/mes`;
  const description = `${page.combinationCount} cuotas de renting del ${page.brand} ${page.model} para ${profile}, desde ${price} €/mes. Compara versiones, plazos, kilómetros, entrada e IVA.`;
  const url = modelAudiencePath(page);
  return { title, description, alternates: { canonical: url }, openGraph: { type: "website", title, description, url } };
}

export default async function ModelAudienceRoute({ params }: Props) {
  const { marca, modelo, publico } = await params;
  const page = findModelAudiencePage(marca, modelo, publico);
  if (!page) notFound();
  const profile = audienceLabels[page.audience];
  const items = vehicles.filter((vehicle) => vehicle.brand === page.brand && vehicle.model === page.model);
  const minimum = page.minimumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const maximum = page.maximumPrice.toLocaleString("es-ES", { maximumFractionDigits: 2 });
  const canonical = modelAudiencePath(page);
  const faqs = [
    { question: `¿Cuánto cuesta el renting del ${page.brand} ${page.model} para ${profile}?`, answer: `Las ${page.combinationCount} configuraciones activas para ${profile} se sitúan actualmente entre ${minimum} y ${maximum} €/mes. El importe exacto depende de versión, plazo, kilómetros, entrada e IVA.` },
    { question: `¿Qué versiones del ${page.brand} ${page.model} pueden contratar los ${profile}?`, answer: `Actualmente comparamos ${page.vehicleCount} ${page.vehicleCount === 1 ? "versión" : "versiones"} con tarifa específica para ${profile}. La disponibilidad final debe confirmarse con el proveedor.` },
    { question: "¿Cómo se compara correctamente una cuota de renting?", answer: "Deben coincidir el tipo de cliente, el tratamiento del IVA, la duración, los kilómetros anuales, la entrada y las coberturas incluidas." },
  ];
  return <SeoListingPage
    heading={`Renting ${page.brand} ${page.model} para ${profile}`}
    summary={`Comparamos ${page.combinationCount} configuraciones activas y ${page.vehicleCount} ${page.vehicleCount === 1 ? "versión" : "versiones"} del ${page.brand} ${page.model} con tarifa específica para ${profile}. Las cuotas publicadas parten de ${minimum} €/mes y muestran plazo, kilometraje, entrada e IVA.`}
    idealFor={`Quien busca específicamente un ${page.brand} ${page.model} como ${page.audience === "particular" ? "cliente particular" : page.audience === "autonomo" ? "profesional autónomo" : "empresa"}, sin mezclar precios destinados a otros perfiles.`}
    canonical={canonical}
    items={items}
    faqs={faqs}
    audience={page.audience}
    relatedLinks={[{ label: `Todas las ofertas ${page.brand} ${page.model}`, href: modelPath(page.brand, page.model) }, { label: `Todos los ${page.brand}`, href: `/marcas/${page.brandSlug}` }]}
  />;
}
