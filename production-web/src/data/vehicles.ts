import inventory from "@/data/imported-inventory.json";
import photoManifest from "@/data/photo-manifest.json";
import vehicleAliases from "@/data/vehicle-aliases.json";
import specEvidence from "@/data/vehicle-spec-evidence.json";
import type { Vehicle, VehicleSpecSource } from "@/types/vehicle";

type PhotoRecord = { hero: string; card: string; compare: string; interior: string; trunk: string; sourceFolder: string };
const photos = photoManifest.photos as Record<string, PhotoRecord>;
type SpecEvidence = Partial<Pick<Vehicle, "trunk" | "consumption" | "consumptionRange" | "doors" | "seats" | "dimensions" | "electricRangeKm" | "emissionsCo2GKm" | "emissionsCo2Range" | "batteryCapacityKWh">> & { source?: Vehicle["specSource"]; sources?: VehicleSpecSource[] };
const officialSpecs = specEvidence.specs as Record<string, SpecEvidence>;
const duplicateSlugs = new Set(Object.keys(vehicleAliases));
export const vehicles = inventory.vehicles.filter((vehicle) => !duplicateSlugs.has(vehicle.slug)).map((vehicle) => {
  const official = officialSpecs[vehicle.id];
  return { ...vehicle, ...(official ?? {}), ...(official?.source ? { specSource: official.source } : {}), ...(official?.sources ? { specSources: official.sources } : {}), images: photos[vehicle.id] ? { hero: photos[vehicle.id].hero, card: photos[vehicle.id].card, compare: photos[vehicle.id].compare, interior: photos[vehicle.id].interior, trunk: photos[vehicle.id].trunk } : null };
}) as Vehicle[];
const brandMap = new Map<string, string>();
for (const vehicle of vehicles) {
  const key = vehicle.brand.toLocaleLowerCase("es");
  const current = brandMap.get(key);
  if (!current || (current === current.toUpperCase() && vehicle.brand !== vehicle.brand.toUpperCase())) brandMap.set(key, vehicle.brand);
}
export const brands = [...brandMap.values()].sort((first, second) => first.localeCompare(second, "es"));
