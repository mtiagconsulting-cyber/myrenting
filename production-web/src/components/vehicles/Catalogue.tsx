"use client";

import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { GitCompareArrows, X } from "lucide-react";
import { Filters } from "@/components/search/Filters";
import { VehicleGrid } from "@/components/vehicles/VehicleGrid";
import { representativeVehicle, vehicleGroupKey } from "@/lib/vehicle-groups";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

type Item = { vehicle: Vehicle; offer: Offer; profileOffers?: Offer[] };

export function Catalogue({ items }: { items: Item[] }) {
  return <Suspense fallback={<div className="mt-6 rounded-xl border border-line bg-surface p-6 text-sm font-semibold text-muted">Preparando el catálogo y sus filtros…</div>}><FilteredCatalogue items={items} /></Suspense>;
}

function FilteredCatalogue({ items }: { items: Item[] }) {
  const params = useSearchParams();
  const [visibleCount, setVisibleCount] = useState(24);
  const [compared, setCompared] = useState<Vehicle[]>([]);
  const filtered = useMemo(() => {
    const selectedBrands = new Set((params.get("marca") ?? "").toLowerCase().split(",").filter(Boolean));
    const fuel = (params.get("combustible") ?? "").toLowerCase();
    const body = (params.get("carroceria") ?? "").toLowerCase();
    const budget = Number(params.get("presupuesto")) || Infinity;
    const kilometers = Number(params.get("kilometros")) || 0;
    const audience = (params.get("publico") ?? "").toLowerCase();
    const matching = items.filter(({ vehicle, offer }) =>
      (!selectedBrands.size || selectedBrands.has(vehicle.brand.toLowerCase())) &&
      (!fuel || vehicle.fuel.toLowerCase() === fuel) &&
      (!body || vehicle.bodyType.toLowerCase() === body) &&
      offer.monthlyPrice <= budget &&
      (!kilometers || offer.kilometers === kilometers) &&
      (!audience || offer.audience === audience)
    );

    // Elegimos la mejor cuota después de filtrar todas las combinaciones.
    // Si se hace antes, los tramos de kilometraje distintos al más barato
    // desaparecen aunque estén disponibles en la campaña.
    const bestByVehicleAndAudience = new Map<string, Item>();
    for (const item of matching) {
      const key = `${vehicleGroupKey(item.vehicle)}:${item.offer.audience}`;
      const current = bestByVehicleAndAudience.get(key);
      if (!current || item.offer.monthlyPrice < current.offer.monthlyPrice) {
        bestByVehicleAndAudience.set(key, item);
      }
    }
    const bestItems = [...bestByVehicleAndAudience.values()];
    if (audience) return bestItems.sort((first, second) => first.offer.monthlyPrice - second.offer.monthlyPrice);

    // Unimos los registros que los proveedores separan por tipo de cliente.
    // La identidad incluye versión, combustible y potencia, de modo que no se
    // mezclan generaciones ni motorizaciones distintas del mismo modelo.
    const groupedByVehicle = new Map<string, Item>();
    for (const item of bestItems) {
      const key = vehicleGroupKey(item.vehicle);
      const current = groupedByVehicle.get(key);
      if (!current) {
        const groupVehicles = items.filter((candidate) => vehicleGroupKey(candidate.vehicle) === key).map((candidate) => candidate.vehicle);
        groupedByVehicle.set(key, { ...item, vehicle: representativeVehicle(groupVehicles), profileOffers: [item.offer] });
        continue;
      }
      current.profileOffers = [...(current.profileOffers ?? []), item.offer].sort((first, second) => first.monthlyPrice - second.monthlyPrice);
      if (item.offer.monthlyPrice < current.offer.monthlyPrice) current.offer = item.offer;
    }
    return [...groupedByVehicle.values()].sort((first, second) => first.offer.monthlyPrice - second.offer.monthlyPrice);
  }, [items, params]);
  useEffect(() => setVisibleCount(24), [params]);

  function toggleCompare(vehicle: Vehicle) {
    setCompared((current) => current.some((item) => item.id === vehicle.id) ? current.filter((item) => item.id !== vehicle.id) : current.length < 2 ? [...current, vehicle] : [current[1], vehicle]);
  }

  return <CatalogueLayout items={filtered} visibleCount={visibleCount} setVisibleCount={setVisibleCount} compared={compared} toggleCompare={toggleCompare} />;
}

function CatalogueLayout({ items, visibleCount, setVisibleCount, compared, toggleCompare }: { items: Item[]; visibleCount: number; setVisibleCount: (value: number) => void; compared: Vehicle[]; toggleCompare: (vehicle: Vehicle) => void }) {
  const visibleItems = items.slice(0, visibleCount);
  return <>
    <div className="mt-6 flex items-center justify-between gap-4">
      <p className="text-sm text-muted"><strong className="font-data text-ink tabular-nums">{items.length}</strong> {items.length === 1 ? "coche encontrado" : "coches encontrados"}<span className="ml-2 text-xs">· Tarifas por perfil dentro de cada ficha</span></p>
      <div className="lg:hidden"><Filters /></div>
    </div>
    <div className="mt-6 grid gap-6 lg:grid-cols-[15rem_minmax(0,1fr)]">
      <div className="hidden lg:block"><Filters /></div>
      <div><VehicleGrid items={visibleItems} comparedIds={compared.map((item) => item.id)} onCompare={toggleCompare} />{visibleItems.length < items.length ? <div className="mt-8 text-center"><button type="button" onClick={() => setVisibleCount(Math.min(visibleCount + 24, items.length))} className="h-12 rounded-lg border border-ink bg-surface px-7 text-sm font-bold text-ink hover:bg-ink hover:text-white">Mostrar 24 coches más <span className="font-data text-xs text-muted">({items.length - visibleItems.length} pendientes)</span></button></div> : null}</div>
    </div>
    {compared.length ? <div className="fixed inset-x-4 bottom-4 z-50 mx-auto flex max-w-3xl items-center justify-between gap-4 rounded-xl border border-white/10 bg-ink px-4 py-3 text-white shadow-2xl sm:px-5"><div className="min-w-0"><p className="text-[0.625rem] font-bold tracking-wide text-orange-400 uppercase">Comparación rápida</p><p className="mt-1 truncate text-sm font-semibold">{compared.map((item) => `${item.brand} ${item.model}`).join(" vs ")}{compared.length === 1 ? " · elige otro coche" : ""}</p></div><div className="flex shrink-0 items-center gap-2">{compared.length === 2 ? <Link href={`/comparar/${compared[0].slug}-vs-${compared[1].slug}`} className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand px-4 text-xs font-bold text-white"><GitCompareArrows size={15} />Comparar</Link> : null}<button type="button" onClick={() => compared.forEach(toggleCompare)} className="grid size-10 place-items-center rounded-lg border border-white/20 text-slate-300 hover:text-white" aria-label="Vaciar comparación"><X size={17} /></button></div></div> : null}
  </>;
}
