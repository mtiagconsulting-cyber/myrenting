import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Hub from "@/components/seo/Hub";
import { byCarroceria, priceRange } from "@/data/vehicles";

const MIN_MODELS = 3;

// SUV se sirve en /renting-suv (evita contenido duplicado): aquí solo el resto.
const CATS: Record<string, { title: string; label: string; ideal: string }> = {
  urbano: {
    title: "Renting de coches urbanos",
    label: "Urbanos",
    ideal: "conducción diaria en ciudad, aparcamiento fácil y bajo consumo.",
  },
  familiar: {
    title: "Renting de coches familiares",
    label: "Familiares",
    ideal: "familias que necesitan maletero amplio, espacio para 5 plazas y comodidad en viajes largos.",
  },
  furgoneta: {
    title: "Renting de furgonetas",
    label: "Furgonetas",
    ideal: "autónomos y empresas que necesitan carga, volumen y fiscalidad deducible.",
  },
};

const eligible = Object.keys(CATS).filter((slug) => byCarroceria(slug).length >= MIN_MODELS);

export function generateStaticParams() {
  return eligible.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const c = CATS[slug];
  const list = byCarroceria(slug);
  if (!c || list.length < MIN_MODELS) return {};
  const { min } = priceRange(list);
  return {
    title: `${c.title} — ${list.length} modelos comparados`,
    description: `Compara ${list.length} ${c.label.toLowerCase()} en renting desde ${min} €/mes. Cuota real por km y plazo, seguro y mantenimiento incluidos, sin entrada.`,
    alternates: { canonical: `/categorias/${slug}` },
  };
}

export default async function CategoriaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const c = CATS[slug];
  const list = byCarroceria(slug);
  if (!c || list.length < MIN_MODELS) notFound();
  const { min, max } = priceRange(list);

  return (
    <Hub
      canonicalPath={`/categorias/${slug}`}
      crumbs={[{ name: "Coches", href: "/coches" }, { name: c.label }]}
      title={c.title}
      intro={`Comparamos ${list.length} ${c.label.toLowerCase()} en renting de gestoras oficiales, con la cuota real según kilómetros y plazo, seguro y mantenimiento incluidos y sin entrada.`}
      vehicles={list}
      summary={[
        { label: "Modelos comparados", value: String(list.length) },
        { label: "Cuota desde", value: `${min} €/mes` },
        { label: "Rango de precio", value: `${min}–${max} €/mes` },
        { label: "Entrada", value: "0 €" },
      ]}
      idealFor={c.ideal}
      faq={[
        { q: `¿Cuánto cuesta un ${c.label.toLowerCase().replace(/s$/, "")} en renting?`, a: `En nuestra comparativa arrancan desde ${min} €/mes, con seguro y mantenimiento incluidos y sin entrada.` },
        { q: "¿Qué incluye la cuota?", a: "Seguro a todo riesgo, mantenimiento y averías, neumáticos, impuestos, asistencia en carretera y gestión de multas. No incluye combustible ni recarga." },
      ]}
    />
  );
}
