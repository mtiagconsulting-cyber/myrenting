import Link from "next/link";
import type { GeoFacts } from "@/lib/geo-facts";
import type { SeoLanding } from "@/lib/seo-landing-engine";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

const money = (value: number) => `${value.toLocaleString("es-ES", { maximumFractionDigits: 2 })} €/mes`;

function questionFor(landing: SeoLanding) {
  if (landing.type === "model") return `¿Cuánto cuesta el renting de un ${landing.dimensions.brand} ${landing.dimensions.model}?`;
  if (landing.type === "brand") return `¿Cuánto cuesta un ${landing.dimensions.brand} de renting?`;
  if (landing.type === "price") return `¿Qué coches de renting cuestan menos de ${landing.dimensions.maxPrice} € al mes?`;
  if (landing.type === "no_entry") return "¿Qué coches de renting hay sin entrada?";
  if (landing.type === "immediate") return "¿Qué coches de renting tienen entrega inmediata?";
  return `¿Qué opciones hay en ${landing.h1.toLowerCase()}?`;
}

export function QuickAnswer({ landing, facts }: { landing: SeoLanding; facts: GeoFacts }) {
  return <section aria-labelledby="respuesta-rapida" className="mt-7 max-w-4xl rounded-xl border border-orange-200 bg-orange-50 p-5 sm:p-6">
    <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Respuesta rápida</p>
    <h2 id="respuesta-rapida" className="font-display mt-2 text-xl font-semibold text-ink">{questionFor(landing)}</h2>
    <p className="mt-3 text-sm leading-7 text-copy">Actualmente MyRenting compara <strong>{facts.numberOfOffers} configuraciones</strong> de esta selección desde <strong>{money(facts.minimumPrice)}</strong>. La opción más económica es el <strong>{facts.cheapestModel}</strong>. Los precios dependen del perfil de cliente, duración y kilometraje.</p>
  </section>;
}

export function KeyFacts({ facts }: { facts: GeoFacts }) {
  const items = [
    ["Precio mínimo", money(facts.minimumPrice)], ["Precio medio", money(facts.averagePrice)],
    ["Configuraciones", facts.numberOfOffers.toLocaleString("es-ES")], ["Modelos", facts.numberOfModels.toLocaleString("es-ES")],
    ["Más económico", facts.cheapestModel], ["Automáticos", facts.automaticCount.toLocaleString("es-ES")],
    ["Híbridos", facts.hybridCount.toLocaleString("es-ES")], ["Eléctricos", facts.electricCount.toLocaleString("es-ES")],
    ["Entrega disponible", facts.immediateDeliveryCount.toLocaleString("es-ES")], ["Sin entrada", facts.noEntryCount.toLocaleString("es-ES")],
  ];
  return <section aria-labelledby="datos-clave" className="mt-10"><h2 id="datos-clave" className="font-display text-2xl font-semibold text-ink">Datos clave de esta selección</h2><dl className="mt-5 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-5">{items.map(([label, value]) => <div key={label} className="bg-surface p-4"><dt className="text-[0.6875rem] font-bold tracking-wide text-muted uppercase">{label}</dt><dd className="font-data mt-2 text-base font-semibold text-ink">{value}</dd></div>)}</dl></section>;
}

export function GeoComparisonTable({ facts }: { facts: GeoFacts }) {
  return <section aria-labelledby="comparativa-datos" className="py-12"><div className="mb-5"><h2 id="comparativa-datos" className="font-display text-3xl font-semibold text-ink">Comparativa de los modelos más económicos</h2><p className="mt-2 text-sm text-muted">Una fila por modelo, usando su configuración publicada de menor precio.</p></div><div className="overflow-x-auto rounded-xl border border-line"><table className="w-full border-collapse bg-surface text-left text-sm"><thead className="bg-slate-50 text-xs text-muted"><tr><th className="px-4 py-3">Modelo</th><th className="px-4 py-3">Desde</th><th className="px-4 py-3">Combustible</th><th className="px-4 py-3">Cambio</th><th className="px-4 py-3">Entrega</th><th className="px-4 py-3">Condiciones</th></tr></thead><tbody>{facts.ranking.map((row) => <tr key={`${row.name}-${row.price}`} className="border-t border-line"><th className="px-4 py-4 font-semibold"><Link href={row.path} className="text-ink hover:text-brand">{row.name}</Link></th><td className="font-data whitespace-nowrap px-4 py-4 font-semibold">{money(row.price)}</td><td className="px-4 py-4">{row.fuel}</td><td className="px-4 py-4">{row.transmission}</td><td className="px-4 py-4">{row.availability}</td><td className="whitespace-nowrap px-4 py-4">{row.duration} meses · {row.kilometers.toLocaleString("es-ES")} km/año</td></tr>)}</tbody></table></div></section>;
}

