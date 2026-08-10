export type Vehicle = {
  slug: string; make: string; model: string; title: string; version: string;
  fuel: string; category: string; dgt: string; cv: string; seats: string;
  cons: string; precio: number; img: string; fuentes: string[]; tipoMin: string;
};
export type Matrix = Record<string, number>;            // "km|meses" -> precio
export type VehicleMatrices = Record<string, Matrix>;   // tipo -> Matrix
