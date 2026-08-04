// Agregador de compatibilidad: reexporta el modelo canónico de data/.
// Las páginas pueden importar de aquí o directamente de @/data/*.
export {
  vehicles,
  sortedByPrice,
  getVehicle,
  byCategory,
  byFuel,
  alternatives,
} from "@/data/vehicles";

export { getMatrices, getOffers, getOffer, offers, cuota } from "@/data/offers";
export { brands, getBrand, brandSlug } from "@/data/brands";

/** Alias retro: antes `getMatrix` devolvía las matrices por perfil de un slug. */
export { getMatrices as getMatrix } from "@/data/offers";
