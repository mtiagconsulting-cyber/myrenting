export type FuelType = "Gasolina" | "Diésel" | "Híbrido" | "Híbrido enchufable" | "Eléctrico";
export type DgtLabel = "C" | "ECO" | "0";
export type BodyType = "Compacto" | "Familiar" | "SUV" | "Berlina" | "Furgoneta";

export interface VehicleImages {
  hero: string;
  card: string;
  compare: string;
  interior: string;
  trunk: string;
}

export interface VehicleDimensions {
  lengthMm?: number;
  widthMm?: number;
  heightMm?: number;
  wheelbaseMm?: number;
}

export interface VehicleSpecSource {
  id: string;
  url: string;
  publisher: string;
  retrievedAt: string;
  retrieval: "live" | "verified-cache";
  confidence: "high";
  matchedVersion: string;
}

export interface Vehicle {
  id: string;
  brand: string;
  model: string;
  version: string;
  slug: string;
  images: VehicleImages | null;
  fuel: FuelType;
  power: number;
  trunk: number | null;
  consumption: number | null;
  consumptionRange?: { min: number; max: number } | null;
  consumptionUnit: "l/100 km" | "kWh/100 km";
  label: DgtLabel;
  bodyType: BodyType;
  transmission?: string | null;
  doors?: number | null;
  seats?: number | null;
  colors?: string[] | null;
  campaign?: string | null;
  sourceUrl?: string | null;
  dimensions?: VehicleDimensions | null;
  electricRangeKm?: number | null;
  emissionsCo2GKm?: number | null;
  emissionsCo2Range?: { min: number; max: number } | null;
  batteryCapacityKWh?: number | null;
  specSource?: VehicleSpecSource | null;
  specSources?: VehicleSpecSource[];
}
