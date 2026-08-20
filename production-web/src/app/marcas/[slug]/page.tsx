import { notFound, permanentRedirect } from "next/navigation";
import { brands } from "@/data/vehicles";
import { contentSlug } from "@/lib/content-slug";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() { return brands.map((brand) => ({ slug: contentSlug(brand) })); }

export default async function LegacyBrandPage({ params }: Props) {
  const { slug } = await params;
  if (!brands.some((brand) => contentSlug(brand) === slug)) notFound();
  permanentRedirect(`/renting/${slug}`);
}
