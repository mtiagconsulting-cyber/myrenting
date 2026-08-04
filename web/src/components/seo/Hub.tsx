import Breadcrumbs, { type Crumb } from "./Breadcrumbs";
import QuickSummary, { type SummaryItem } from "./QuickSummary";
import { JsonLd } from "./JsonLd";
import VehicleGrid from "@/components/vehicles/VehicleGrid";
import type { Vehicle } from "@/types";

const SITE = "https://myrenting.es";

export type Faq = { q: string; a: string };

export default function Hub({
  crumbs,
  title,
  intro,
  vehicles,
  summary,
  idealFor,
  faq,
  canonicalPath,
}: {
  crumbs: Crumb[];
  title: string;
  intro: string;
  vehicles: Vehicle[];
  summary: SummaryItem[];
  idealFor?: string;
  faq?: Faq[];
  canonicalPath: string;
}) {
  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: title,
    numberOfItems: vehicles.length,
    itemListElement: vehicles.map((v, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `${SITE}/coches/${v.slug}/`,
      name: v.title,
    })),
  };
  const faqLd = faq?.length
    ? {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: faq.map((f) => ({
          "@type": "Question",
          name: f.q,
          acceptedAnswer: { "@type": "Answer", text: f.a },
        })),
      }
    : null;

  return (
    <div className="mx-auto max-w-[1200px] px-6 pb-16">
      <Breadcrumbs items={crumbs} />
      <h1 className="text-[clamp(28px,3.4vw,38px)] font-extrabold tracking-tight text-ink">{title}</h1>
      <p className="mt-3 max-w-[76ch] text-[15.5px] leading-relaxed text-body">{intro}</p>

      <QuickSummary items={summary} idealFor={idealFor} />

      <div className="mb-4 mt-8 flex items-baseline justify-between">
        <h2 className="text-[22px] font-extrabold text-ink">{vehicles.length} modelos</h2>
      </div>
      <VehicleGrid vehicles={vehicles} />

      {faq?.length ? (
        <section className="mt-12">
          <h2 className="mb-4 text-[22px] font-extrabold text-ink">Preguntas frecuentes</h2>
          <div className="divide-y divide-line rounded-xl2 border border-line bg-white">
            {faq.map((f, i) => (
              <div key={i} className="p-5">
                <h3 className="text-[15.5px] font-bold text-ink">{f.q}</h3>
                <p className="mt-1.5 text-[14.5px] leading-relaxed text-body">{f.a}</p>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <JsonLd data={faqLd ? [itemList, faqLd] : itemList} />
      <link rel="canonical" href={SITE + canonicalPath} />
    </div>
  );
}
