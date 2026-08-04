// Shim de compatibilidad. El modelo canónico vive en @/types.
export type { Vehicle, Perfil, Gestora } from "@/types";
export type { PriceMatrix, VehicleMatrices } from "@/types";
/** Alias retro: una matriz de precio suelta ("km|meses" → €/mes). */
export type Matrix = import("@/types").PriceMatrix;
