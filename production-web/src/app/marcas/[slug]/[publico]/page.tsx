import { notFound, permanentRedirect } from "next/navigation";
import { findBrandAudiencePage, brandAudiencePages } from "@/lib/seo-indexability";

type Props = { params: Promise<{ slug: string; publico: string }> };

export function generateStaticParams() { return brandAudiencePages.map((page) => ({ slug: page.brandSlug, publico: page.audience })); }

export default async function LegacyBrandAudiencePage({ params }: Props) {
  const { slug, publico } = await params;
  const page = findBrandAudiencePage(slug, publico);
  if (!page) notFound();
  permanentRedirect(`/renting/${page.brandSlug}`);
}
