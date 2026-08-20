import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { audienceLabels } from "@/lib/catalog-taxonomy";
import type { OfferAudience } from "@/types/offer";
import type { BodyType } from "@/types/vehicle";

const audiences: OfferAudience[] = ["particular", "autonomo", "empresa"];
const categories: Array<{ slug: string; name: string; body?: BodyType; bodies?: BodyType[] }> = [{ slug: "suv", name: "SUV", body: "SUV" }, { slug: "familiares", name: "familiares", bodies: ["SUV", "Familiar", "Furgoneta"] }, { slug: "urbanos", name: "urbanos y compactos", body: "Compacto" }, { slug: "berlinas", name: "berlinas", body: "Berlina" }, { slug: "empresas", name: "coches", bodies: ["SUV", "Familiar", "Furgoneta", "Compacto", "Berlina"] }];
type Props = { params: Promise<{ slug: string; publico: string }> };
export function generateStaticParams() { return categories.flatMap(({ slug }) => audiences.map((publico) => ({ slug, publico }))); }

export async function generateMetadata({ params }: Props): Promise<Metadata> { const { slug, publico } = await params; const category = categories.find((item) => item.slug === slug); if (!category || !audiences.includes(publico as OfferAudience)) return {}; const audience = publico as OfferAudience; const title = `Renting de ${category.name} para ${audienceLabels[audience]}`; const description = `Compara ${category.name} de renting para ${audienceLabels[audience]} con cuota, plazo, kilómetros e IVA claramente indicados.`; const url = `/categorias/${slug}/${publico}`; return { title, description, alternates: { canonical: url }, openGraph: { type: "website", title, description, url } }; }

export default async function AudienceCategoryPage({ params }: Props) {
  const { slug, publico } = await params; const category = categories.find((item) => item.slug === slug); if (!category || !audiences.includes(publico as OfferAudience)) notFound(); const audience = publico as OfferAudience;
  const availableIds = new Set(offers.filter((offer) => offer.audience === audience).map((offer) => offer.vehicleId));
  const items = vehicles.filter((vehicle) => availableIds.has(vehicle.id) && (category.body ? vehicle.bodyType === category.body : category.bodies?.includes(vehicle.bodyType)));
  const profile = audienceLabels[audience]; const heading = `Renting de ${category.name} para ${profile}`;
  const summary = `${items.length} vehículos con ofertas activas para ${profile}. Las cuotas se muestran con su tratamiento de IVA, duración, kilometraje y entrada para poder compararlas con el mismo criterio.`;
  const faqs = [{ question: `¿Cómo se muestran los precios para ${profile}?`, answer: audience === "particular" ? "Las cuotas para particulares se identifican con IVA incluido cuando así consta en la fuente." : "Las cuotas profesionales indican expresamente si deben sumarse el IVA, para no compararlas como si fueran precios finales." }, { question: `¿Qué condiciones debo igualar al comparar ${category.name}?`, answer: "Compara el mismo plazo, kilómetros anuales, entrada y coberturas; después revisa el coste total del contrato." }];
  return <SeoListingPage heading={heading} summary={summary} idealFor={`Quien busca ${category.name} específicamente como ${audience === "particular" ? "cliente particular" : audience === "autonomo" ? "profesional autónomo" : "empresa"}, sin mezclar cuotas de otros perfiles.`} canonical={`/categorias/${slug}/${publico}`} items={items} faqs={faqs} audience={audience} />;
}
