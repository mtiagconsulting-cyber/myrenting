import Image from "next/image";
import { Suspense } from "react";
import { ImageOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { OfferConfigurator } from "@/components/vehicles/OfferConfigurator";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export function VehicleDetail({ vehicle, offer, offers, summary }: { vehicle: Vehicle; offer: Offer; offers: Offer[]; summary: string }) {
  return (
    <section className="grid gap-7 lg:grid-cols-[1.25fr_0.75fr] lg:items-start">
      <div>
        <div className="mb-5 flex flex-wrap items-center gap-2"><Badge tone="brand">{vehicle.fuel}</Badge><Badge>{vehicle.bodyType}</Badge><Badge>{vehicle.label}</Badge></div>
        <p className="text-sm font-bold text-muted">{vehicle.brand}</p>
        <h1 className="font-display mt-1 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">{vehicle.model}</h1>
        <p className="mt-3 text-sm font-semibold text-copy">{vehicle.version}</p>
        <p className="mt-5 max-w-2xl text-base leading-7 text-muted">{summary}</p>

        {vehicle.images ? <div className="relative mt-7 aspect-[16/9] overflow-hidden rounded-xl bg-slate-100"><Image src={vehicle.images.hero} alt={`${vehicle.brand} ${vehicle.model}`} fill priority sizes="(max-width: 1024px) 100vw, 65vw" className="object-cover" /></div> : <div className="mt-7 grid aspect-[16/7] place-items-center rounded-xl border border-line bg-[linear-gradient(135deg,#f8fafc,#e2e8f0)] text-center"><div><ImageOff className="mx-auto mb-4 text-slate-400" size={28} aria-hidden="true" /><p className="font-display text-4xl font-semibold text-slate-500">{vehicle.brand} {vehicle.model}</p><p className="mt-2 text-xs font-semibold text-muted">Imagen oficial pendiente de autorización</p></div></div>}
      </div>
      <Suspense fallback={<div className="min-h-96 rounded-xl border border-line bg-surface p-7 shadow-card"><p className="text-sm font-semibold text-muted">Preparando las combinaciones disponibles…</p></div>}>
        <OfferConfigurator vehicle={vehicle} offers={offers} initialOffer={offer} />
      </Suspense>
    </section>
  );
}
