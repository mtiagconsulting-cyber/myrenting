import type { Metadata } from "next";
import Hub from "@/components/seo/Hub";
import { byCarroceria, priceRange } from "@/data/vehicles";

const list = byCarroceria("suv");
const { min, max } = priceRange(list);

export const metadata: Metadata = {
  title: "Renting de SUV — mejores ofertas comparadas",
  description: `Compara ${list.length} SUV en renting desde ${min} €/mes. Cuota real por km y plazo, seguro y mantenimiento incluidos, sin entrada.`,
  alternates: { canonical: "/renting-suv" },
};

export default function RentingSuv() {
  return (
    <Hub
      canonicalPath="/renting-suv"
      crumbs={[{ name: "Coches", href: "/coches" }, { name: "SUV" }]}
      title="Renting de SUV"
      intro={`Los SUV combinan posición de conducción elevada, espacio y versatilidad. Comparamos ${list.length} modelos de gestoras oficiales, con la cuota real según kilómetros y plazo, seguro y mantenimiento incluidos y sin entrada.`}
      vehicles={list}
      summary={[
        { label: "Modelos comparados", value: String(list.length) },
        { label: "Cuota desde", value: `${min} €/mes` },
        { label: "Rango de precio", value: `${min}–${max} €/mes` },
        { label: "Entrada", value: "0 €" },
      ]}
      idealFor="familias y quienes buscan espacio, maletero grande y buena visibilidad, sin renunciar a etiquetas ECO o CERO."
      faq={[
        { q: "¿Cuánto cuesta un SUV en renting?", a: `Depende del modelo, los kilómetros y el plazo. En nuestra comparativa los SUV arrancan desde ${min} €/mes con seguro y mantenimiento incluidos y sin entrada.` },
        { q: "¿Qué incluye la cuota?", a: "Seguro a todo riesgo, mantenimiento y averías, neumáticos, impuestos, asistencia en carretera y gestión de multas. No incluye combustible ni recarga." },
        { q: "¿Hay SUV con etiqueta ECO o CERO?", a: "Sí. Puedes filtrar por etiqueta DGT en el listado para ver solo híbridos (ECO) o eléctricos (CERO)." },
      ]}
    />
  );
}
