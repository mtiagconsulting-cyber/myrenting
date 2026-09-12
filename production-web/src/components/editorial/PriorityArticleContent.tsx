import Link from "next/link";
import { FAQ } from "@/components/seo/FAQ";
import { VehicleGrid } from "@/components/vehicles/VehicleGrid";
import { offers, inventoryUpdatedAt } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { canonicalVehicles, vehiclesInSameGroup } from "@/lib/vehicle-groups";
import { offerPriceExVat } from "@/lib/offer-pricing";

const targets: Record<string, {
  eyebrow: string;
  title: string;
  contentHeading: string;
  description: string;
  categoryHref: string;
  categoryLabel: string;
  relatedModels?: Array<{ label: string; href: string }>;
  faqs?: Array<{ question: string; answer: string }>;
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
    relatedModels: [{ label: "Renting Peugeot 208", href: "/renting/peugeot/208" }, { label: "Renting Opel Corsa", href: "/renting/opel/corsa" }, { label: "Renting Dacia Sandero", href: "/renting/dacia/sandero" }, { label: "Renting SEAT Ibiza", href: "/renting/seat/ibiza" }],
    faqs: [
      { question: "¿Cuál es el coche de renting más barato?", answer: "La oferta más barata cambia con el inventario. Compara siempre cuota con y sin IVA, entrada, plazo y kilómetros antes de decidir." },
      { question: "¿Un renting barato incluye seguro y mantenimiento?", answer: "Depende de la campaña. Comprueba en la ficha y en el contrato qué seguro, mantenimiento, neumáticos y asistencia están incluidos." },
      { question: "¿Hay renting barato sin entrada?", answer: "Sí existen campañas sin entrada, pero no todas las cuotas bajas lo son. Revisa el pago inicial y el coste total bajo las mismas condiciones." },
    ],
  },
  "mejores-coches-renting-2026.html": {
    eyebrow: "Selección por calidad y precio",
    title: "Mejores coches de renting en 2026: selección y ofertas",
    contentHeading: "Los coches de renting que conviene comparar en 2026",
    description: "No existe un único coche mejor para todos. Esta selección prioriza cuotas competitivas y permite continuar hacia el inventario real para revisar versión, plazo, kilometraje e IVA.",
    categoryHref: "/renting",
    categoryLabel: "Comparar todos los coches",
    relatedModels: [{ label: "Renting Kia Niro", href: "/renting/kia/niro" }, { label: "Renting Peugeot 208", href: "/renting/peugeot/208" }, { label: "Renting Hyundai Tucson", href: "/renting/hyundai/tucson" }, { label: "Renting Nissan Qashqai", href: "/renting/nissan/qashqai" }],
  },
  "que-incluye-renting-coche.html": {
    eyebrow: "Condiciones del contrato",
    title: "Qué incluye el renting de un coche: coberturas y gastos",
    contentHeading: "Qué suele incluir la cuota de renting",
    description: "La cobertura exacta depende de cada campaña. Antes de contratar, revisa seguro, mantenimiento, neumáticos, asistencia, entrada, kilometraje y posibles penalizaciones.",
    categoryHref: "/preguntas-frecuentes",
    categoryLabel: "Consultar preguntas frecuentes",
  },
  "renting-particulares-guia-2026.html": {
    eyebrow: "Guía para particulares",
    title: "Renting para particulares en 2026: guía para elegir bien",
    contentHeading: "Cómo contratar un renting como particular",
    description: "Compara cuotas con IVA incluido, entrada, duración, kilometraje y coberturas. Esta guía conecta cada decisión con ofertas vigentes para particulares.",
    categoryHref: "/renting/particulares",
    categoryLabel: "Ver renting para particulares",
  },
  "mejores-suv-renting-2026.html": {
    eyebrow: "Comparativa actualizada",
    title: "Mejores SUV de renting en 2026: ofertas y cómo elegir",
    contentHeading: "Qué SUV conviene comparar en renting",
    description: "La mejor opción depende del espacio, uso, motorización y presupuesto. La selección se calcula con los SUV que tienen una campaña activa en Myrenting.",
    categoryHref: "/renting/suv",
    categoryLabel: "Comparar todos los SUV",
    relatedModels: [{ label: "Renting Kia Niro", href: "/renting/kia/niro" }, { label: "Renting Hyundai Tucson", href: "/renting/hyundai/tucson" }, { label: "Renting Volkswagen T-Roc", href: "/renting/volkswagen/t-roc" }, { label: "Renting Nissan Qashqai", href: "/renting/nissan/qashqai" }],
    filter: (vehicle) => vehicle.bodyType === "SUV",
  },
  "renting-autonomos-deduccion-2026.html": {
    eyebrow: "Fiscalidad sin promesas absolutas",
    title: "Renting para autónomos en 2026: IVA, IRPF y requisitos",
    contentHeading: "Qué puede deducir un autónomo en el renting",
    description: "La deducción depende de la vinculación del vehículo con la actividad, el impuesto y la documentación disponible. Compara cuotas sin IVA y consulta tu caso con un asesor fiscal.",
    categoryHref: "/renting/autonomos",
    categoryLabel: "Ver renting para autónomos",
  },
  "renting-vs-leasing-diferencias-2026.html": {
    eyebrow: "Comparativa de contratación",
    title: "Renting vs. leasing en 2026: diferencias y cuál elegir",
    contentHeading: "Diferencias entre renting y leasing",
    description: "El renting prioriza el uso del vehículo y los servicios asociados; el leasing es una fórmula de financiación. La opción adecuada depende de la propiedad, la contabilidad y las coberturas que necesitas.",
    categoryHref: "/renting/empresas",
    categoryLabel: "Comparar renting para empresas",
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
    const offer = offers.filter((item) => ids.has(item.vehicleId)).sort((a, b) => offerPriceExVat(a) - offerPriceExVat(b))[0];
    return offer ? [{ vehicle, offer }] : [];
  }).sort((a, b) => offerPriceExVat(a.offer) - offerPriceExVat(b.offer)).slice(0, 6);
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
      {target.relatedModels?.length ? <nav aria-label="Modelos relacionados" className="mt-6 flex flex-wrap gap-2">{target.relatedModels.map((item) => <Link key={item.href} href={item.href} className="rounded-full border border-line bg-surface px-4 py-2 text-xs font-bold text-copy hover:border-brand hover:text-brand">{item.label}</Link>)}</nav> : null}
    </section>
    {slug === "que-incluye-renting-coche.html" ? <IncludedGuide /> : <>
    {slug === "renting-particulares-guia-2026.html" ? <ParticularGuide /> : null}
    {slug === "mejores-suv-renting-2026.html" ? <SuvGuide /> : null}
    {slug === "renting-autonomos-deduccion-2026.html" ? <AutonomosGuide /> : null}
    {slug === "renting-vs-leasing-diferencias-2026.html" ? <LeasingGuide /> : null}
    <section className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><h2 className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">Ofertas reales para comparar</h2><p className="mt-2 text-sm text-muted">Ordenadas por la cuota publicada más baja, sin ocultar el perfil ni el tratamiento del IVA.</p></div><Link href={target.categoryHref} className="rounded-lg bg-brand px-5 py-3 text-sm font-bold text-white hover:bg-brand-hover">{target.categoryLabel}</Link></div>
      <VehicleGrid items={listings} />
    </section></>}
    <section className="mx-auto mb-14 max-w-4xl px-5 sm:px-8"><div className="rounded-xl bg-ink p-6 text-white sm:flex sm:items-center sm:justify-between sm:gap-6"><div><h2 className="font-display text-2xl font-semibold">Continúa con ofertas disponibles</h2><p className="mt-2 text-sm text-slate-300">Revisa la versión concreta, cuota, entrada, plazo y kilómetros antes de solicitar información.</p></div><Link href={target.categoryHref} className="mt-5 inline-flex shrink-0 rounded-lg bg-brand px-5 py-3 text-sm font-bold text-white sm:mt-0">{target.categoryLabel}</Link></div></section>
    {target.faqs?.length ? <section className="mx-auto mb-14 max-w-4xl px-5 sm:px-8"><FAQ items={target.faqs} /></section> : null}
  </>;
}

