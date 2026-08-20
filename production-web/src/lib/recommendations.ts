import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export function recommendVehicles(vehicle: Vehicle, offer: Offer, vehicles: Vehicle[], offers: Offer[], limit = 3) {
  return vehicles
    .filter((candidate) => candidate.id !== vehicle.id)
    .flatMap((candidate) => {
      const candidateOffer = offers
        .filter((item) => item.vehicleId === candidate.id && item.audience === offer.audience)
        .sort((first, second) => Math.abs(first.monthlyPrice - offer.monthlyPrice) - Math.abs(second.monthlyPrice - offer.monthlyPrice))[0]
        ?? offers.filter((item) => item.vehicleId === candidate.id).sort((first, second) => first.monthlyPrice - second.monthlyPrice)[0];
      if (!candidateOffer) return [];
      const score =
        (candidate.bodyType === vehicle.bodyType ? 40 : 0) +
        (candidate.fuel === vehicle.fuel ? 24 : 0) +
        (candidate.label === vehicle.label ? 8 : 0) +
        Math.max(0, 18 - Math.abs(candidateOffer.monthlyPrice - offer.monthlyPrice) / 10) +
        Math.max(0, 10 - Math.abs(candidate.power - vehicle.power) / 15);
      return [{ vehicle: candidate, offer: candidateOffer, score }];
    })
    .sort((first, second) => second.score - first.score || first.offer.monthlyPrice - second.offer.monthlyPrice)
    .slice(0, limit);
}
