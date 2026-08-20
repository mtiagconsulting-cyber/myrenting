import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { vehicles } from "@/data/vehicles";
import { fuelPages } from "@/lib/catalog-taxonomy";

type Props = { params: Promise<{ slug: string }> };
export function generateStaticParams() { return fuelPages.map(({ slug }) => ({ slug })); }
export async function generateMetadata({ params }: Props): Promise<Metadata> { const { slug } = await params; const page = fuelPages.find((item) => item.slug === slug); if (!page) return {}; const title = `Renting de coches ${page.label}`; const description = `Compara coches ${page.label} de renting con precios, perfiles, plazo, kilómetros, IVA y datos técnicos visibles.`; const url = `/combustibles/${slug}`; return { title, description, alternates: { canonical: url }, openGraph: { type: "website", title, description, url } }; }
export default async function FuelPage({ params }: Props) { const { slug } = await params; const page = fuelPages.find((item) => item.slug === slug); if (!page) notFound(); const items = vehicles.filter((vehicle) => vehicle.fuel === page.fuel); const faqs = [{ question: `¿Cuántos coches ${page.label} se comparan?`, answer: `El inventario actual contiene ${items.length} vehículos ${page.label}. La cifra se actualiza al importar nuevas ofertas.` }, { question: "¿Cómo comparo el coste?", answer: "Iguala perfil, plazo, kilómetros, entrada e IVA. En eléctricos, revisa además autonomía y consumo cuando la fuente los facilite." }]; return <SeoListingPage heading={`Renting de coches ${page.label}`} summary={`${items.length} vehículos ${page.label} disponibles en el inventario actual, con sus cuotas y condiciones separadas por tipo de cliente.`} idealFor={`Quien ya ha decidido priorizar una motorización ${page.label} y quiere comparar la oferta disponible con criterios homogéneos.`} canonical={`/combustibles/${slug}`} items={items} faqs={faqs} />; }
