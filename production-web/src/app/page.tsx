import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, CalendarClock, GitCompareArrows, ShieldCheck } from "lucide-react";
import { CategoryGrid } from "@/components/home/CategoryGrid";
import { QuickComparison } from "@/components/home/QuickComparison";
import { SearchEngine } from "@/components/search/SearchEngine";
import { VehicleCard } from "@/components/vehicles/VehicleCard";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { brands } from "@/data/vehicles";
import { getComparison, popularComparisonSlugs } from "@/lib/comparison";
import { canonicalVehicles, vehicleModelKey } from "@/lib/vehicle-groups";

export const metadata: Metadata = {
  title: "Renting de coches para particulares, autónomos y empresas | MyRenting",
  description: `Compara ${vehicles.length} vehículos y ${offers.length.toLocaleString("es-ES")} combinaciones reales de renting por cuota, plazo, kilómetros, IVA y coberturas en España.`,
  alternates: { canonical: "/" },
  openGraph: { title: "Renting de coches con cuotas y condiciones claras | MyRenting", description: "Compara ofertas para particulares, autónomos y empresas por precio, plazo, kilómetros, IVA y servicios incluidos.", url: "/" },
};

export default function HomePage() {
  const popularComparisons = popularComparisonSlugs.map((slug) => ({ slug, comparison: getComparison(slug) })).filter((item) => item.comparison !== null);
  const cheapestVehicles = canonicalVehicles(vehicles).flatMap((vehicle) => {
    const modelKey = vehicleModelKey(vehicle);
    const modelVehicles = vehicles.filter((item) => vehicleModelKey(item) === modelKey);
    const groupIds = new Set(modelVehicles.map((item) => item.id));
    const groupOffers = offers.filter((offer) => groupIds.has(offer.vehicleId));
    if (!groupOffers.length) return [];
    const offer = [...groupOffers].sort((first, second) => (first.monthlyPriceExVat ?? first.monthlyPrice / (first.priceIncludesVat ? 1.21 : 1)) - (second.monthlyPriceExVat ?? second.monthlyPrice / (second.priceIncludesVat ? 1.21 : 1)))[0];
    const selectedVehicle = modelVehicles.find((item) => item.id === offer.vehicleId) ?? vehicle;
    return [{ vehicle: selectedVehicle, offer }];
  }).sort((first, second) => (first.offer.monthlyPriceExVat ?? first.offer.monthlyPrice) - (second.offer.monthlyPriceExVat ?? second.offer.monthlyPrice)).slice(0, 6);
  return (
    <main id="contenido-principal">
      <section className="border-b border-line bg-surface">
        <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14 lg:py-18">
          <div className="max-w-3xl">
            <p className="mb-4 text-xs font-bold tracking-[0.12em] text-brand uppercase">Comparador independiente</p>
            <h1 className="font-display text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Encuentra tu renting ideal</h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-muted sm:text-lg">
              Comparamos ofertas reales, condiciones y vehículos para ayudarte a elegir mejor.
            </p>
          </div>

          <div className="mt-8 rounded-xl border border-line bg-canvas p-4 shadow-card sm:p-6">
            <SearchEngine brands={brands} />
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 border-t border-line pt-4 text-xs font-semibold text-muted">
              <span className="inline-flex items-center gap-2"><ShieldCheck size={15} className="text-positive" aria-hidden="true" />Condiciones transparentes</span>
              <span className="inline-flex items-center gap-2"><GitCompareArrows size={15} aria-hidden="true" />Compara cuota y entrada</span>
              <span className="inline-flex items-center gap-2"><CalendarClock size={15} aria-hidden="true" />Inventario verificado</span>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl space-y-16 px-5 py-12 sm:px-8 sm:py-16 lg:space-y-22">
        <nav aria-label="Búsquedas frecuentes" className="flex flex-wrap gap-2">{[{label:"Sin entrada",href:"/renting/sin-entrada"},{label:"Menos de 300 €",href:"/renting/menos-de-300-euros"},{label:"Menos de 500 €",href:"/renting/menos-de-500-euros"},{label:"Para autónomos",href:"/renting/autonomos"},{label:"Entrega disponible",href:"/renting/entrega-inmediata"}].map((item)=><Link key={item.href} href={item.href} className="rounded-full border border-line bg-surface px-4 py-2.5 text-xs font-bold text-copy hover:border-brand hover:text-brand">{item.label}</Link>)}</nav>
        <section>
          <div className="mb-7 flex items-end justify-between gap-5">
            <div>
              <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Cuotas más bajas</p>
              <h2 className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink">Los coches de renting más baratos</h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">Las cuotas más competitivas del inventario, ordenadas por precio con IVA y sin IVA.</p>
            </div>
            <Link href="/coches" className="hidden items-center gap-2 text-sm font-bold text-ink sm:flex">Ver coches <ArrowRight size={16} aria-hidden="true" /></Link>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {cheapestVehicles.map((item) => <VehicleCard key={item.vehicle.id} vehicle={item.vehicle} offer={item.offer} />)}
          </div>
          <Link href="/coches" className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-lg bg-brand px-5 text-sm font-bold text-white hover:bg-brand-hover">Ver todos los coches <ArrowRight size={16} aria-hidden="true" /></Link>
        </section>
        <section className="grid gap-7 lg:grid-cols-[0.58fr_1fr] lg:items-start">
          <div className="lg:sticky lg:top-26">
            <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Comparativa rápida</p>
            <h2 className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink">Dos compactos disponibles, dos cuotas reales</h2>
            <p className="mt-4 max-w-md text-sm leading-6 text-muted">Compara precio, plazo, kilometraje e IVA con datos actuales del proveedor.</p>
          </div>
          <QuickComparison />
        </section>

        <section>
          <div className="mb-7 flex items-end justify-between gap-5">
            <div>
              <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Explorar por uso</p>
              <h2 className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink">¿Qué tipo de coche necesitas?</h2>
            </div>
            <Link href="/coches" className="hidden items-center gap-2 text-sm font-bold text-ink sm:flex">Ver todos <ArrowRight size={16} aria-hidden="true" /></Link>
          </div>
          <CategoryGrid />
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_0.7fr]">
          <div>
            <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Comparativas populares</p>
            <h2 className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink">Las decisiones que más se repiten</h2>
            <div className="mt-7 divide-y divide-line border-y border-line">
              {popularComparisons.map(({ slug, comparison }) => comparison && (
                <Link key={slug} href={`/comparar/${slug}`} className="group grid grid-cols-[1fr_auto_1fr_auto] items-center gap-3 py-5 text-sm font-bold text-ink">
                  <span>{comparison.first.vehicle.brand} {comparison.first.vehicle.model}</span><span className="font-data text-[0.625rem] text-muted">VS</span><span>{comparison.second.vehicle.brand} {comparison.second.vehicle.model}</span><ArrowRight size={17} className="transition-transform group-hover:translate-x-1" aria-hidden="true" />
                </Link>
              ))}
            </div>
          </div>

          <aside className="rounded-xl bg-ink p-6 text-white sm:p-8">
            <p className="text-xs font-bold tracking-[0.1em] text-orange-400 uppercase">Datos MyRenting</p>
            <div className="mt-6 divide-y divide-white/15">
              <div className="flex items-end justify-between py-5"><span className="text-sm text-slate-300">Modelos analizados</span><strong className="font-data text-3xl tracking-[-0.06em]">{vehicles.length}</strong></div>
              <div className="flex items-end justify-between py-5"><span className="text-sm text-slate-300">Combinaciones de cuota</span><strong className="font-data text-3xl tracking-[-0.06em]">{offers.length}</strong></div>
              <div className="flex items-end justify-between py-5"><span className="text-sm text-slate-300">Perfiles diferenciados</span><strong className="font-display text-xl">3</strong></div>
            </div>
            <p className="mt-5 text-xs leading-5 text-slate-400">Inventario conciliado con M‑Renting, Quadis y la oferta adicional de Kia.</p>
          </aside>
        </section>
      </div>
    </main>
  );
}
