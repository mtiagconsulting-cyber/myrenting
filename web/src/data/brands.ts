import { vehicles } from "./vehicles";
import type { Brand, Vehicle } from "@/types";

/** slug de marca: "Mercedes-Benz" → "mercedes-benz". */
export function brandSlug(make: string): string {
  return make
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function buildBrands(list: Vehicle[]): Brand[] {
  const map = new Map<string, Vehicle[]>();
  for (const v of list) {
    const arr = map.get(v.make) ?? [];
    arr.push(v);
    map.set(v.make, arr);
  }
  return [...map.entries()]
    .map(([name, vs]) => ({
      slug: brandSlug(name),
      name,
      vehicles: [...vs].sort((a, b) => a.precio - b.precio),
      count: vs.length,
      desde: Math.min(...vs.map((v) => v.precio)),
    }))
    .sort((a, b) => a.name.localeCompare(b.name, "es"));
}

export const brands: Brand[] = buildBrands(vehicles);

export function getBrand(slug: string): Brand | undefined {
  return brands.find((b) => b.slug === slug);
}
