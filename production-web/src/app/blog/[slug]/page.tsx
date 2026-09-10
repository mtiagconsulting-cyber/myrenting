import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Schema, editorialSchema } from "@/components/seo/Schema";
import { PriorityArticleContent, priorityArticleMetadata } from "@/components/editorial/PriorityArticleContent";
import legacy from "@/data/legacy-articles.json";
import { inventoryUpdatedAt } from "@/data/offers";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() { return legacy.articles.filter((article) => article.slug !== "mejores-coches-renting-baratos.html").map((article) => ({ slug: article.slug })); }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const article = legacy.articles.find((item) => item.slug === slug);
  if (!article) return {};
  const priority = priorityArticleMetadata(slug);
  const title = priority?.title ?? article.title.replace(/\s*\|\s*MyRenting$/i, "");
  const description = priority?.description ?? article.description;
  return { title, description, alternates: { canonical: `/blog/${slug}` }, openGraph: { type: "article", title, description, url: `/blog/${slug}`, publishedTime: legacy.generatedAt, modifiedTime: priority ? inventoryUpdatedAt : legacy.generatedAt } };
}

export default async function LegacyArticlePage({ params }: Props) {
  const { slug } = await params;
  const article = legacy.articles.find((item) => item.slug === slug);
  if (!article) notFound();
  const priority = priorityArticleMetadata(slug);
  return <main id="contenido-principal">
    <Schema data={editorialSchema({ path: `/blog/${slug}`, title: priority?.title ?? article.headline, description: priority?.description ?? article.description, datePublished: legacy.generatedAt, dateModified: priority ? inventoryUpdatedAt : legacy.generatedAt })} />
    <header className="border-b border-line bg-ink text-white"><div className="mx-auto max-w-4xl px-5 py-12 sm:px-8 sm:py-18"><Link href="/blog" className="text-xs font-bold tracking-[0.1em] text-orange-400 uppercase">Guías MyRenting</Link><h1 className="font-display mt-4 text-4xl font-semibold tracking-[-0.05em] sm:text-6xl">{priority?.title ?? article.headline}</h1>{(priority?.description ?? article.intro) && <p className="mt-5 max-w-3xl text-base leading-7 text-slate-300">{priority?.description ?? article.intro}</p>}</div></header>
    {!priority && article.html.trim() ? <article className="legacy-article mx-auto max-w-4xl px-5 py-10 sm:px-8 sm:py-14" dangerouslySetInnerHTML={{ __html: article.html }} /> : null}
    <PriorityArticleContent slug={slug} />
  </main>;
}
