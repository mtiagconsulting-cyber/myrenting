import inventory from "@/data/imported-inventory.json";
import vehicleAliases from "@/data/vehicle-aliases.json";
import type { Offer } from "@/types/offer";

const duplicateVehicleIds = new Set(Object.keys(vehicleAliases).map((slug) => `veh-${slug}`));
export const offers = inventory.offers.filter((offer) => !duplicateVehicleIds.has(offer.vehicleId)) as Offer[];
export const inventoryUpdatedAt = inventory.generatedAt;