export function priorityArticleFaqs(slug: string) {
  return targets[slug]?.faqs ?? [];
}

function ParticularGuide() {
  return <section className="legacy-article mx-auto max-w-4xl px-5 pt-10 sm:px-8 sm:pt-12">
    <h2>Qué debe mirar un particular</h2>
    <p>Para comparar dos ofertas, usa siempre la cuota con IVA incluido y las mismas condiciones de entrada, plazo y kilómetros. Una cuota menor puede terminar siendo más cara si exige un pago inicial o incluye menos kilometraje.</p>
    <h2>Documentación y aprobación</h2>
    <p>La gestora suele solicitar identificación, permiso de conducir, justificantes de ingresos y documentación bancaria. La contratación está sujeta a un estudio de solvencia y la aprobación nunca está garantizada.</p>
    <h2>Antes de firmar</h2>
    <ul><li>Confirma por escrito el plazo de entrega y la versión exacta.</li><li>Revisa franquicia, neumáticos, vehículo de sustitución y asistencia.</li><li>Comprueba el coste por exceso de kilómetros y la penalización por cancelación.</li><li>Verifica qué se considera desgaste normal al devolver el vehículo.</li></ul>
  </section>;
}

function SuvGuide() {
  return <section className="legacy-article mx-auto max-w-4xl px-5 pt-10 sm:px-8 sm:pt-12">
    <h2>Cómo elegir un SUV de renting</h2>
    <p>Prioriza el espacio útil y la motorización que encajan con tus recorridos. Para ciudad puede interesar un híbrido o eléctrico; para viajes frecuentes conviene comparar consumo, autonomía, maletero y kilómetros contratados.</p>
    <h2>Cómo se ordena la selección</h2>
    <p>Mostramos modelos con oferta activa y los ordenamos por su cuota publicada más baja. El precio final depende del perfil, IVA, plazo, kilometraje, entrada y disponibilidad de cada campaña.</p>
    <h2>Comprobaciones importantes</h2>
    <ul><li>Compara versiones y potencias equivalentes.</li><li>No des por incluida una cobertura si no figura en la oferta.</li><li>Confirma el stock y el plazo de entrega con el proveedor.</li><li>Valora el coste contractual completo, no solo la cuota mensual.</li></ul>
  </section>;
}

