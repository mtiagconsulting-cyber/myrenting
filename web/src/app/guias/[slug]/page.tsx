import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Breadcrumbs from "@/components/seo/Breadcrumbs";
import { JsonLd } from "@/components/seo/JsonLd";
import { guias, getGuia } from "@/data/guias";

const SITE = "https://myrenting.es";

export function generateStaticParams() {
  return guias.map((g) => ({ slug: g.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const g = getGuia(slug);
  if (!g) return {};
  return {
    title: g.title,
    description: g.description,
    alternates: { canonical: `/guias/${g.slug}` },
    openGraph: { type: "article", title: g.title, description: g.description },
  };
}

export default async function GuiaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const g = getGuia(slug);
  if (!g) notFound();

  const articleLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: g.title,
    description: g.description,
    datePublished: g.updated,
    dateModified: g.updated,
    author: { "@type": "Organization", name: "myrenting" },
    publisher: { "@type": "Organization", name: "myrenting" },
    mainEntityOfPage: `${SITE}/guias/${g.slug}/`,
  };
  const faqLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: g.faq.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };

  return (
    <div className="mx-auto max-w-[820px] px-6 pb-16">
      <Breadcrumbs items={[{ name: "Guías", href: "/guias" }, { name: g.title }]} />
      <article>
        <h1 className="text-[clamp(28px,3.4vw,40px)] font-extrabold leading-[1.1] tracking-tight text-ink">
          {g.title}
        </h1>
        <p className="mt-4 text-[17px] leading-relaxed text-body">{g.intro}</p>

        {g.sections.map((s, i) => (
          <section key={i} className="mt-8">
            <h2 className="text-[22px] font-extrabold tracking-tight text-ink">{s.h}</h2>
            <p className="mt-2.5 text-[15.5px] leading-relaxed text-body">{s.body}</p>
          </section>
        ))}

        <section className="mt-12">
          <h2 className="mb-4 text-[22px] font-extrabold text-ink">Preguntas frecuentes</h2>
          <div className="divide-y divide-line rounded-xl2 border border-line bg-white">
            {g.faq.map((f, i) => (
              <div key={i} className="p-5">
                <h3 className="text-[15.5px] font-bold text-ink">{f.q}</h3>
                <p className="mt-1.5 text-[14.5px] leading-relaxed text-body">{f.a}</p>
              </div>
            ))}
          </div>
        </section>
      </article>
      <JsonLd data={[articleLd, faqLd]} />
    </div>
  );
}
