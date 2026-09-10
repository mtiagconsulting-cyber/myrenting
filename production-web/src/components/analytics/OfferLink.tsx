"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { trackAnalyticsEvent } from "@/lib/analytics";
import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export function OfferLink({ href, vehicle, offer }: { href: string; vehicle: Vehicle; offer: Offer }) {
  return <Link href={href} onClick={() => trackAnalyticsEvent("cta_click", { cta_name: "vehicle_card", vehicle_id: vehicle.id, vehicle_name: `${vehicle.brand} ${vehicle.model}`, offer_id: offer.id, customer_type: offer.audience, monthly_price: offer.monthlyPrice })} className="mt-auto flex min-h-11 items-center justify-between rounded-lg bg-ink px-4 text-sm font-bold text-white transition-colors hover:bg-copy">
    Ver oferta y condiciones <ArrowRight size={16} aria-hidden="true" />
  </Link>;
}
