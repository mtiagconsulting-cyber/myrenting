import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export interface ComparisonSide {
  vehicle: Vehicle;
  offer: Offer;
}

export interface VehicleComparison {
  first: ComparisonSide;
  second: ComparisonSide;
  matchedConfiguration: boolean;
}
