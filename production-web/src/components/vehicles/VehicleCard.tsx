import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { FavoriteButton } from "@/components/vehicles/FavoriteButton";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";
import { vehiclePublicPath } from "@/lib/vehicle-groups";

export function VehicleCard({ vehicle, offer, compared = false, onCompare }: { vehicle: Vehicle; offer: Offer; profileOffers?: Offer[]; compared?: boolean; onCompare?: (vehicle: Vehicle) => void }) {
  const priceExVat = offer.monthlyPriceExVat ?? offer.monthlyPrice / (offer.priceIncludesVat ? 1.21 : 1);
  const priceIncVat = offer.monthlyPriceIncVat ?? offer.monthlyPrice * (offer.priceIncludesVat ? 1 : 1.21);
  return (
    <article className="group overflow-hidden rounded-xl border border-line bg-surface shadow-card transition-shadow hover:shadow-lg">
      <div className="relative aspect-[16/10] overflow-hidden bg-slate-100">
        {vehicle.images ? <Image src={vehicle.images.card} alt="Imagen editorial de automóvil" fill sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw" className="object-cover transition duration-500 group-hover:scale-[1.02]" /> : <div className="grid h-full place-items-center bg-[linear-gradient(135deg,#f8fafc,#e2e8f0)] px-6 text-center"><p className="font-display text-3xl font-semibold tracking-[-0.05em] text-slate-500">{vehicle.brand}<br />{vehicle.model}</p></div>}
        <div className="absolute top-3 left-3 flex gap-2">
          <Badge tone={offer.availability === "Disponible" ? "positive" : "neutral"}>{offer.availability}</Badge>
          <Badge>{vehicle.label}</Badge>
        </div>
        <FavoriteButton vehicleId={vehicle.id} vehicleName={`${vehicle.brand} ${vehicle.model}`} className="absolute top-3 right-3" />
        {onCompare ? <button type="button" onClick={() => onCompare(vehicle)} className={`absolute right-3 bottom-3 rounded-lg border px-3 py-2 text-[0.6875rem] font-bold shadow-sm transition ${compared ? "border-brand bg-brand text-white" : "border-white/80 bg-white/95 text-ink hover:border-brand"}`} aria-pressed={compared}>{compared ? "Seleccionado" : "Comparar"}</button> : null}
        {vehicle.images ? <p className="absolute bottom-2 left-3 rounded bg-ink/80 px-2 py-1 text-[0.625rem] text-white">Imagen editorial</p> : null}
      </div>

      <div className="p-5">
        <div className="flex items-center justify-between gap-3"><p className="text-xs font-bold text-muted">{vehicle.brand}</p>{offer.verifiedAt ? <time dateTime={offer.verifiedAt} className="text-[0.625rem] font-semibold text-positive">Actualizada {new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "short" }).format(new Date(offer.verifiedAt))}</time> : <span className="text-[0.625rem] font-semibold text-amber-700">Confirmar vigencia</span>}</div>
        <h2 className="font-display mt-1 text-2xl font-semibold tracking-[-0.04em] text-ink">{vehicle.model}</h2>
        <p className="mt-1 min-h-10 text-xs leading-5 text-muted">{vehicle.version}</p>

        <div className="mt-5 grid grid-cols-3 divide-x divide-line border-y border-line py-4">
          <div className="pr-3"><p className="text-[0.625rem] font-bold text-muted uppercase">Motor</p><p className="mt-1 text-xs font-bold text-ink">{vehicle.fuel}</p></div>
          <div className="px-3"><p className="text-[0.625rem] font-bold text-muted uppercase">Potencia</p><p className="font-data mt-1 text-xs font-semibold text-ink">{vehicle.power} CV</p></div>
          <div className="pl-3"><p className="text-[0.625rem] font-bold text-muted uppercase">Cambio</p><p className="font-data mt-1 text-xs font-semibold text-ink">{vehicle.transmission || "Consultar"}</p></div>
        </div>

        <div className="mt-5 flex items-end justify-between gap-4">
          <div className="grid gap-2">
            <div><p className="text-[0.625rem] font-bold tracking-wide text-muted uppercase">Sin IVA</p><p className="font-data mt-0.5 text-2xl font-semibold tracking-[-0.05em] text-ink tabular-nums">{priceExVat.toLocaleString("es-ES", { maximumFractionDigits: 2 })} €<span className="font-sans text-xs font-semibold tracking-normal text-muted">/mes</span></p></div>
            <div><p className="text-[0.625rem] font-bold tracking-wide text-muted uppercase">Con IVA</p><p className="font-data mt-0.5 text-lg font-semibold text-copy tabular-nums">{priceIncVat.toLocaleString("es-ES", { maximumFractionDigits: 2 })} €<span className="font-sans text-xs font-semibold text-muted">/mes</span></p></div>
          </div>
          <p className="text-right text-[0.6875rem] leading-5 text-muted">{offer.initialPayment === 0 ? "Sin entrada" : `${offer.initialPayment.toLocaleString("es-ES")} € de entrada`}<br />{offer.kilometers.toLocaleString("es-ES")} km/año</p>
        </div>

        <div className="mt-4 flex items-center gap-2 text-[0.6875rem] font-semibold text-positive"><Check size={14} aria-hidden="true" />{offer.insurance && offer.maintenance ? "Seguro y mantenimiento incluidos" : "Consulta las coberturas de la oferta"}</div>

        <Link href={`${vehiclePublicPath(vehicle)}?publico=${offer.audience}`} className="mt-5 flex min-h-11 items-center justify-between rounded-lg bg-ink px-4 text-sm font-bold text-white transition-colors hover:bg-copy">
          Ver oferta y condiciones <ArrowRight size={16} aria-hidden="true" />
        </Link>
      </div>
    </article>
  );
}
