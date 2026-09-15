import { NextResponse } from "next/server";
import { reviewEnv } from "@/lib/reviews-db";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { assistedSearchModelPath } from "@/lib/assisted-search";
import { offerPriceExVat, offerPriceIncVat } from "@/lib/offer-pricing";
import { vehicleModelKey } from "@/lib/vehicle-groups";

export const runtime = "nodejs";

const clean = (value: unknown, length: number) => String(value ?? "").trim().slice(0, length);
const bodyTypes: Record<string, string[]> = { Utilitario: ["Compacto"], Compacto: ["Compacto"], SUV: ["SUV"], Berlina: ["Berlina"], Familiar: ["Familiar", "Furgoneta"] };
const budgetMaximum: Record<string, number> = { "Menos de 250 €": 250, "250–300 €": 300, "300–400 €": 400, "400–500 €": 500, "500–700 €": 700 };

function assistedRecommendations(input: { brand: string; model: string; vehicleType: string; customerType: string; budgetRange: string; annualKm: string }) {
  const annualKm = Number(input.annualKm.replace(/\D/g, "")) || 0;
  const maximum = budgetMaximum[input.budgetRange] ?? Number.POSITIVE_INFINITY;
  const allowedBodies = bodyTypes[input.vehicleType];
  const byId = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));
  const bestByModel = new Map<string, { vehicle: (typeof vehicles)[number]; offer: (typeof offers)[number]; price: number }>();
  for (const offer of offers) {
    const vehicle = byId.get(offer.vehicleId);
    if (!vehicle || (input.customerType && offer.audience !== input.customerType)) continue;
    if (input.brand && vehicle.brand.toLowerCase() !== input.brand.toLowerCase()) continue;
    const cleanModel = vehicle.model.replace(new RegExp(`^${vehicle.brand}\\s+`, "i"), "");
    if (input.model && cleanModel.toLowerCase() !== input.model.toLowerCase()) continue;
    if (allowedBodies && !allowedBodies.includes(vehicle.bodyType)) continue;
    const price = input.customerType === "particular" ? offerPriceIncVat(offer) : offerPriceExVat(offer);
    if (price > maximum) continue;
    const key = vehicleModelKey(vehicle);
    const current = bestByModel.get(key);
    const score = price + (annualKm ? Math.abs(offer.kilometers - annualKm) / 1000 : 0);
    const currentScore = current ? current.price + (annualKm ? Math.abs(current.offer.kilometers - annualKm) / 1000 : 0) : Number.POSITIVE_INFINITY;
    if (!current || score < currentScore) bestByModel.set(key, { vehicle, offer, price });
  }
  return [...bestByModel.values()].sort((a, b) => a.price - b.price).slice(0, 3).map(({ vehicle, offer, price }) => ({
    id: vehicle.id, name: `${vehicle.brand} ${vehicle.model.replace(new RegExp(`^${vehicle.brand}\\s+`, "i"), "")}`,
    href: assistedSearchModelPath(vehicle.brand, vehicle.model), image: vehicle.images?.card ?? null,
    price: Math.round(price * 100) / 100, priceLabel: offer.audience === "particular" ? "IVA incluido" : "sin IVA",
  }));
}

