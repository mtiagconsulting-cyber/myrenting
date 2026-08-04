import type { Gestora, Perfil } from "./vehicle";

/** Matriz de precios: clave "km|meses" (p.ej. "15000|60") → €/mes. */
export type PriceMatrix = Record<string, number>;

/**
 * Offer = una configuración de renting contratable de un Vehicle,
 * para un perfil concreto. Entidad canónica (N).
 */
export interface Offer {
  vehicleSlug: string;
  perfil: Perfil;
  /** particular ⇒ cuota con IVA; empresa/autónomo ⇒ sin IVA. */
  iva: boolean;
  matrix: PriceMatrix;
  /** Cuota mínima de la matriz. */
  desde: number;
  kmOptions: number[];
  plazoOptions: number[];
}

/** Todas las matrices de un vehículo, indexadas por perfil. */
export type VehicleMatrices = Partial<Record<Perfil, PriceMatrix>>;
