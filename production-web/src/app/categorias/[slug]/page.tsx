import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { vehicles } from "@/data/vehicles";
import type { BodyType } from "@/types/vehicle";
import { audienceLabels } from "@/lib/catalog-taxonomy";
import type { OfferAudience } from "@/types/offer";

type Props = { params: Promise<{ slug: string }> };
const categories: Array<{ slug: string; name: string; body?: BodyType; bodies?: BodyType[] }> = [{ slug: "suv", name: "SUV", body: "SUV" }, { slug: "familiares", name: "Familiares", bodies: ["SUV", "Familiar", "Furgoneta"] }, { slug: "urbanos", name: "Urbanos y compactos", body: "Compacto" }, { slug: "berlinas", name: "Berlinas", body: "Berlina" }, { slug: "empresas", name: "Coches para empresas" }];
export function generateStaticParams() { return categories.map(({ slug }) => ({ slug })); }
export async function generateMetadata({ params }: Props): Promise<Metadata> { const { slug } = await params; const category = categories.find((item) => item.slug === slug); if (!category) return {}; const title=`Renting de coches ${category.name}`;const description=`Compara coches ${category.name.toLowerCase()} de renting por precio y condiciones.`;return { title, description, alternates: { canonical: `/categorias/${slug}` },openGraph:{type:"website",title,description,url:`/categorias/${slug}`} }; }

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params;
  const category = categories.find((item) => item.slug === slug);
  if (!category) notFound();
  const items = category.body ? vehicles.filter((vehicle) => vehicle.bodyType === category.body) : category.bodies ? vehicles.filter((vehicle) => category.bodies?.includes(vehicle.bodyType)) : vehicles;
  const relatedLinks=(["particular","autonomo","empresa"] as OfferAudience[]).map((audience)=>({label:`Para ${audienceLabels[audience]}`,href:`/categorias/${slug}/${audience}`}));
  const faqs = [{ question: `¿Qué caracteriza a los coches ${category.name.toLowerCase()}?`, answer: "Cada ficha muestra tamaño de maletero, motor, consumo y condiciones para valorar si encaja con tu uso." }, { question: "¿Cómo comparar las cuotas?", answer: "Compara siempre con la misma duración, kilometraje y entrada, y revisa el coste total del contrato." }];
  return <SeoListingPage heading={`Renting de ${category.name.toLowerCase()}`} summary={`Selección de coches ${category.name.toLowerCase()} con sus principales datos y condiciones de renting visibles.`} idealFor={`Quien prioriza una carrocería ${category.name.toLowerCase()} y necesita comparar las diferencias económicas y prácticas entre modelos.`} canonical={`/categorias/${slug}`} items={items} faqs={faqs} relatedLinks={relatedLinks} />;
}
