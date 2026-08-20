import assert from "node:assert/strict";
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

console.log("Payload de email, mensaje de WhatsApp y evento de lead verificados.");
