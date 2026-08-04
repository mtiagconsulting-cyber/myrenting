import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Hub from "@/components/seo/Hub";
import { brands, getBrand } from "@/data/brands";

const MIN_MODELS = 3; // quality gate: sin páginas thin

const eligible = brands.filter((b) => b.count >= MIN_MODELS);

export function generateStaticParams() {
  return eligible.map((b) => ({ slug: b.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const b = getBrand(slug);
  if (!b) return {};
  return {
    title: `Renting ${b.name} — ${b.count} modelos comparados`,
    description: `Compara ${b.count} modelos de renting de ${b.name} desde ${b.desde} €/mes. Cuota real por km y plazo, seguro y mantenimiento incluidos, sin entrada.`,
    alternates: { canonical: `/marcas/${b.slug}` },
  };
}

export default async function MarcaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const b = getBrand(slug);
  if (!b || b.count < MIN_MODELS) notFound();
  const max = Math.max(...b.vehicles.map((v) => v.precio));

  return (
    <Hub
      canonicalPath={`/marcas/${b.slug}`}
      crumbs={[{ name: "Marcas", href: "/marcas" }, { name: b.name }]}
      title={`Renting ${b.name}`}
      intro={`Comparamos ${b.count} modelos de ${b.name} en renting de gestoras oficiales, con la cuota real según kilómetros y plazo, seguro y mantenimiento incluidos y sin entrada.`}
      vehicles={b.vehicles}
      summary={[
        { label: "Modelos comparados", value: String(b.count) },
        { label: "Cuota desde", value: `${b.desde} €/mes` },
        { label: "Rango de precio", value: `${b.desde}–${max} €/mes` },
        { label: "Entrada", value: "0 €" },
      ]}
      idealFor={`quienes tienen clara la marca ${b.name} y quieren comparar sus modelos por cuota, etiqueta y equipamiento en un solo lugar.`}
      faq={[
        { q: `¿Cuánto cuesta un ${b.name} en renting?`, a: `Los modelos de ${b.name} en nuestra comparativa arrancan desde ${b.desde} €/mes, con seguro y mantenimiento incluidos y sin entrada. La cuota exacta depende de los kilómetros y el plazo.` },
        { q: "¿Qué incluye la cuota?", a: "Seguro a todo riesgo, mantenimiento y averías, neumáticos, impuestos, asistencia en carretera y gestión de multas. No incluye combustible ni recarga." },
      ]}
    />
  );
}
