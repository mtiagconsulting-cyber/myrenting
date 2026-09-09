import { notFound, permanentRedirect } from "next/navigation";
import { findBrandAudiencePage } from "@/lib/seo-indexability";

type Props = { params: Promise<{ slug: string; publico: string }> };

export function generateStaticParams() { return []; }

export default async function LegacyBrandAudiencePage({ params }: Props) {
  const { slug, publico } = await params;
  const page = findBrandAudiencePage(slug, publico);
  if (!page) notFound();
  permanentRedirect(`/renting/${page.brandSlug}`);
}
