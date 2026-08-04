import vehiclesJson from "./vehicles.json";
import type { Vehicle } from "@/types";

export const vehicles = vehiclesJson as Vehicle[];

export const sortedByPrice: Vehicle[] = [...vehicles].sort((a, b) => a.precio - b.precio);

export function getVehicle(slug: string): Vehicle | undefined {
  return vehicles.find((v) => v.slug === slug);
}

export function byCategory(cat: string): Vehicle[] {
  return vehicles.filter((v) => v.category.toLowerCase().includes(cat.toLowerCase()));
}

const fuelMatchers: Record<string, (f: string) => boolean> = {
  electricos: (f) => f.includes("eléctr") || f.includes("electric"),
  hibridos: (f) => f.includes("híbr") || f.includes("hibr"),
  diesel: (f) => f.includes("diés") || f.includes("dies"),
  gasolina: (f) => f.includes("gasolina"),
};

export function byFuel(bucket: string): Vehicle[] {
  const match = fuelMatchers[bucket];
  if (!match) return vehicles;
  return vehicles.filter((v) => match(v.fuel.toLowerCase()));
}

/** Alternativas por cercanía de precio (para "Alternativas" en ficha). */
export function alternatives(v: Vehicle, n = 4): Vehicle[] {
  return [...vehicles]
    .filter((x) => x.slug !== v.slug)
    .sort((a, b) => Math.abs(a.precio - v.precio) - Math.abs(b.precio - v.precio))
    .slice(0, n);
}
