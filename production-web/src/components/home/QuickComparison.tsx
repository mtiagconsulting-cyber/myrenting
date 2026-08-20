import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Surface } from "@/components/ui/surface";
import { getComparison, popularComparisonSlugs } from "@/lib/comparison";

export function QuickComparison() {
  const comparison = getComparison(popularComparisonSlugs[0]);
  if (!comparison) return null;
  const cars = [comparison.first, comparison.second];
  const lowerPrice = Math.min(...cars.map(({ offer }) => offer.monthlyPrice));
  return (
    <Surface className="overflow-hidden">
      <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]">
        {cars.map(({ vehicle, offer }) => (
          <div key={vehicle.id} className="p-5 sm:p-7">
            <Badge tone={offer.monthlyPrice === lowerPrice ? "brand" : "neutral"}>{offer.monthlyPrice === lowerPrice ? "Menor cuota" : `${offer.duration} meses`}</Badge>
            <p className="mt-5 text-xs font-bold text-muted">{vehicle.brand}</p>
            <h3 className="font-display mt-1 text-2xl font-semibold tracking-[-0.04em] text-ink sm:text-3xl">{vehicle.model}</h3>
            <p className="font-data mt-4 text-3xl font-semibold tracking-[-0.06em] text-ink tabular-nums">
              {offer.monthlyPrice} €<span className="font-sans text-xs font-semibold tracking-normal text-muted">/mes</span>
            </p>
            <div className="mt-5 space-y-2 text-xs text-copy">
              <p className="flex items-center gap-2"><Check size={14} className="text-positive" aria-hidden="true" />{vehicle.fuel}</p>
              <p className="flex items-center gap-2"><Check size={14} className="text-positive" aria-hidden="true" />{offer.kilometers.toLocaleString("es-ES")} km/año · {offer.priceIncludesVat ? "IVA incluido" : "+ IVA"}</p>
            </div>
          </div>
        )).flatMap((item, index) => index === 0 ? [item, <div key="versus" className="grid w-12 place-items-center border-x border-line bg-slate-50"><span className="font-data text-[0.6875rem] font-semibold text-muted">VS</span></div>] : [item])}
      </div>
      <Link href={`/comparar/${popularComparisonSlugs[0]}`} className="flex min-h-13 items-center justify-center gap-2 border-t border-line bg-slate-50 px-5 text-sm font-bold text-ink transition-colors hover:bg-slate-100">
        Ver todas las diferencias <ArrowRight size={16} aria-hidden="true" />
      </Link>
    </Surface>
  );
}
