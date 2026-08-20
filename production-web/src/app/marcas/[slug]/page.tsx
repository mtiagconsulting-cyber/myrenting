import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { brands, vehicles } from "@/data/vehicles";
import { offers } from "@/data/offers";
import { contentSlug } from "@/lib/content-slug";

type Props = { params: Promise<{ slug: string }> };
const slugify = contentSlug;
export function generateStaticParams() { return brands.map((brand) => ({ slug: slugify(brand) })); }
export async function generateMetadata({ params }: Props): Promise<Metadata> { const { slug } = await params; const brand = brands.find((item) => slugify(item) === slug); if (!brand) return {}; const title=`Renting ${brand}: modelos y ofertas`;const description=`Compara modelos ${brand} de renting por cuota, condiciones, consumo y maletero.`;return { title, description, alternates: { canonical: `/marcas/${slug}` },openGraph:{type:"website",title,description,url:`/marcas/${slug}`} }; }

export default async function BrandPage({ params }: Props) {
  const { slug } = await params;
  const brand = brands.find((item) => slugify(item) === slug);
  if (!brand) notFound();
  const items = vehicles.filter((vehicle) => vehicle.brand === brand);
  const ids = new Set(items.map((vehicle) => vehicle.id));
  const brandOffers = offers.filter((offer) => ids.has(offer.vehicleId));
  const prices = brandOffers.map((offer) => offer.monthlyPrice);
  const minimum = prices.length ? Math.min(...prices).toLocaleString("es-ES", { maximumFractionDigits: 2 }) : null;
  const audiences = new Set(brandOffers.map((offer) => offer.audience));
  const profiles = [audiences.has("particular") && "particulares", audiences.has("autonomo") && "autónomos", audiences.has("empresa") && "empresas"].filter(Boolean).join(", ");
  const summary = minimum ? `Actualmente comparamos ${items.length} ${items.length === 1 ? "modelo" : "modelos"} ${brand}, con cuotas publicadas desde ${minimum} €/mes para ${profiles}. Los precios se separan por perfil, plazo, kilómetros e IVA.` : `Consulta los modelos ${brand} recopilados y compara sus condiciones de renting cuando haya cuotas activas.`;
  const faqs = [{ question: `¿Qué modelos ${brand} de renting están disponibles?`, answer: `La selección muestra los modelos ${brand} disponibles actualmente en el inventario de MyRenting.` }, { question: `¿Cómo comparar ofertas de ${brand}?`, answer: "Revisa cuota, entrada, duración, kilómetros anuales y coste total antes de decidir." }];
  return <SeoListingPage heading={`Renting ${brand}`} summary={summary} idealFor={`Personas que ya consideran ${brand} y quieren contrastar el coste completo de sus opciones de renting.`} canonical={`/marcas/${slug}`} items={items} faqs={faqs} />;
}