export type ModelOfferRow = { vehicle: Vehicle; offer: Offer };

const audienceLabel: Record<Offer["audience"], string> = {
  particular: "Particular",
  autonomo: "Autónomo",
  empresa: "Empresa",
};

function vatPrices(offer: Offer) {
  const withoutVat = offer.monthlyPriceExVat ?? (offer.priceIncludesVat ? offer.monthlyPrice / 1.21 : offer.monthlyPrice);
  const withVat = offer.monthlyPriceIncVat ?? (offer.priceIncludesVat ? offer.monthlyPrice : offer.monthlyPrice * 1.21);
  return { withoutVat, withVat };
}

export function ModelOfferComparison({ brand, model, rows }: { brand: string; model: string; rows: ModelOfferRow[] }) {
  return <section aria-labelledby="comparativa-versiones" className="py-12">
    <div className="mb-5">
      <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Versiones y condiciones</p>
      <h2 id="comparativa-versiones" className="font-display mt-2 text-3xl font-semibold text-ink">Precios de renting del {brand} {model}</h2>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">Comparamos la cuota más baja de cada versión y perfil. Se muestran el precio sin IVA y con IVA para que puedas comparar las ofertas con el mismo criterio.</p>
    </div>
    <div className="overflow-x-auto rounded-xl border border-line">
      <table className="w-full border-collapse bg-surface text-left text-sm">
        <thead className="bg-slate-50 text-xs text-muted"><tr><th className="px-4 py-3">Versión</th><th className="px-4 py-3">Perfil</th><th className="px-4 py-3">Sin IVA</th><th className="px-4 py-3">Con IVA</th><th className="px-4 py-3">Contrato</th><th className="px-4 py-3">Proveedor</th></tr></thead>
        <tbody>{rows.map(({ vehicle, offer }) => {
          const prices = vatPrices(offer);
          return <tr key={`${vehicle.id}-${offer.audience}`} className="border-t border-line align-top">
            <th className="min-w-64 px-4 py-4 font-semibold text-ink"><span className="block">{vehicle.version}</span><span className="mt-1 block text-xs font-normal text-muted">{vehicle.fuel} · {vehicle.power} CV · {vehicle.transmission || "Cambio por confirmar"}</span></th>
            <td className="px-4 py-4">{audienceLabel[offer.audience]}</td>
            <td className="font-data whitespace-nowrap px-4 py-4 font-semibold">{money(prices.withoutVat)}</td>
            <td className="font-data whitespace-nowrap px-4 py-4 font-semibold">{money(prices.withVat)}</td>
            <td className="whitespace-nowrap px-4 py-4">{offer.duration} meses<br /><span className="text-xs text-muted">{offer.kilometers.toLocaleString("es-ES")} km/año · {offer.initialPayment === 0 ? "sin entrada" : `${offer.initialPayment.toLocaleString("es-ES")} € de entrada`}</span></td>
            <td className="px-4 py-4">{offer.provider}<span className="mt-1 block text-xs text-muted">{offer.availability}</span></td>
          </tr>;
        })}</tbody>
      </table>
    </div>
    <p className="mt-3 text-xs leading-5 text-muted">Las cuotas pueden cambiar según duración, kilometraje y perfil. Confirma disponibilidad y precio final con el proveedor antes de contratar.</p>
  </section>;
}

export function GeoRanking({ facts, heading }: { facts: GeoFacts; heading: string }) {
  return <section aria-labelledby="ranking-geo" className="mb-14"><h2 id="ranking-geo" className="font-display text-3xl font-semibold text-ink">Los 5 {heading.toLowerCase()} más baratos actualmente</h2><ol className="mt-5 divide-y divide-line rounded-xl border border-line bg-surface">{facts.ranking.slice(0, 5).map((row, index) => <li key={row.name} className="flex items-center justify-between gap-4 p-4"><span className="min-w-0"><span className="mr-3 font-data text-muted">{index + 1}.</span><Link href={row.path} className="font-bold text-ink hover:text-brand">{row.name}</Link></span><strong className="font-data whitespace-nowrap text-ink">{money(row.price)}</strong></li>)}</ol></section>;
}
