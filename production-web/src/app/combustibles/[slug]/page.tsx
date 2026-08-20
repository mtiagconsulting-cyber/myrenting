import { notFound, permanentRedirect } from "next/navigation";
import { fuelPages } from "@/lib/catalog-taxonomy";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() { return fuelPages.map(({ slug }) => ({ slug })); }

export default async function LegacyFuelPage({ params }: Props) {
  const { slug } = await params;
  if (!fuelPages.some((page) => page.slug === slug)) notFound();
  permanentRedirect(`/renting/${slug}`);
}
