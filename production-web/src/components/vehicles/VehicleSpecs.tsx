import type { Vehicle } from "@/types/vehicle";

export function VehicleSpecs({ vehicle }: { vehicle: Vehicle }) {
  const specs = [
    ["Motor", vehicle.fuel],
    ["Potencia", vehicle.power ? `${vehicle.power} CV` : "Consultar"],
    ["Consumo", vehicle.consumptionRange ? `${vehicle.consumptionRange.min.toLocaleString("es-ES")}–${vehicle.consumptionRange.max.toLocaleString("es-ES")} ${vehicle.consumptionUnit}` : vehicle.consumption !== null ? `${vehicle.consumption.toLocaleString("es-ES")} ${vehicle.consumptionUnit}` : "Consultar"],
    ["Cambio", vehicle.transmission || "Consultar"],
    ["Etiqueta DGT", vehicle.label],
    ...(vehicle.trunk ? [["Maletero", `${vehicle.trunk} litros`]] : []),
    ...(vehicle.doors ? [["Puertas", String(vehicle.doors)]] : []),
    ...(vehicle.seats ? [["Plazas", String(vehicle.seats)]] : []),
    ...(vehicle.dimensions?.lengthMm ? [["Longitud", `${vehicle.dimensions.lengthMm.toLocaleString("es-ES")} mm`]] : []),
    ...(vehicle.dimensions?.widthMm ? [["Anchura", `${vehicle.dimensions.widthMm.toLocaleString("es-ES")} mm`]] : []),
    ...(vehicle.dimensions?.heightMm ? [["Altura", `${vehicle.dimensions.heightMm.toLocaleString("es-ES")} mm`]] : []),
    ...(vehicle.electricRangeKm ? [["Autonomía eléctrica", `${vehicle.electricRangeKm} km WLTP`]] : []),
    ...(vehicle.emissionsCo2Range ? [["Emisiones CO₂", `${vehicle.emissionsCo2Range.min}–${vehicle.emissionsCo2Range.max} g/km`]] : vehicle.emissionsCo2GKm !== null && vehicle.emissionsCo2GKm !== undefined ? [["Emisiones CO₂", `${vehicle.emissionsCo2GKm} g/km`]] : []),
    ...(vehicle.batteryCapacityKWh ? [["Batería", `${vehicle.batteryCapacityKWh} kWh`]] : []),
    ...(vehicle.colors?.length ? [["Colores", vehicle.colors.join(", ")]] : []),
    ...(vehicle.campaign ? [["Campaña", vehicle.campaign]] : []),
  ];

  return (
    <section aria-labelledby="datos-tecnicos">
      <div className="mb-5 flex items-end justify-between gap-4">
        <h2 id="datos-tecnicos" className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Datos técnicos</h2>
        <p className="hidden text-xs text-muted sm:block">Datos de la versión mostrada</p>
      </div>
      <dl className="grid grid-cols-2 overflow-hidden rounded-xl border border-line bg-surface sm:grid-cols-5">
        {specs.map(([label, value], index) => (
          <div key={label} className={`p-4 sm:p-5 ${index > 0 ? "border-l border-line" : ""} ${index > 1 ? "border-t sm:border-t-0" : ""}`}>
            <dt className="text-[0.625rem] font-bold tracking-[0.08em] text-muted uppercase">{label}</dt>
            <dd className="font-data mt-2 text-sm font-semibold tracking-[-0.02em] text-ink sm:text-base">{value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-3 text-[0.6875rem] leading-5 text-muted">Los datos técnicos se publican únicamente cuando constan en una fuente identificada. {vehicle.specSource ? <>Coincidencia de versión validada con <a href={vehicle.specSource.url} target="_blank" rel="noreferrer noopener" className="font-bold text-copy underline">{vehicle.specSource.publisher}</a>.</> : vehicle.sourceUrl ? <a href={vehicle.sourceUrl} target="_blank" rel="noreferrer noopener nofollow" className="font-bold text-copy underline">Consultar la fuente del vehículo</a> : "Los campos pendientes se muestran como “Consultar”."}</p>
    </section>
  );
}
