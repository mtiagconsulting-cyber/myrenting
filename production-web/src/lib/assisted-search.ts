import { contentSlug } from "@/lib/content-slug";
import { vehicles } from "@/data/vehicles";

export type AssistedSearchContext = {
  brand?: string;
  model?: string;
  sourcePage: string;
};

export type AssistedSearchVehicleOption = {
  brand: string;
  models: string[];
};

export function assistedSearchVehicleOptions(): AssistedSearchVehicleOption[] {
  const catalogue = new Map<string, { brand: string; models: Map<string, string> }>();
  for (const vehicle of vehicles) {
    const key = contentSlug(vehicle.brand);
    const current = catalogue.get(key);
    const brand = !current || (current.brand === current.brand.toUpperCase() && vehicle.brand !== vehicle.brand.toUpperCase()) ? vehicle.brand : current.brand;
    const models = current?.models ?? new Map<string, string>();
    const model = vehicle.model.replace(new RegExp(`^${vehicle.brand}\\s+`, "i"), "");
    const modelKey = contentSlug(model);
    const currentModel = models.get(modelKey);
    if (!currentModel || (currentModel === currentModel.toUpperCase() && model !== model.toUpperCase())) models.set(modelKey, model);
    catalogue.set(key, { brand, models });
  }
  return [...catalogue.values()]
    .map(({ brand, models }) => ({ brand, models: [...models.values()].sort((a, b) => a.localeCompare(b, "es")) }))
    .sort((a, b) => a.brand.localeCompare(b.brand, "es"));
}

export function assistedSearchModelPath(brand: string, model: string) {
  const brandSlug = contentSlug(brand);
  let modelSlug = contentSlug(model);
  if (modelSlug.startsWith(`${brandSlug}-`)) modelSlug = modelSlug.slice(brandSlug.length + 1);
  return `/renting/${brandSlug}/${modelSlug}`;
}
