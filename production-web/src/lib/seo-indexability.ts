import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { contentSlug } from "@/lib/content-slug";
import { canonicalVehicles, vehiclesInSameGroup } from "@/lib/vehicle-groups";
import type { OfferAudience } from "@/types/offer";

export const seoAudiences: OfferAudience[] = ["particular", "autonomo", "empresa"];

export interface ModelAudiencePage {
  brand: string;
  model: string;
  brandSlug: string;
  modelSlug: string;
  audience: OfferAudience;
  vehicleCount: number;
  combinationCount: number;
  minimumPrice: number;
  maximumPrice: number;
}

export interface BrandAudiencePage {
  brand: string;
  brandSlug: string;
  audience: OfferAudience;
  modelCount: number;
  vehicleCount: number;
  combinationCount: number;
  minimumPrice: number;
  maximumPrice: number;
}

export const modelAudiencePages: ModelAudiencePage[] = (() => {
  const groups = new Map<string, { brand: string; model: string }>();
  for (const vehicle of vehicles) groups.set(`${contentSlug(vehicle.brand)}/${contentSlug(vehicle.model)}`, { brand: vehicle.brand, model: vehicle.model });

  return [...groups.values()].flatMap(({ brand, model }) => {
    const modelVehicles = vehicles.filter((vehicle) => vehicle.brand === brand && vehicle.model === model);
    const canonical = canonicalVehicles(modelVehicles);
    return seoAudiences.flatMap((audience) => {
      const eligibleOffers = canonical.flatMap((vehicle) => {
        const ids = new Set(vehiclesInSameGroup(vehicle, modelVehicles).map((item) => item.id));
        return offers.filter((offer) => ids.has(offer.vehicleId) && offer.audience === audience);
      });
      if (eligibleOffers.length < 3) return [];
      const prices = eligibleOffers.map((offer) => offer.monthlyPrice);
      return [{
        brand,
        model,
        brandSlug: contentSlug(brand),
        modelSlug: contentSlug(model),
        audience,
        vehicleCount: canonical.filter((vehicle) => vehiclesInSameGroup(vehicle, modelVehicles).some((candidate) => offers.some((offer) => offer.vehicleId === candidate.id && offer.audience === audience))).length,
        combinationCount: eligibleOffers.length,
        minimumPrice: Math.min(...prices),
        maximumPrice: Math.max(...prices),
      }];
    });
  });
})();

export function findModelAudiencePage(brandSlug: string, modelSlug: string, audience: string) {
  return modelAudiencePages.find((page) => page.brandSlug === brandSlug && page.modelSlug === modelSlug && page.audience === audience);
}

export function modelAudiencePath(page: Pick<ModelAudiencePage, "brandSlug" | "modelSlug" | "audience">) {
  return `/modelos/${page.brandSlug}/${page.modelSlug}/${page.audience}`;
}

export const brandAudiencePages: BrandAudiencePage[] = (() => {
  const brands = [...new Map(vehicles.map((vehicle) => [contentSlug(vehicle.brand), vehicle.brand])).entries()];
  return brands.flatMap(([brandSlug, brand]) => seoAudiences.flatMap((audience) => {
    const brandVehicles = vehicles.filter((vehicle) => contentSlug(vehicle.brand) === brandSlug);
    const canonical = canonicalVehicles(brandVehicles);
    const eligibleVehicles = canonical.filter((vehicle) => {
      const ids = new Set(vehiclesInSameGroup(vehicle, brandVehicles).map((item) => item.id));
      return offers.some((offer) => ids.has(offer.vehicleId) && offer.audience === audience);
    });
    const eligibleIds = new Set(brandVehicles.filter((vehicle) => eligibleVehicles.some((candidate) => vehiclesInSameGroup(candidate, brandVehicles).some((item) => item.id === vehicle.id))).map((vehicle) => vehicle.id));
    const eligibleOffers = offers.filter((offer) => eligibleIds.has(offer.vehicleId) && offer.audience === audience);
    // Una página de marca necesita catálogo suficiente para aportar más valor
    // que sus modelos individuales.
    if (eligibleVehicles.length < 2 || eligibleOffers.length < 6) return [];
    const prices = eligibleOffers.map((offer) => offer.monthlyPrice);
    return [{ brand, brandSlug, audience, modelCount: new Set(eligibleVehicles.map((vehicle) => vehicle.model)).size, vehicleCount: eligibleVehicles.length, combinationCount: eligibleOffers.length, minimumPrice: Math.min(...prices), maximumPrice: Math.max(...prices) }];
  }));
})();

export function findBrandAudiencePage(brandSlug: string, audience: string) {
  return brandAudiencePages.find((page) => page.brandSlug === brandSlug && page.audience === audience);
}

export function brandAudiencePath(page: Pick<BrandAudiencePage, "brandSlug" | "audience">) {
  return `/marcas/${page.brandSlug}/${page.audience}`;
}
