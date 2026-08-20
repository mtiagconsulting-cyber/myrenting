import { notFound, permanentRedirect } from "next/navigation";
import { vehicles } from "@/data/vehicles";
import { contentSlug } from "@/lib/content-slug";

type Props = { params: Promise<{ marca: string; modelo: string }> };
const groups = [...new Set(vehicles.map((vehicle) => `${contentSlug(vehicle.brand)}/${contentSlug(vehicle.model)}`))];

export function generateStaticParams() { return groups.map((path) => { const [marca, modelo] = path.split("/"); return { marca, modelo }; }); }

export default async function LegacyModelPage({ params }: Props) {
  const { marca, modelo } = await params;
  if (!groups.includes(`${marca}/${modelo}`)) notFound();
  permanentRedirect(`/renting/${marca}/${modelo}`);
}
