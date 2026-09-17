import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { buildFormSubmitPayload, buildLeadEvent, buildLeadMessage } from "../../src/lib/lead.ts";

const contact = { name: "Ana", lastName: "García", phone: "600123123", email: "ana@example.com", city: "Madrid" };
const vehicle = { id: "vehicle-test", brand: "KIA", model: "NIRO", version: "Drive", slug: "test", images: null, fuel: "Híbrido", power: 139, trunk: 451, consumption: 4.5, consumptionUnit: "l/100 km", label: "ECO", bodyType: "SUV" };
const offer = { id: "offer-test", vehicleId: vehicle.id, provider: "Proveedor", audience: "particular", monthlyPrice: 381, priceIncludesVat: true, initialPayment: 0, duration: 60, kilometers: 15000, maintenance: true, insurance: true, tyres: false, availability: "Disponible" };

const message = buildLeadMessage(contact, vehicle, offer);
for (const expected of ["Ana", "García", "600123123", "ana@example.com", "Madrid", "Particular", "KIA NIRO Drive", "15.000 km/año", "60 meses", "381 €/mes IVA incluido", "offer-test"]) {
  assert.ok(message.includes(expected), `Falta en WhatsApp: ${expected}`);
}

const payload = buildFormSubmitPayload(contact, vehicle, offer, "https://myrenting.es/coches/test", "");
assert.equal(payload.Nombre, "Ana");
assert.equal(payload.Apellidos, "García");
assert.equal(payload["Tipo de cliente"], "Particular");
assert.equal(payload["Kilómetros anuales"], "15.000 km/año");
assert.equal(payload.Plazo, "60 meses");
assert.equal(payload.Cuota, "381 €/mes IVA incluido");
assert.equal(payload["URL de la oferta"], "https://myrenting.es/coches/test");

const event = buildLeadEvent("email", vehicle, offer);
assert.deepEqual(event, { event: "generate_lead", lead_channel: "email", customer_type: "particular", vehicle_id: "vehicle-test", vehicle_name: "KIA NIRO", offer_id: "offer-test", monthly_price: 381, duration_months: 60, annual_kilometers: 15000, currency: "EUR" });

const trackedSources = await Promise.all([
  "../../src/components/vehicles/OfferConfigurator.tsx",
  "../../src/components/vehicles/Catalogue.tsx",
  "../../src/components/search/SearchEngine.tsx",
  "../../src/components/search/Filters.tsx",
  "../../src/components/analytics/OfferLink.tsx",
  "../../src/components/analytics/JourneyTracker.tsx",
  "../../src/components/leads/AssistedSearchCTA.tsx",
  "../../src/lib/analytics.ts",
  "../../src/lib/lead.ts",
].map((path) => readFile(new URL(path, import.meta.url), "utf8")));
const trackedCode = trackedSources.join("\n");
for (const trackedEvent of ["journey_page_view", "view_item", "view_item_list", "search", "filter", "cta_click", "offer_configure", "form_view", "form_start", "form_error", "lead_submit_attempt", "lead_submit_error", "lead_submit_success", "form_submit", "generate_lead", "lead_recorded"]) {
  assert.ok(trackedCode.includes(`\"${trackedEvent}\"`), `Falta instrumentar el evento ${trackedEvent}`);
}
assert.ok(!trackedCode.includes('"lead_validado"'), "No debe declararse un lead validado desde el navegador sin revisión comercial");
assert.ok(trackedCode.includes("if (analyticsWindow.gtag)"), "El envío debe elegir una sola vía de Analytics");
assert.ok(!trackedCode.includes('dataLayer.push({ event, ...parameters });\n  analyticsWindow.dataLayer = dataLayer;\n  analyticsWindow.gtag'), "Los eventos no deben enviarse a la vez por dataLayer y gtag");

const offerConfigurator = trackedSources[0];
assert.ok(offerConfigurator.indexOf('trackAnalyticsEvent("lead_submit_attempt"') < offerConfigurator.indexOf('fetch("/api/leads"'), "El intento debe registrarse antes de llamar a la API");
assert.ok(offerConfigurator.indexOf('if (!leadResponse.ok || !leadResult?.reference)') < offerConfigurator.indexOf('trackConfirmedLead("whatsapp"'), "WhatsApp solo puede contar como lead tras confirmación del servidor");

console.log("Payloads y eventos del embudo de lead verificados.");
