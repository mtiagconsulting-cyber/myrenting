import vehiclesJson from "@/data/vehicles.json";
import matricesJson from "@/data/matrices.json";
import type { Vehicle, VehicleMatrices } from "./types";

export const vehicles = vehiclesJson as Vehicle[];
const matrices = matricesJson as Record<string, VehicleMatrices>;

export function getVehicle(slug: string) { return vehicles.find(v => v.slug === slug); }
export function getMatrix(slug: string) { return matrices[slug]; }
export function byCategory(cat: string) {
  return vehicles.filter(v => v.category.toLowerCase().includes(cat.toLowerCase()));
}
export function byFuel(bucket: string) {
  const f = (v: Vehicle) => v.fuel.toLowerCase();
  const map: Record<string,(v:Vehicle)=>boolean> = {
    electricos: v => f(v).includes("eléctr")||f(v).includes("electric"),
    hibridos: v => f(v).includes("híbr")||f(v).includes("hibr"),
    diesel: v => f(v).includes("diés")||f(v).includes("dies"),
    gasolina: v => f(v).includes("gasolina"),
  };
  return vehicles.filter(map[bucket] ?? (()=>true));
}
export const sortedByPrice = [...vehicles].sort((a,b)=>a.precio-b.precio);
export function alternatives(v: Vehicle, n=4) {
  return [...vehicles].filter(x=>x.slug!==v.slug)
    .sort((a,b)=>Math.abs(a.precio-v.precio)-Math.abs(b.precio-v.precio)).slice(0,n);
}
