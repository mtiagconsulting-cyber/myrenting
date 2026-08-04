import { Suspense } from "react";
import Link from "next/link";
import VehicleListing from "@/components/vehicles/VehicleListing";
import { vehicles } from "@/data/vehicles";

export const metadata = {
  title: `Renting de coches en España — ${vehicles.length} modelos comparados`,
  description:
    "Compara modelos de renting de varias gestoras. Filtra por combustible, etiqueta DGT, carrocería y precio. Cuotas reales, sin entrada.",
};

export default function Coches() {
  return (
    <div className="mx-auto max-w-[1200px] px-6">
      <div className="pb-2 pt-6 text-[12.5px] text-muted">
        <Link href="/">Inicio</Link> › <b className="text-ink">Coches</b>
      </div>
      <h1 className="text-[34px] font-extrabold tracking-tight text-ink">Renting de coches en España</h1>
      <div className="mt-3.5 max-w-[74ch] rounded-xl2 border border-line border-l-[3px] border-l-orange bg-white px-[18px] py-3.5 text-[15px] text-ink">
        Comparamos <b>{vehicles.length} modelos</b> de gestoras oficiales. Cuotas reales, con seguro y
        mantenimiento incluidos y sin entrada.
      </div>
      <Suspense fallback={<div className="py-16 text-center text-muted">Cargando coches…</div>}>
        <VehicleListing />
      </Suspense>
    </div>
  );
}
