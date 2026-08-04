import type { Metadata } from "next";
import Hub from "@/components/seo/Hub";
import { byFuel, priceRange } from "@/data/vehicles";

const list = [...byFuel("hibridos")].sort((a, b) => a.precio - b.precio);
const { min, max } = priceRange(list);

export const metadata: Metadata = {
  title: "Renting de coches híbridos — etiqueta ECO comparada",
  description: `Compara ${list.length} coches híbridos en renting desde ${min} €/mes. Etiqueta ECO, menor consumo, cuota real sin entrada.`,
  alternates: { canonical: "/renting-hibridos" },
};

export default function RentingHibridos() {
  return (
    <Hub
      canonicalPath="/renting-hibridos"
      crumbs={[{ name: "Coches", href: "/coches" }, { name: "Híbridos" }]}
      title="Renting de coches híbridos"
      intro={`Los híbridos reducen consumo y emisiones y suelen lograr la etiqueta ECO de la DGT, con acceso a zonas de bajas emisiones. Comparamos ${list.length} modelos con cuota real por km y plazo, seguro y mantenimiento incluidos y sin entrada.`}
      vehicles={list}
      summary={[
        { label: "Modelos comparados", value: String(list.length) },
        { label: "Cuota desde", value: `${min} €/mes` },
        { label: "Rango de precio", value: `${min}–${max} €/mes` },
        { label: "Etiqueta DGT", value: "ECO (mayoría)" },
      ]}
      idealFor="quienes hacen ciudad y carretera, quieren bajar el consumo y necesitan etiqueta ECO para circular por zonas de bajas emisiones sin cargar en casa."
      faq={[
        { q: "¿Los híbridos tienen etiqueta ECO?", a: "La mayoría de híbridos convencionales y enchufables obtienen la etiqueta ECO de la DGT. Los micro-híbridos pueden tener etiqueta ECO o C según el modelo." },
        { q: "¿Necesito enchufe para un híbrido?", a: "Los híbridos convencionales (HEV) y micro-híbridos no necesitan enchufe. Solo los híbridos enchufables (PHEV) se benefician de cargar la batería." },
        { q: "¿Cuánto cuesta un híbrido en renting?", a: `En nuestra comparativa los híbridos arrancan desde ${min} €/mes, con seguro y mantenimiento incluidos y sin entrada.` },
      ]}
    />
  );
}
