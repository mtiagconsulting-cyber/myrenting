import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import type { VehicleComparison } from "@/types/comparison";

export const popularComparisonSlugs = [
  "quadis-512258-vs-quadis-508905",
  "quadis-509319-vs-quadis-508905",
  "quadis-523043-vs-quadis-521147",
];

export function getComparison(slug: string): VehicleComparison | null {
  const [firstSlug, secondSlug, ...rest] = slug.split("-vs-");
  if (!firstSlug || !secondSlug || rest.length > 0 || firstSlug === secondSlug) return null;
  const firstVehicle = vehicles.find((vehicle) => vehicle.slug === firstSlug);
  const secondVehicle = vehicles.find((vehicle) => vehicle.slug === secondSlug);
  if (!firstVehicle || !secondVehicle) return null;
  const firstOffers = offers.filter((offer) => offer.vehicleId === firstVehicle.id);
  const secondOffers = offers.filter((offer) => offer.vehicleId === secondVehicle.id);
  const audienceOrder = { particular: 0, autonomo: 1, empresa: 2 };
  const matches = firstOffers.flatMap((first) => secondOffers.filter((second) => first.audience === second.audience && first.duration === second.duration && first.kilometers === second.kilometers).map((second) => ({ first, second }))).sort((a, b) => audienceOrder[a.first.audience] - audienceOrder[b.first.audience] || a.first.monthlyPrice + a.second.monthlyPrice - b.first.monthlyPrice - b.second.monthlyPrice);
  const matched = matches[0];
  const lowestPreferred = (list: typeof offers) => list.sort((a, b) => audienceOrder[a.audience] - audienceOrder[b.audience] || a.monthlyPrice - b.monthlyPrice)[0];
  const firstOffer = matched?.first ?? lowestPreferred(firstOffers);
  const secondOffer = matched?.second ?? lowestPreferred(secondOffers);
  if (!firstOffer || !secondOffer) return null;
  return { first: { vehicle: firstVehicle, offer: firstOffer }, second: { vehicle: secondVehicle, offer: secondOffer }, matchedConfiguration: Boolean(matched) };
}

export function totalContractCost(monthlyPrice: number, duration: number, initialPayment: number) {
  return monthlyPrice * duration + initialPayment;
}
