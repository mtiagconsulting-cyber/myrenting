import Image from "next/image";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import type { VehicleComparison } from "@/types/comparison";
import { vehiclePublicPath } from "@/lib/vehicle-groups";

export function ComparisonHeader({ comparison }: { comparison: VehicleComparison }) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_2.5rem_minmax(0,1fr)] overflow-hidden rounded-xl border border-line bg-surface">
      {[comparison.first, comparison.second].flatMap((side, index) => {
        const card = <article key={side.vehicle.id} className="min-w-0 p-3 sm:p-6"><div className="relative aspect-[16/10] overflow-hidden rounded-lg bg-slate-100">{side.vehicle.images ? <Image src={side.vehicle.images.compare} alt="Imagen editorial de automóvil" fill sizes="(max-width: 768px) 50vw, 40vw" className="object-cover" /> : <div className="grid h-full place-items-center px-3 text-center font-display text-xl font-semibold text-slate-500">{side.vehicle.brand} {side.vehicle.model}</div>}<Badge className="absolute top-2 left-2">{side.vehicle.label}</Badge></div><p className="mt-4 text-[0.6875rem] font-bold text-muted">{side.vehicle.brand}</p><h2 className="font-display mt-1 truncate text-xl font-semibold tracking-[-0.04em] text-ink sm:text-3xl">{side.vehicle.model}</h2><p className="font-data mt-3 text-2xl font-semibold tracking-[-0.06em] text-ink sm:text-4xl">{side.offer.monthlyPrice} €<span className="font-sans text-[0.625rem] font-semibold tracking-normal text-muted sm:text-xs">/mes</span></p><Link href={vehiclePublicPath(side.vehicle)} className="mt-4 inline-block text-xs font-bold text-brand hover:underline">Ver ficha completa</Link></article>;
        return index === 0 ? [card, <div key="vs" className="grid place-items-center border-x border-line bg-slate-50"><span className="font-data text-[0.625rem] font-semibold text-muted sm:text-xs">VS</span></div>] : [card];
      })}
    </div>
  );
}
