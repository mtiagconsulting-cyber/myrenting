import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SeoListingPage } from "@/components/seo/SeoListingPage";
import { offers } from "@/data/offers";
import { seoPages } from "@/data/seo-pages";
import { vehicles } from "@/data/vehicles";

type Props = { params: Promise<{ landing: string }> };

export function generateStaticParams() { return seoPages.map(({ slug: landing }) => ({ landing })); }
export async function generateMetadata({ params }: Props): Promise<Metadata> { const { landing } = await params; const config = seoPages.find((item) => item.slug === landing); if (!config) return {}; return { title: config.title, description: config.description, alternates: { canonical: `/${config.slug}` } }; }

export default async function LandingPage({ params }: Props) {
  const { landing } = await params;
  const config = seoPages.find((item) => item.slug === landing);
  if (!config) notFound();
  const items = vehicles.filter((vehicle) => { const matchingOffers = offers.filter((item) => item.vehicleId === vehicle.id && (!config.audience || item.audience === config.audience) && (!config.offerFilter || config.offerFilter(item))); const offer = matchingOffers.sort((first, second) => first.monthlyPrice - second.monthlyPrice)[0]; return offer ? config.filter(vehicle, offer.monthlyPrice) : false; });
  return <SeoListingPage heading={config.heading} summary={config.summary} idealFor={config.idealFor} canonical={`/${config.slug}`} items={items} faqs={config.faqs} audience={config.audience} offerFilter={config.offerFilter} />;
}
