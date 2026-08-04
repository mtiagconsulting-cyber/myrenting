import type { Metadata } from "next";
import Hub from "@/components/seo/Hub";
import { byFuel, priceRange } from "@/data/vehicles";

const list = [...byFuel("electricos")].sort((a, b) => a.precio - b.precio);
const { min, max } = priceRange(list);

export const metadata: Metadata = {
  title: "Renting de coches eléctricos — etiqueta CERO comparada",
  description: `Compara ${list.length} coches eléctricos en renting desde ${min} €/mes. Etiqueta CERO, cero emisiones, cuota real sin entrada.`,
  alternates: { canonical: "/renting-electricos" },
};

export default function RentingElectricos() {
  return (
    <Hub
      canonicalPath="/renting-electricos"
      crumbs={[{ name: "Coches", href: "/coches" }, { name: "Eléctricos" }]}
      title="Renting de coches eléctricos"
      intro={`Los eléctricos tienen etiqueta CERO, acceso sin restricciones a las zonas de bajas emisiones y el menor coste por kilómetro. Comparamos ${list.length} modelos con cuota real por km y plazo, seguro y mantenimiento incluidos y sin entrada.`}
      vehicles={list}
      summary={[
        { label: "Modelos comparados", value: String(list.length) },
        { label: "Cuota desde", value: `${min} €/mes` },
        { label: "Rango de precio", value: `${min}–${max} €/mes` },
        { label: "Etiqueta DGT", value: "CERO" },
      ]}
      idealFor="quienes pueden cargar en casa o en el trabajo, hacen sobre todo ciudad y quieren circular sin restricciones por las zonas de bajas emisiones."
      faq={[
        { q: "¿Qué etiqueta tienen los eléctricos?", a: "Los eléctricos puros (BEV) tienen la etiqueta CERO de la DGT, la más favorable, con acceso libre a las zonas de bajas emisiones." },
        { q: "¿El renting eléctrico incluye el punto de carga?", a: "La cuota incluye seguro, mantenimiento, neumáticos e impuestos, pero no el punto de carga doméstico ni la electricidad. Consúltanos si te interesa añadir instalación." },
        { q: "¿Cuánto cuesta un eléctrico en renting?", a: `En nuestra comparativa los eléctricos arrancan desde ${min} €/mes, con seguro y mantenimiento incluidos y sin entrada.` },
      ]}
    />
  );
}
