import type { Vehicle } from "./vehicle";

/** Una fila de la tabla comparativa (sin puntuaciones artificiales). */
export interface ComparisonRow {
  label: string;
  a: string;
  b: string;
  /** Cuál es "mejor" en esta fila cuando aplica objetivamente (p.ej. precio). */
  winner?: "a" | "b" | "tie";
}

/** Comparación entre dos vehículos. */
export interface Comparison {
  a: Vehicle;
  b: Vehicle;
  cheaper: "a" | "b" | "tie";
  rows: ComparisonRow[];
  /** Recomendaciones honestas: "Elegiría A si…" / "Elegiría B si…". */
  verdictA: string;
  verdictB: string;
}
