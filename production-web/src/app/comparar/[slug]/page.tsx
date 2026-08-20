import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ComparisonHeader } from "@/components/comparison/ComparisonHeader";
import { ComparisonSelector } from "@/components/comparison/ComparisonSelector";
import { ComparisonTable } from "@/components/comparison/ComparisonTable";
import { RecommendationBox } from "@/components/comparison/RecommendationBox";
import { AnswerSummary } from "@/components/seo/AnswerSummary";
import { Breadcrumb } from "@/components/seo/Breadcrumb";
import { SourceStatus } from "@/components/seo/SourceStatus";
import { getComparison, popularComparisonSlugs, totalContractCost } from "@/lib/comparison";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() { return popularComparisonSlugs.map((slug) => ({ slug })); }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const comparison = getComparison(slug);
  if (!comparison) return {};
  const first = comparison.first.vehicle;
  const second = comparison.second.vehicle;
  return { title: `${first.brand} ${first.model} vs ${second.brand} ${second.model}`, description: `Compara precio, condiciones, consumo, maletero y equipamiento del ${first.brand} ${first.model} y el ${second.brand} ${second.model}.`, alternates: { canonical: `/comparar/${slug}` } };
}

export default async function ComparisonPage({ params }: Props) {
  const { slug } = await params;
  const comparison = getComparison(slug);
  if (!comparison) notFound();
  const first = comparison.first;
  const second = comparison.second;
  const firstName = `${first.vehicle.brand} ${first.vehicle.model}`;
  const secondName = `${second.vehicle.brand} ${second.vehicle.model}`;
  const cheaper = first.offer.monthlyPrice <= second.offer.monthlyPrice ? first : second;
  const largerTrunk = (first.vehicle.trunk ?? 0) >= (second.vehicle.trunk ?? 0) ? first : second;
  const difference = Math.abs(first.offer.monthlyPrice - second.offer.monthlyPrice);
  const configuration = `${first.offer.audience === "autonomo" ? "autónomos" : first.offer.audience === "empresa" ? "empresas" : "particulares"}, ${first.offer.duration} meses y ${first.offer.kilometers.toLocaleString("es-ES")} km/año`;

  return (
    <main id="contenido-principal" className="mx-auto max-w-6xl px-5 py-7 sm:px-8 sm:py-10">
      <Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: "Comparar", path: "/comparar" }, { name: `${firstName} vs ${secondName}`, path: `/comparar/${slug}` }]} />
      <div className="mb-7"><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Comparación directa</p><h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-5xl">{firstName} vs {secondName}</h1><p className="mt-4 max-w-3xl text-sm leading-6 text-muted">Precios y condiciones publicados por los proveedores, comparados con el mismo criterio. Revisa siempre el coste total antes de decidir.</p></div>
      <div className={`mb-5 rounded-lg border px-4 py-3 text-xs leading-5 ${comparison.matchedConfiguration ? "border-emerald-200 bg-emerald-50 text-emerald-900" : "border-amber-200 bg-amber-50 text-amber-900"}`}>{comparison.matchedConfiguration ? `Comparación homogénea: ambas cuotas corresponden a ${configuration}.` : "No existe una configuración idéntica en ambas ofertas. Los precios se muestran como referencia y no deben compararse directamente."}</div>
      <ComparisonHeader comparison={comparison} />
      <div className="mt-7 space-y-3">
        <AnswerSummary
          title={`Diferencia entre ${first.vehicle.model} y ${second.vehicle.model}`}
          answer={`${cheaper.vehicle.brand} ${cheaper.vehicle.model} tiene la cuota mensual más baja${difference ? ` por ${difference} €` : ""}. ${largerTrunk.vehicle.trunk !== null ? `${largerTrunk.vehicle.brand} ${largerTrunk.vehicle.model} ofrece ${largerTrunk.vehicle.trunk} litros de maletero.` : "Consulta la capacidad de maletero en la ficha del proveedor."} La mejor elección depende del uso y del coste total.`}
          facts={[
            { label: "Menor cuota", value: `${cheaper.vehicle.brand} ${cheaper.vehicle.model} · ${cheaper.offer.monthlyPrice} €/mes` },
            { label: `Coste total ${first.vehicle.model}`, value: `${totalContractCost(first.offer.monthlyPrice, first.offer.duration, first.offer.initialPayment).toLocaleString("es-ES")} €` },
            { label: `Coste total ${second.vehicle.model}`, value: `${totalContractCost(second.offer.monthlyPrice, second.offer.duration, second.offer.initialPayment).toLocaleString("es-ES")} €` },
          ]}
        />
        <SourceStatus />
      </div>
      <div className="mt-14 space-y-16 sm:mt-20 sm:space-y-20">
        <ComparisonTable comparison={comparison} />
        <RecommendationBox comparison={comparison} />
        <section className="rounded-xl border border-line bg-slate-50 p-5 sm:p-7"><h2 className="font-display text-2xl font-semibold tracking-[-0.04em] text-ink">Comparar otros coches</h2><div className="mt-5"><ComparisonSelector compact /></div></section>
      </div>
    </main>
  );
}
