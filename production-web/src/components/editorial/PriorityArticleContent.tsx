import Link from "next/link";
import { VehicleGrid } from "@/components/vehicles/VehicleGrid";
import { offers, inventoryUpdatedAt } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { canonicalVehicles, vehiclesInSameGroup } from "@/lib/vehicle-groups";

const targets: Record<string, {
  eyebrow: string;
  title: string;
  contentHeading: string;
  description: string;
  categoryHref: string;
  categoryLabel: string;
  filter?: (vehicle: (typeof vehicles)[number]) => boolean;
}> = {
  "renting-electrico-2026.html": {
    eyebrow: "Ofertas eléctricas actualizadas",
    title: "Renting eléctrico 2026: ofertas, precios y cómo elegir",
    contentHeading: "Qué eléctrico elegir en renting en 2026",
    description: "Compara primero cuota, autonomía adecuada para tus trayectos, acceso a carga y kilometraje anual. El inventario inferior se recalcula con las campañas activas.",
    categoryHref: "/renting/electricos",
    categoryLabel: "Ver todos los eléctricos",
    filter: (vehicle) => vehicle.fuel === "Eléctrico",
  },
  "renting-barato-2026.html": {
    eyebrow: "Guía para ahorrar",
    title: "Renting barato 2026: ofertas reales y cómo comparar",
    contentHeading: "Cómo encontrar un renting barato sin comparar cuotas engañosas",
    description: "Una cuota baja solo es realmente barata cuando comparas el mismo perfil, IVA, entrada, duración y kilómetros. Estas son las opciones activas de menor precio.",
    categoryHref: "/renting/menos-de-300-euros",
    categoryLabel: "Ver renting por menos de 300 €",
  },
  "mejores-coches-renting-2026.html": {
    eyebrow: "Selección por calidad y precio",
    title: "Mejores coches de renting en 2026: selección y ofertas",
    contentHeading: "Los coches de renting que conviene comparar en 2026",
    description: "No existe un único coche mejor para todos. Esta selección prioriza cuotas competitivas y permite continuar hacia el inventario real para revisar versión, plazo, kilometraje e IVA.",
    categoryHref: "/renting",
    categoryLabel: "Comparar todos los coches",
  },
  "que-incluye-renting-coche.html": {
    eyebrow: "Condiciones del contrato",
    title: "Qué incluye el renting de un coche: coberturas y gastos",
    contentHeading: "Qué suele incluir la cuota de renting",
    description: "La cobertura exacta depende de cada campaña. Antes de contratar, revisa seguro, mantenimiento, neumáticos, asistencia, entrada, kilometraje y posibles penalizaciones.",
    categoryHref: "/preguntas-frecuentes",
    categoryLabel: "Consultar preguntas frecuentes",
  },
};

export function priorityArticleMetadata(slug: string) {
  const target = targets[slug];
  if (!target) return null;
  return {
    title: target.title,
    description: target.description,
  };
}

export function PriorityArticleContent({ slug }: { slug: string }) {
  const target = targets[slug];
  if (!target) return null;
  const candidates = target.filter ? vehicles.filter(target.filter) : vehicles;
  const listings = canonicalVehicles(candidates).flatMap((vehicle) => {
    const ids = new Set(vehiclesInSameGroup(vehicle, candidates).map((item) => item.id));
    const offer = offers.filter((item) => ids.has(item.vehicleId)).sort((a, b) => a.monthlyPrice - b.monthlyPrice)[0];
    return offer ? [{ vehicle, offer }] : [];
  }).sort((a, b) => a.offer.monthlyPrice - b.offer.monthlyPrice).slice(0, 6);
  const updated = new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "long", year: "numeric" }).format(new Date(inventoryUpdatedAt));

  return <>
    <section className="mx-auto max-w-4xl px-5 pt-10 sm:px-8 sm:pt-14">
      <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">{target.eyebrow}</p>
      <h2 className="font-display mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink sm:text-4xl">{target.contentHeading}</h2>
      <p className="mt-4 text-base leading-7 text-muted">{target.description}</p>
      <div className="mt-6 grid gap-3 rounded-xl border border-line bg-surface p-5 text-sm leading-6 text-copy sm:grid-cols-2">
        <p><strong className="text-ink">Compara condiciones equivalentes.</strong> El precio cambia según perfil, IVA, plazo, kilómetros y entrada.</p>
        <p><strong className="text-ink">Confirma la disponibilidad.</strong> El stock y las campañas pueden cambiar antes de formalizar el contrato.</p>
      </div>
      <p className="mt-4 text-xs text-muted">Ofertas revisadas el <time dateTime={inventoryUpdatedAt}>{updated}</time>.</p>
    </section>
    {slug === "que-incluye-renting-coche.html" ? <IncludedGuide /> : <section className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><h2 className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Ofertas reales para comparar</h2><p className="mt-2 text-sm text-muted">Ordenadas por la cuota publicada más baja, sin ocultar el perfil ni el tratamiento del IVA.</p></div><Link href={target.categoryHref} className="rounded-lg bg-brand px-5 py-3 text-sm font-bold text-white hover:bg-brand-hover">{target.categoryLabel}</Link></div>
      <VehicleGrid items={listings} />
    </section>}
    <section className="mx-auto mb-14 max-w-4xl px-5 sm:px-8"><div className="rounded-xl bg-ink p-6 text-white sm:flex sm:items-center sm:justify-between sm:gap-6"><div><h2 className="font-display text-2xl font-semibold">Continúa con ofertas disponibles</h2><p className="mt-2 text-sm text-slate-300">Revisa la versión concreta, cuota, entrada, plazo y kilómetros antes de solicitar información.</p></div><Link href={target.categoryHref} className="mt-5 inline-flex shrink-0 rounded-lg bg-brand px-5 py-3 text-sm font-bold text-white sm:mt-0">{target.categoryLabel}</Link></div></section>
  </>;
}

function IncludedGuide() {
  return <section className="legacy-article mx-auto max-w-4xl px-5 py-10 sm:px-8 sm:py-12">
    <h2>Servicios que debes comprobar</h2>
    <ul><li><strong>Seguro:</strong> modalidad, franquicia, conductores admitidos y exclusiones.</li><li><strong>Mantenimiento:</strong> revisiones y reparaciones cubiertas durante el contrato.</li><li><strong>Neumáticos:</strong> número de sustituciones y condiciones de desgaste.</li><li><strong>Asistencia:</strong> cobertura territorial y vehículo de sustitución.</li><li><strong>Impuestos e ITV:</strong> quién gestiona y paga cada concepto.</li></ul>
    <h2>Gastos que normalmente quedan fuera</h2>
    <p>El combustible o la recarga, las multas, los daños por uso indebido y los kilómetros excedidos suelen facturarse aparte. La cancelación anticipada también puede tener penalización.</p>
    <h2>Qué comparar antes de firmar</h2>
    <p>No compares únicamente la cuota. Revisa la entrada, el IVA, el coste contractual estimado, la duración, los kilómetros anuales y las coberturas que constan por escrito. Las condiciones del proveedor y el contrato prevalecen sobre cualquier resumen comercial.</p>
  </section>;
}
