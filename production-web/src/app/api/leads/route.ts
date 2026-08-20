import { NextResponse } from "next/server";
import { reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";

const clean = (value: unknown, length: number) => String(value ?? "").trim().slice(0, length);

export async function POST(request: Request) {
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body || body.website) return NextResponse.json({ ok: true });
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
