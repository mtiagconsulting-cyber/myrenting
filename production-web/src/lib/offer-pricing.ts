import type { Offer } from "@/types/offer";

export function offerPriceExVat(offer: Offer) {
  return offer.monthlyPriceExVat ?? (offer.priceIncludesVat ? offer.monthlyPrice / 1.21 : offer.monthlyPrice);
}

export function offerPriceIncVat(offer: Offer) {
  return offer.monthlyPriceIncVat ?? (offer.priceIncludesVat ? offer.monthlyPrice : offer.monthlyPrice * 1.21);
}

export function formatMonthlyPrice(value: number) {
  return value.toLocaleString("es-ES", { maximumFractionDigits: 2 });
}

