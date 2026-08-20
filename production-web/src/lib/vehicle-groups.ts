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

/**
 * Identidad comercial de una versión. Los proveedores crean registros separados
 * por público, pero marca, modelo y versión permanecen iguales. Combustible y
 * potencia evitan unir accidentalmente dos motorizaciones con nombres parecidos.
 */
export function vehicleGroupKey(vehicle: Vehicle) {
  return [vehicle.brand, vehicle.model, vehicle.version, vehicle.fuel, vehicle.power]
    .map(normalizeIdentityPart)
    .join("|");
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
    const key = vehicleGroupKey(vehicle);
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