async function saveAssistedSearch(body: Record<string, unknown>) {
  const lead = {
    name: clean(body.name, 120), phone: clean(body.phone, 40), email: clean(body.email, 160), customerType: clean(body.customerType, 20),
    searchType: clean(body.searchType, 20), brand: clean(body.brand, 80), model: clean(body.model, 100), vehicleType: clean(body.vehicleType, 40),
    budgetRange: clean(body.budgetRange, 60), annualKm: clean(body.annualKm, 40), purchaseTiming: clean(body.purchaseTiming, 60),
    sourcePage: clean(body.sourcePage, 500), pageUrl: clean(body.pageUrl, 500), referrer: clean(body.referrer, 500),
    utmSource: clean(body.utmSource, 160), utmMedium: clean(body.utmMedium, 160), utmCampaign: clean(body.utmCampaign, 160),
    utmContent: clean(body.utmContent, 160), utmTerm: clean(body.utmTerm, 160), legalAccepted: body.legalAccepted === true,
  };
  if (!lead.name || !lead.phone || !lead.email.includes("@") || !lead.customerType || !lead.searchType || !lead.budgetRange || !lead.annualKm || !lead.purchaseTiming || !lead.sourcePage || !lead.legalAccepted) {
    return NextResponse.json({ error: "Revisa los datos y acepta la política de privacidad." }, { status: 400 });
  }
  const id = `MR-A-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${crypto.randomUUID().slice(0, 8).toUpperCase()}`;
  try {
    const { REVIEWS_DB } = reviewEnv();
    try {
      await REVIEWS_DB.prepare("INSERT INTO leads (id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name, offer_id, provider, duration_months, annual_kilometers, monthly_price, price_includes_vat, initial_payment, channel, page_url, lead_type, search_type, brand, model, vehicle_type, budget_range, purchase_timing, source_page, referrer, utm_source, utm_medium, utm_campaign, utm_content, utm_term, legal_accepted) VALUES (?, ?, '', ?, ?, '', ?, '', ?, '', '', 0, ?, 0, 0, 0, 'email', ?, 'assisted_search', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)")
        .bind(id, lead.name, lead.phone, lead.email, lead.customerType, [lead.brand, lead.model].filter(Boolean).join(" "), Number(lead.annualKm.replace(/\D/g, "")) || 0, lead.pageUrl, lead.searchType, lead.brand, lead.model, lead.vehicleType, lead.budgetRange, lead.purchaseTiming, lead.sourcePage, lead.referrer, lead.utmSource, lead.utmMedium, lead.utmCampaign, lead.utmContent, lead.utmTerm).run();
    } catch {
      const metadata = JSON.stringify({ leadType: "assisted_search", ...lead });
      await REVIEWS_DB.prepare("INSERT INTO leads (id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name, offer_id, provider, duration_months, annual_kilometers, monthly_price, price_includes_vat, initial_payment, channel, page_url) VALUES (?, ?, '', ?, ?, '', ?, 'assisted_search', ?, 'assisted_search', 'MyRenting', 0, ?, 0, 0, 0, 'email', ?)")
        .bind(id, lead.name, lead.phone, lead.email, lead.customerType, metadata, Number(lead.annualKm.replace(/\D/g, "")) || 0, lead.pageUrl).run();
    }
    return NextResponse.json({ ok: true, reference: id, recommendations: assistedRecommendations(lead) });
  } catch {
    return NextResponse.json({ error: "No se pudo registrar la solicitud." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body || body.website) return NextResponse.json({ ok: true });
  if (body.leadType === "assisted_search") return saveAssistedSearch(body);
  const lead = {
    firstName: clean(body.firstName, 60), lastName: clean(body.lastName, 100), phone: clean(body.phone, 40),
    email: clean(body.email, 160), city: clean(body.city, 100), customerType: clean(body.customerType, 20),
    vehicleId: clean(body.vehicleId, 180), vehicleName: clean(body.vehicleName, 240), offerId: clean(body.offerId, 220),
    provider: clean(body.provider, 100), channel: clean(body.channel, 20), pageUrl: clean(body.pageUrl, 500),
    duration: Number(body.duration), kilometers: Number(body.kilometers), monthlyPrice: Number(body.monthlyPrice),
    initialPayment: Number(body.initialPayment), priceIncludesVat: body.priceIncludesVat === true,
  };
  if (!lead.firstName || !lead.lastName || !lead.phone || !lead.email.includes("@") || !lead.city || !lead.vehicleId || !lead.offerId || !["email", "whatsapp"].includes(lead.channel) || !Number.isFinite(lead.monthlyPrice)) {
    return NextResponse.json({ error: "Revisa los datos de contacto y la configuración seleccionada." }, { status: 400 });
  }
  const id = `MR-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${crypto.randomUUID().slice(0, 8).toUpperCase()}`;
  try {
    const { REVIEWS_DB } = reviewEnv();
    await REVIEWS_DB.prepare("INSERT INTO leads (id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name, offer_id, provider, duration_months, annual_kilometers, monthly_price, price_includes_vat, initial_payment, channel, page_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
      .bind(id, lead.firstName, lead.lastName, lead.phone, lead.email, lead.city, lead.customerType, lead.vehicleId, lead.vehicleName, lead.offerId, lead.provider, lead.duration, lead.kilometers, lead.monthlyPrice, lead.priceIncludesVat ? 1 : 0, lead.initialPayment, lead.channel, lead.pageUrl).run();
    return NextResponse.json({ ok: true, reference: id });
  } catch {
    return NextResponse.json({ error: "No se pudo registrar la solicitud." }, { status: 503 });
  }
}
