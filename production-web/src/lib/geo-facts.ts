import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { getLandingPairs, type SeoLanding } from "@/lib/seo-landing-engine";
import { vehiclePublicPath } from "@/lib/vehicle-groups";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export interface GeoRankingRow {
  name: string;
  brand: string;
  model: string;
  price: number;
  fuel: string;
  transmission: string;
  availability: Offer["availability"];
  duration: number;
  kilometers: number;
  provider: string;
  path: string;
}

export interface GeoFacts {
  minimumPrice: number;
  maximumPrice: number;
  averagePrice: number;
  cheapestVehicle: string;
  cheapestModel: string;
  cheapestBrand: string;
  numberOfOffers: number;
  numberOfModels: number;
  numberOfBrands: number;
  automaticCount: number;
  hybridCount: number;
  electricCount: number;
  ecoCount: number;
  zeroCount: number;
  immediateDeliveryCount: number;
  noEntryCount: number;
  availableDurations: number[];
  availableKilometers: number[];
  availableFuels: string[];
  providers: string[];
  ranking: GeoRankingRow[];
}

function isAutomatic(vehicle: Vehicle) {
  return /auto|dsg|cvt|dct|stronic|automatic/i.test(vehicle.transmission ?? vehicle.version);
}

export function generateGeoFacts(landing: Pick<SeoLanding, "filters">): GeoFacts | null {
  const pairs = getLandingPairs(landing);
  if (!pairs.length) return null;
  const sorted = [...pairs].sort((a, b) => a.offer.monthlyPrice - b.offer.monthlyPrice);
  const cheapestByModel = new Map<string, (typeof pairs)[number]>();
  for (const pair of sorted) {
    const key = `${pair.vehicle.brand}|${pair.vehicle.model}`;
    if (!cheapestByModel.has(key)) cheapestByModel.set(key, pair);
  }
  const ranking = [...cheapestByModel.values()].slice(0, 10).map(({ vehicle, offer }) => ({
    name: `${vehicle.brand} ${vehicle.model}`,
    brand: vehicle.brand,
    model: vehicle.model,
    price: offer.monthlyPrice,
    fuel: vehicle.fuel,
    transmission: vehicle.transmission || (isAutomatic(vehicle) ? "Automático" : "Consultar"),
    availability: offer.availability,
    duration: offer.duration,
    kilometers: offer.kilometers,
    provider: offer.provider,
    path: vehiclePublicPath(vehicle),
  }));
  const prices = pairs.map(({ offer }) => offer.monthlyPrice);
  const first = sorted[0];
  return {
    minimumPrice: Math.min(...prices),
    maximumPrice: Math.max(...prices),
    averagePrice: Math.round(prices.reduce((sum, value) => sum + value, 0) / prices.length),
    cheapestVehicle: `${first.vehicle.brand} ${first.vehicle.model} ${first.vehicle.version}`,
    cheapestModel: `${first.vehicle.brand} ${first.vehicle.model}`,
    cheapestBrand: first.vehicle.brand,
    numberOfOffers: pairs.length,
    numberOfModels: new Set(pairs.map(({ vehicle }) => `${vehicle.brand}|${vehicle.model}`)).size,
    numberOfBrands: new Set(pairs.map(({ vehicle }) => vehicle.brand).filter(Boolean)).size,
    automaticCount: pairs.filter(({ vehicle }) => isAutomatic(vehicle)).length,
    hybridCount: pairs.filter(({ vehicle }) => vehicle.fuel === "Híbrido" || vehicle.fuel === "Híbrido enchufable").length,
    electricCount: pairs.filter(({ vehicle }) => vehicle.fuel === "Eléctrico").length,
    ecoCount: pairs.filter(({ vehicle }) => vehicle.label === "ECO").length,
    zeroCount: pairs.filter(({ vehicle }) => vehicle.label === "0").length,
    immediateDeliveryCount: pairs.filter(({ offer }) => offer.availability === "Disponible").length,
    noEntryCount: pairs.filter(({ offer }) => offer.initialPayment === 0).length,
    availableDurations: [...new Set(pairs.map(({ offer }) => offer.duration))].sort((a, b) => a - b),
    availableKilometers: [...new Set(pairs.map(({ offer }) => offer.kilometers))].sort((a, b) => a - b),
    availableFuels: [...new Set(pairs.map(({ vehicle }) => vehicle.fuel))].sort((a, b) => a.localeCompare(b, "es")),
    providers: [...new Set(pairs.map(({ offer }) => offer.provider))].sort((a, b) => a.localeCompare(b, "es")),
    ranking,
  };
}

function factsFor(filters: SeoLanding["filters"]) {
  return generateGeoFacts({ filters });
}

export function getMarketStats() { return factsFor({}); }
export function getBrandStats(brand: string) { return factsFor({ brand }); }
export function getModelStats(brand: string, model: string) { return factsFor({ brand, model }); }
export function getCategoryStats(bodyTypes: Vehicle["bodyType"][]) { return factsFor({ bodyTypes }); }
export function getPriceStats(maxPrice: number) { return factsFor({ maxPrice }); }

export function inventoryEntityCounts() {
  return { vehicles: vehicles.length, offers: offers.length };
}
