import { contentSlug } from "@/lib/content-slug";
import type { FuelType } from "@/types/vehicle";
import type { OfferAudience } from "@/types/offer";

export const audienceLabels: Record<OfferAudience, string> = { particular: "particulares", autonomo: "autónomos", empresa: "empresas" };

export const fuelPages: Array<{ slug: string; fuel: FuelType; label: string }> = [
  { slug: "gasolina", fuel: "Gasolina", label: "gasolina" },
  { slug: "diesel", fuel: "Diésel", label: "diésel" },
  { slug: "hibridos", fuel: "Híbrido", label: "híbridos" },
  { slug: "hibridos-enchufables", fuel: "Híbrido enchufable", label: "híbridos enchufables" },
  { slug: "electricos", fuel: "Eléctrico", label: "eléctricos" },
];

export function modelPath(brand: string, model: string) { return `/renting/${contentSlug(brand)}/${contentSlug(model)}`; }
export function categoryPath(bodyType: string) {
  if (bodyType === "SUV") return "/renting/suv";
  if (bodyType === "Familiar" || bodyType === "Furgoneta") return "/renting/familiares";
  if (bodyType === "Compacto") return "/renting/coches-pequenos";
  return "/renting";
}
