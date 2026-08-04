import type { Vehicle } from "./vehicle";

/** Brand = agregado por marca (make) para hubs /marcas/[slug]. */
export interface Brand {
  slug: string;
  name: string;
  vehicles: Vehicle[];
  count: number;
  /** Cuota "desde" mínima de la marca. */
  desde: number;
}
