import { notFound, permanentRedirect } from "next/navigation";
import { seoPages } from "@/data/seo-pages";

type Props = { params: Promise<{ landing: string }> };

const destinations: Record<string, string> = {
  "renting-suv": "/renting/suv", "renting-hibridos": "/renting/hibridos", "renting-electricos": "/renting/electricos",
  "renting-barato": "/renting/baratos", "renting-sin-entrada": "/renting/sin-entrada", "renting-entrega-inmediata": "/renting/entrega-inmediata",
  "renting-autonomos": "/renting/autonomos", "renting-automaticos": "/renting/automaticos", "renting-etiqueta-eco": "/renting/etiqueta-eco",
  "renting-etiqueta-cero": "/renting/etiqueta-cero", "renting-furgonetas": "/renting/furgonetas", "renting-menos-300-euros": "/renting/menos-de-300-euros",
  "renting-menos-350-euros": "/renting/menos-de-400-euros", "renting-menos-450-euros": "/renting/menos-de-500-euros", "renting-menos-500-euros": "/renting/menos-de-500-euros",
  "renting-menos-600-euros": "/renting/menos-de-500-euros", "renting-menos-700-euros": "/renting/menos-de-500-euros",
};

export function generateStaticParams() { return seoPages.map(({ slug: landing }) => ({ landing })); }

export default async function LegacyLandingPage({ params }: Props) {
  const { landing } = await params;
  if (!seoPages.some((page) => page.slug === landing)) notFound();
  permanentRedirect(destinations[landing] ?? "/renting");
}
