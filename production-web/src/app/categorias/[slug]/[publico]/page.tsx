import { notFound, permanentRedirect } from "next/navigation";

type Props = { params: Promise<{ slug: string; publico: string }> };
const categories = ["suv", "familiares", "urbanos", "berlinas", "empresas"];
const audiences: Record<string, string> = { particular: "/renting/particulares", autonomo: "/renting/autonomos", empresa: "/renting/empresas" };

export function generateStaticParams() { return categories.flatMap((slug) => Object.keys(audiences).map((publico) => ({ slug, publico }))); }

export default async function LegacyCategoryAudiencePage({ params }: Props) {
  const { slug, publico } = await params;
  if (!categories.includes(slug) || !audiences[publico]) notFound();
  permanentRedirect(audiences[publico]);
}
