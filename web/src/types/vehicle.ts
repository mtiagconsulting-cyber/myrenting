/** Gestoras de renting con las que trabajamos. */
export type Gestora = "Quadis" | "M Automoción" | "Kia Renting";

/** Perfil de cliente: define IVA y matriz de precio aplicable. */
export type Perfil = "particular" | "autonomo" | "empresa";

/**
 * Vehicle = el modelo físico y sus especificaciones.
 * Entidad canónica (1) — se relaciona 1:N con Offer.
 */
export interface Vehicle {
  slug: string;
  make: string;
  model: string;
  title: string;
  version: string;
  fuel: string;
  /** Categoría comercial: SUV, Urbano, Familiar, Furgoneta… */
  category: string;
  /** Etiqueta medioambiental DGT: 0, ECO, C, B o "—". */
  dgt: string;
  cv: string;
  seats: string;
  cons: string;
  img: string;
  /** Cuota "desde" mostrada (mínimo entre perfiles/combinaciones). */
  precio: number;
  fuentes: Gestora[];
  /** Perfil que produce la cuota mínima (particular | autonomo | empresa). */
  tipoMin: Perfil;
}
