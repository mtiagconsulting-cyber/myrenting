"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useId, useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";
import { brands } from "@/data/vehicles";

const fuels = ["Híbrido", "Híbrido enchufable", "Eléctrico", "Gasolina", "Diésel"];
const bodies = ["SUV", "Compacto", "Berlina", "Furgoneta"];
const audiences = [["particular", "Particular"], ["autonomo", "Autónomo"], ["empresa", "Empresa"]];

export function Filters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [open, setOpen] = useState(false);
  const instanceId = useId();

  function update(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    router.push(`/coches?${params.toString()}`, { scroll: false });
  }

  function toggleBrand(value: string) {
    const selected = new Set((searchParams.get("marca") ?? "").split(",").filter(Boolean));
    if (selected.has(value)) selected.delete(value);
    else selected.add(value);
    update("marca", [...selected].join(","));
  }

  const content = (scope: "desktop" | "mobile") => (
    <div className="space-y-7">
      <FilterGroup label="Perfil" name="publico" inputName={`publico-${instanceId}-${scope}`} values={audiences} current={searchParams.get("publico") ?? ""} update={update} />
      <MultiFilterGroup label="Marca" values={brands.map((brand) => [brand.toLowerCase(), brand])} current={(searchParams.get("marca") ?? "").split(",").filter(Boolean)} toggle={toggleBrand} />
      <FilterGroup label="Combustible" name="combustible" inputName={`combustible-${instanceId}-${scope}`} values={fuels.map((fuel) => [fuel.toLowerCase(), fuel])} current={searchParams.get("combustible") ?? ""} update={update} />
      <FilterGroup label="Tipo de coche" name="carroceria" inputName={`carroceria-${instanceId}-${scope}`} values={bodies.map((body) => [body.toLowerCase(), body])} current={searchParams.get("carroceria") ?? ""} update={update} />
      <label className="block">
        <span className="text-xs font-bold tracking-wide text-ink uppercase">Cuota máxima</span>
        <select value={searchParams.get("presupuesto") ?? ""} onChange={(event) => update("presupuesto", event.target.value)} className="mt-3 h-11 w-full rounded-lg border border-line bg-surface px-3 text-sm font-semibold text-ink">
          <option value="">Cualquier cuota</option><option value="300">Hasta 300 €</option><option value="400">Hasta 400 €</option><option value="500">Hasta 500 €</option><option value="700">Hasta 700 €</option>
        </select>
      </label>
      <label className="block">
        <span className="text-xs font-bold tracking-wide text-ink uppercase">Kilómetros al año</span>
        <select value={searchParams.get("kilometros") ?? ""} onChange={(event) => update("kilometros", event.target.value)} className="mt-3 h-11 w-full rounded-lg border border-line bg-surface px-3 text-sm font-semibold text-ink">
          <option value="">Cualquier kilometraje</option><option value="10000">10.000 km</option><option value="15000">15.000 km</option><option value="20000">20.000 km</option><option value="25000">25.000 km</option><option value="30000">30.000 km</option>
        </select>
      </label>
      <button type="button" onClick={() => router.push("/coches")} className="text-xs font-bold text-brand hover:underline">Limpiar todos los filtros</button>
    </div>
  );

  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className="inline-flex h-11 items-center gap-2 rounded-lg border border-line bg-surface px-4 text-sm font-bold text-ink lg:hidden"><SlidersHorizontal size={17} aria-hidden="true" />Filtros</button>
      <aside className="hidden rounded-xl border border-line bg-surface p-5 lg:block" aria-label="Filtros">{content("desktop")}</aside>
      {open ? <div className="fixed inset-0 z-[80] bg-ink/30 lg:hidden"><aside className="absolute inset-y-0 right-0 w-[min(90%,24rem)] overflow-y-auto bg-surface p-5 shadow-2xl" aria-label="Filtros móviles"><div className="mb-7 flex items-center justify-between border-b border-line pb-4"><h2 className="font-display text-xl font-semibold text-ink">Filtrar coches</h2><button type="button" onClick={() => setOpen(false)} className="grid size-10 place-items-center rounded-lg hover:bg-slate-100" aria-label="Cerrar filtros"><X size={20} aria-hidden="true" /></button></div>{content("mobile")}<button type="button" onClick={() => setOpen(false)} className="mt-8 h-12 w-full rounded-lg bg-brand text-sm font-bold text-white">Ver resultados</button></aside></div> : null}
    </>
  );
}

function FilterGroup({ label, name, inputName, values, current, update }: { label: string; name: string; inputName: string; values: string[][]; current: string; update: (key: string, value: string) => void }) {
  return <fieldset><legend className="text-xs font-bold tracking-wide text-ink uppercase">{label}</legend><div className="mt-3 space-y-2.5">{values.map(([value, text]) => <label key={value} className="flex cursor-pointer items-center gap-3 text-sm text-copy"><input type="radio" name={inputName} value={value} checked={current === value} onClick={(event) => { if (current === value) { event.preventDefault(); update(name, ""); } }} onChange={() => { if (current !== value) update(name, value); }} className="size-4 accent-orange-600" />{text}</label>)}</div></fieldset>;
}

function MultiFilterGroup({ label, values, current, toggle }: { label: string; values: string[][]; current: string[]; toggle: (value: string) => void }) {
  const selected = new Set(current);
  return <fieldset><legend className="flex w-full items-center justify-between text-xs font-bold tracking-wide text-ink uppercase"><span>{label}</span>{selected.size ? <span className="rounded-full bg-orange-100 px-2 py-0.5 font-data text-[0.625rem] text-orange-700">{selected.size}</span> : null}</legend><p className="mt-2 text-[0.6875rem] leading-4 text-muted">Puedes elegir varias marcas</p><div className="mt-3 max-h-64 space-y-2.5 overflow-y-auto pr-1">{values.map(([value, text]) => <label key={value} className="flex cursor-pointer items-center gap-3 text-sm text-copy"><input type="checkbox" value={value} checked={selected.has(value)} onChange={() => toggle(value)} className="size-4 rounded accent-orange-600" />{text}</label>)}</div></fieldset>;
}
