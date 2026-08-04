import matricesJson from "./matrices.json";
import type { Offer, Perfil, PriceMatrix, VehicleMatrices } from "@/types";

const raw = matricesJson as Record<string, Record<string, PriceMatrix>>;

/** particular ⇒ con IVA; empresa/autónomo ⇒ sin IVA. */
const IVA_BY_PERFIL: Record<Perfil, boolean> = {
  particular: true,
  autonomo: false,
  empresa: false,
};

function optionsFromMatrix(matrix: PriceMatrix): { km: number[]; plazo: number[] } {
  const km = new Set<number>();
  const plazo = new Set<number>();
  for (const key of Object.keys(matrix)) {
    const [k, m] = key.split("|").map(Number);
    if (!Number.isNaN(k)) km.add(k);
    if (!Number.isNaN(m)) plazo.add(m);
  }
  return {
    km: [...km].sort((a, b) => a - b),
    plazo: [...plazo].sort((a, b) => a - b),
  };
}

function buildOffer(vehicleSlug: string, perfil: Perfil, matrix: PriceMatrix): Offer {
  const { km, plazo } = optionsFromMatrix(matrix);
  const desde = Math.min(...Object.values(matrix));
  return {
    vehicleSlug,
    perfil,
    iva: IVA_BY_PERFIL[perfil],
    matrix,
    desde,
    kmOptions: km,
    plazoOptions: plazo,
  };
}

/** Todas las ofertas contratables, aplanadas (vehículo × perfil). */
export const offers: Offer[] = Object.entries(raw).flatMap(([slug, byPerfil]) =>
  (Object.entries(byPerfil) as [Perfil, PriceMatrix][]).map(([perfil, matrix]) =>
    buildOffer(slug, perfil, matrix),
  ),
);

/** Matrices de un vehículo indexadas por perfil (para el configurador). */
export function getMatrices(slug: string): VehicleMatrices | undefined {
  return raw[slug] as VehicleMatrices | undefined;
}

export function getOffers(slug: string): Offer[] {
  return offers.filter((o) => o.vehicleSlug === slug);
}

export function getOffer(slug: string, perfil: Perfil): Offer | undefined {
  return offers.find((o) => o.vehicleSlug === slug && o.perfil === perfil);
}

/** Cuota concreta para un perfil, km y plazo (o undefined si no existe). */
export function cuota(slug: string, perfil: Perfil, km: number, meses: number): number | undefined {
  return raw[slug]?.[perfil]?.[`${km}|${meses}`];
}
