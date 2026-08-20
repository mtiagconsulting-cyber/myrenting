"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { ArrowRight, GitCompareArrows } from "lucide-react";
import { vehicles } from "@/data/vehicles";

export function ComparisonSelector({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [first, setFirst] = useState("quadis-512258");
  const [second, setSecond] = useState("quadis-508905");
  const invalid = first === second;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!invalid) router.push(`/comparar/${first}-vs-${second}`);
  }

  return (
    <form onSubmit={submit} className={`grid gap-3 ${compact ? "sm:grid-cols-[1fr_auto_1fr_auto]" : "md:grid-cols-[1fr_auto_1fr_auto]"}`}>
      <VehicleSelect label="Primer coche" value={first} onChange={setFirst} />
      <span className="font-data hidden self-end pb-4 text-xs font-semibold text-muted sm:block">VS</span>
      <VehicleSelect label="Segundo coche" value={second} onChange={setSecond} />
      <button disabled={invalid} type="submit" className="mt-auto inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-bold text-white hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-45"><GitCompareArrows size={17} aria-hidden="true" />Comparar<ArrowRight size={15} aria-hidden="true" /></button>
      {invalid ? <p className="text-xs font-semibold text-red-700 sm:col-span-4">Elige dos coches diferentes.</p> : null}
    </form>
  );
}

function VehicleSelect({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label><span className="mb-2 block text-xs font-bold text-ink">{label}</span><select value={value} onChange={(event) => onChange(event.target.value)} className="h-12 w-full rounded-lg border border-line bg-surface px-3.5 text-sm font-semibold text-ink">{vehicles.map((vehicle) => <option key={vehicle.id} value={vehicle.slug}>{vehicle.brand} {vehicle.model}</option>)}</select></label>;
}