function AutonomosGuide() {
  return <section className="legacy-article mx-auto max-w-4xl px-5 pt-10 sm:px-8 sm:pt-12">
    <h2>La deducción no es automática</h2>
    <p>La cuota puede ser gasto deducible cuando está vinculada a la actividad, correctamente justificada y contabilizada. En IVA, el porcentaje depende del grado de afectación y de la capacidad de acreditarlo. Myrenting no presta asesoramiento fiscal.</p>
    <h2>Qué documentación conviene conservar</h2>
    <ul><li>Contrato, facturas y justificantes de pago.</li><li>Registro de desplazamientos y uso profesional cuando sea necesario.</li><li>Documentación que relacione el vehículo con la actividad económica.</li><li>Criterio confirmado por tu asesor para IVA e IRPF.</li></ul>
    <h2>Cómo comparar ofertas para autónomos</h2>
    <p>Compara cuotas sin IVA con el mismo plazo, kilometraje y entrada. Revisa también seguro, mantenimiento, neumáticos, cancelación anticipada y coste por exceso de kilómetros.</p>
  </section>;
}

function LeasingGuide() {
  return <section className="legacy-article mx-auto max-w-4xl px-5 pt-10 sm:px-8 sm:pt-12">
    <h2>Renting: uso y servicios</h2>
    <p>La cuota de renting suele agrupar el uso del vehículo con servicios como mantenimiento, seguro o asistencia, según el contrato. Al finalizar, lo habitual es devolver el vehículo.</p>
    <h2>Leasing: financiación</h2>
    <p>El leasing se orienta normalmente a financiar un activo y puede incorporar una opción de compra. Los servicios asociados al uso no tienen por qué estar incluidos.</p>
    <h2>Qué debes comparar</h2>
    <ul><li>Coste total y pagos iniciales.</li><li>Servicios y riesgos asumidos por cada parte.</li><li>Tratamiento contable y fiscal aplicable.</li><li>Condiciones de finalización y posible adquisición.</li></ul>
  </section>;
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
