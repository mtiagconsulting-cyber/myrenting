import type { Metadata } from "next";
import { Catalogue } from "@/components/vehicles/Catalogue";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";

export const metadata: Metadata = { title: "Buscador de coches de renting", description: "Filtra coches de renting por cuota, combustible, carrocería y condiciones.", alternates: { canonical: "/renting" }, robots: { index: false, follow: true } };

export default function CarsPage() {
  const items = offers.flatMap((offer) => {
    const vehicle = vehicles.find((candidate) => candidate.id === offer.vehicleId);
    if (!vehicle) return [];
    return [{ vehicle, offer }];
  });

  return (
    <main id="contenido-principal" className="mx-auto max-w-7xl px-5 py-9 sm:px-8 sm:py-12">
      <div className="border-b border-line pb-7">
        <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Inventario verificado</p>
        <h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.045em] text-ink">Coches de renting</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">Compara ofertas reales para particulares, autónomos y empresas. Indicamos si la cuota incluye IVA para evitar comparaciones engañosas.</p>
      </div>

      <Catalogue items={items} />
    </main>
  );
}
