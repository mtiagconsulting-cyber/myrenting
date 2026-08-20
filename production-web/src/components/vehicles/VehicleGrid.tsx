import { VehicleCard } from "@/components/vehicles/VehicleCard";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export function VehicleGrid({ items, comparedIds = [], onCompare }: { items: Array<{ vehicle: Vehicle; offer: Offer; profileOffers?: Offer[] }>; comparedIds?: string[]; onCompare?: (vehicle: Vehicle) => void }) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-surface px-6 py-16 text-center">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-ink">No hay ofertas con estos filtros</h2>
        <p className="mt-2 text-sm text-muted">Amplía el presupuesto o elimina algún filtro para ver más coches.</p>
      </div>
    );
  }

  return <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">{items.map(({ vehicle, offer, profileOffers }) => <VehicleCard key={profileOffers?.length ? vehicle.id : offer.id} vehicle={vehicle} offer={offer} profileOffers={profileOffers} compared={comparedIds.includes(vehicle.id)} onCompare={onCompare} />)}</div>;
}
