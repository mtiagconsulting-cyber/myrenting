"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { ChevronDown, Search } from "lucide-react";

const fieldClassName =
  "h-12 w-full appearance-none rounded-lg border border-line bg-surface px-3.5 pr-10 text-sm font-semibold text-ink outline-none transition-colors hover:border-slate-300 focus:border-brand";

export function SearchEngine({ brands }: { brands: string[] }) {
  const router = useRouter();
  const [brand, setBrand] = useState("");
  const [budget, setBudget] = useState("");
  const [kilometers, setKilometers] = useState("");
  const [audience, setAudience] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams();

    if (brand) params.set("marca", brand);
    if (budget) params.set("presupuesto", budget);
    if (kilometers) params.set("kilometros", kilometers);
    if (audience) params.set("publico", audience);

    router.push(`/coches?${params.toString()}`);
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[1.3fr_0.9fr_0.9fr_0.9fr_auto]" aria-label="Buscar ofertas de renting">
      <label className="block">
        <span className="mb-2 block text-xs font-bold text-ink">Marca o modelo</span>
        <span className="relative block">
          <select className={fieldClassName} value={brand} onChange={(event) => setBrand(event.target.value)}>
            <option value="">Todas las marcas</option>
            {brands.map((item) => <option key={item} value={item.toLowerCase()}>{item}</option>)}
          </select>
          <ChevronDown className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-muted" size={17} aria-hidden="true" />
        </span>
      </label>

      <label className="block">
        <span className="mb-2 block text-xs font-bold text-ink">Tipo de cliente</span>
        <span className="relative block">
          <select className={fieldClassName} value={audience} onChange={(event) => setAudience(event.target.value)}>
            <option value="">Todos los perfiles</option>
            <option value="particular">Particular</option>
            <option value="autonomo">Autónomo</option>
            <option value="empresa">Empresa</option>
          </select>
          <ChevronDown className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-muted" size={17} aria-hidden="true" />
        </span>
      </label>

      <label className="block">
        <span className="mb-2 block text-xs font-bold text-ink">Presupuesto mensual</span>
        <span className="relative block">
          <select className={fieldClassName} value={budget} onChange={(event) => setBudget(event.target.value)}>
            <option value="">Sin límite</option>
            <option value="300">Hasta 300 €</option>
            <option value="400">Hasta 400 €</option>
            <option value="500">Hasta 500 €</option>
            <option value="700">Hasta 700 €</option>
          </select>
          <ChevronDown className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-muted" size={17} aria-hidden="true" />
        </span>
      </label>

      <label className="block">
        <span className="mb-2 block text-xs font-bold text-ink">Kilómetros al año</span>
        <span className="relative block">
          <select className={fieldClassName} value={kilometers} onChange={(event) => setKilometers(event.target.value)}>
            <option value="">Cualquier kilometraje</option>
            <option value="10000">10.000 km</option>
            <option value="15000">15.000 km</option>
            <option value="20000">20.000 km</option>
            <option value="25000">25.000 km</option>
            <option value="30000">30.000 km</option>
          </select>
          <ChevronDown className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-muted" size={17} aria-hidden="true" />
        </span>
      </label>

      <button type="submit" className="mt-auto inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-brand px-6 text-sm font-bold text-white transition-colors hover:bg-brand-hover">
        <Search size={18} strokeWidth={2.3} aria-hidden="true" />
        Buscar ofertas
      </button>
    </form>
  );
}
