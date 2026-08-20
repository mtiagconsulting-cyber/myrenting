import { notFound, permanentRedirect } from "next/navigation";

type Props = { params: Promise<{ slug: string }> };
const destinations: Record<string, string> = { suv: "/renting/suv", familiares: "/renting/familiares", urbanos: "/renting/coches-pequenos", berlinas: "/renting", empresas: "/renting/empresas" };

export function generateStaticParams() { return Object.keys(destinations).map((slug) => ({ slug })); }

export default async function LegacyCategoryPage({ params }: Props) {
  const { slug } = await params;
  if (!destinations[slug]) notFound();
  permanentRedirect(destinations[slug]);
}
