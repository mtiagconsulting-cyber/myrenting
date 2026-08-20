import type { Vehicle } from "@/types/vehicle";
import { contentSlug } from "@/lib/content-slug";

function normalizeIdentityPart(value: string | number) {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

/** Identidad de motorización compartida entre proveedores.
 *
 * Las gestoras suelen escribir de forma distinta la misma versión (por ejemplo,
 * "6 Vel. MAN" y "6 Vel. Manual Turbo"). Marca, modelo, combustible, potencia y
 * cambio son más estables y permiten reunir esas variantes sin mezclar motores.
 */
export function vehicleGroupKey(vehicle: Vehicle) {
  return [vehicle.brand, vehicle.model, vehicle.fuel, vehicle.power, vehicle.transmission ?? ""]
    .map(normalizeIdentityPart)
    .join("|");
}

export function vehicleModelKey(vehicle: Vehicle) {
  const brand = normalizeIdentityPart(vehicle.brand);
  let model = normalizeIdentityPart(vehicle.model);
  // Algunos proveedores repiten la marca dentro del modelo (p. ej.
  // "ALFA-ROMEO / ALFA ROMEO JUNIOR").
  if (model.startsWith(`${brand} `)) model = model.slice(brand.length + 1);
  return `${brand}|${model}`;
}

export function vehiclesInSameGroup(vehicle: Vehicle, allVehicles: Vehicle[]) {
  const key = vehicleGroupKey(vehicle);
  return allVehicles.filter((candidate) => vehicleGroupKey(candidate) === key);
}

export function representativeVehicle(group: Vehicle[]) {
  return [...group].sort((first, second) => {
    const firstRank = first.slug.includes("particular") ? 0 : first.slug.includes("autonomo") ? 1 : 2;
    const secondRank = second.slug.includes("particular") ? 0 : second.slug.includes("autonomo") ? 1 : 2;
    return firstRank - secondRank || first.slug.localeCompare(second.slug, "es");
  })[0];
}

export function canonicalVehicle(vehicle: Vehicle, allVehicles: Vehicle[]) {
  return representativeVehicle(vehiclesInSameGroup(vehicle, allVehicles));
}

export function canonicalVehicles(allVehicles: Vehicle[]) {
  const groups = new Map<string, Vehicle[]>();
  for (const vehicle of allVehicles) {
    const key = vehicleModelKey(vehicle);
    groups.set(key, [...(groups.get(key) ?? []), vehicle]);
  }
  return [...groups.values()].map(representativeVehicle);
}

export function vehiclePublicSlug(vehicle: Vehicle) {
  return contentSlug(`${vehicle.brand}-${vehicle.model}-${vehicle.version}-${vehicle.power}-cv-${vehicle.fuel}`);
}

export function vehiclePublicPath(vehicle: Vehicle) {
  return `/coches/${vehiclePublicSlug(vehicle)}`;
}
