export type OfferAvailability = "Disponible" | "Entrega próxima" | "Consultar";
export type OfferAudience = "particular" | "autonomo" | "empresa";

export interface Offer {
  id: string;
  vehicleId: string;
  provider: string;
  audience: OfferAudience;
  monthlyPrice: number;
  priceIncludesVat: boolean;
  monthlyPriceExVat?: number | null;
  monthlyPriceIncVat?: number | null;
  initialPayment: number;
  duration: number;
  kilometers: number;
  maintenance: boolean | null;
  insurance: boolean | null;
  tyres: boolean | null;
  availability: OfferAvailability;
  coverage?: Array<{ item: string; detail: string }>;
  sourceUrl?: string | null;
  verifiedAt?: string;
}
