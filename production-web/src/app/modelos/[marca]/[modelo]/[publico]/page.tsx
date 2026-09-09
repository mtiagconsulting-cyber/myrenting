import { notFound, permanentRedirect } from "next/navigation";
import { findModelAudiencePage } from "@/lib/seo-indexability";

type Props = { params: Promise<{ marca: string; modelo: string; publico: string }> };

export function generateStaticParams() { return []; }

export default async function LegacyModelAudiencePage({ params }: Props) {
  const { marca, modelo, publico } = await params;
  const page = findModelAudiencePage(marca, modelo, publico);
  if (!page) notFound();
  permanentRedirect(`/renting/${page.brandSlug}/${page.modelSlug}`);
}
