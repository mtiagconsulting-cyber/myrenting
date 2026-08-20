import { Check, Minus } from "lucide-react";
import { totalContractCost } from "@/lib/comparison";
import type { ComparisonSide, VehicleComparison } from "@/types/comparison";

type Row = { group: string; label: string; value: (side: ComparisonSide) => string | boolean | null };

const rows: Row[] = [
  { group: "Renting", label: "Cuota mensual", value: ({ offer }) => `${offer.monthlyPrice} €/mes` },
  { group: "Renting", label: "Entrada", value: ({ offer }) => `${offer.initialPayment.toLocaleString("es-ES")} €` },
  { group: "Renting", label: "Coste total", value: ({ offer }) => `${totalContractCost(offer.monthlyPrice, offer.duration, offer.initialPayment).toLocaleString("es-ES")} €` },
  { group: "Renting", label: "Duración", value: ({ offer }) => `${offer.duration} meses` },
  { group: "Renting", label: "Kilómetros", value: ({ offer }) => `${offer.kilometers.toLocaleString("es-ES")} km/año` },
  { group: "Vehículo", label: "Motor", value: ({ vehicle }) => vehicle.fuel },
  { group: "Vehículo", label: "Potencia", value: ({ vehicle }) => `${vehicle.power} CV` },
  { group: "Vehículo", label: "Consumo", value: ({ vehicle }) => vehicle.consumption === null ? "Consultar" : `${vehicle.consumption.toLocaleString("es-ES")} ${vehicle.consumptionUnit}` },
  { group: "Vehículo", label: "Maletero", value: ({ vehicle }) => vehicle.trunk === null ? "Consultar" : `${vehicle.trunk} litros` },
  { group: "Vehículo", label: "Etiqueta DGT", value: ({ vehicle }) => vehicle.label },
  { group: "Incluido", label: "Seguro", value: ({ offer }) => offer.insurance },
  { group: "Incluido", label: "Mantenimiento", value: ({ offer }) => offer.maintenance },
  { group: "Incluido", label: "Neumáticos", value: ({ offer }) => offer.tyres },
];

export function ComparisonTable({ comparison }: { comparison: VehicleComparison }) {
  let lastGroup = "";
  return (
    <section aria-labelledby="tabla-comparativa">
      <div className="mb-5"><h2 id="tabla-comparativa" className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Comparación completa</h2><p className="mt-2 text-xs text-muted sm:hidden">Desliza la tabla horizontalmente para ver ambos coches.</p></div>
      <div className="overflow-x-auto rounded-xl border border-line bg-surface">
        <table className="w-full min-w-[44rem] border-collapse text-left">
          <thead><tr className="border-b border-line bg-slate-50"><th className="sticky left-0 z-10 w-[32%] bg-slate-50 p-4 text-xs font-bold text-muted">Característica</th><th className="w-[34%] border-l border-line p-4 text-sm font-bold text-ink">{comparison.first.vehicle.brand} {comparison.first.vehicle.model}</th><th className="w-[34%] border-l border-line p-4 text-sm font-bold text-ink">{comparison.second.vehicle.brand} {comparison.second.vehicle.model}</th></tr></thead>
          <tbody>{rows.map((row) => { const showGroup = row.group !== lastGroup; lastGroup = row.group; const first = row.value(comparison.first); const second = row.value(comparison.second); return <tr key={`${row.group}-${row.label}`} className="border-b border-line last:border-0"><th className="sticky left-0 z-10 bg-surface p-4"><span className="block text-[0.625rem] font-bold tracking-[0.08em] text-brand uppercase">{showGroup ? row.group : ""}</span><span className="mt-1 block text-xs font-semibold text-copy">{row.label}</span></th><Cell value={first} /><Cell value={second} /></tr>; })}</tbody>
        </table>
      </div>
    </section>
  );
}

function Cell({ value }: { value: string | boolean | null }) { return <td className="border-l border-line p-4 font-data text-sm font-semibold text-ink tabular-nums">{value === null ? <span className="inline-flex items-center gap-2 font-sans text-xs text-muted"><Minus size={16} aria-hidden="true" />No consta</span> : typeof value === "boolean" ? value ? <span className="inline-flex items-center gap-2 font-sans text-xs text-positive"><Check size={16} aria-hidden="true" />Incluido</span> : <span className="inline-flex items-center gap-2 font-sans text-xs text-muted"><Minus size={16} aria-hidden="true" />No incluido</span> : value}</td>; }
