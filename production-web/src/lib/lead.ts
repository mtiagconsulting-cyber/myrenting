import type { Offer } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";

export type LeadChannel = "email" | "whatsapp";
export type LeadContact = { name: string; lastName: string; phone: string; email: string; city: string };

const audienceLabel = { particular: "Particular", autonomo: "Autónomo", empresa: "Empresa" } as const;

export function buildLeadMessage(contact: LeadContact, vehicle: Vehicle, offer: Offer) {
  return [
    "NUEVA SOLICITUD DE RENTING",
    "",
    `Nombre: ${contact.name.trim()}`,
    `Apellidos: ${contact.lastName.trim()}`,
    `Teléfono: ${contact.phone.trim()}`,
    `Email: ${contact.email.trim()}`,
    `Ciudad: ${contact.city.trim()}`,
    `Tipo de cliente: ${audienceLabel[offer.audience]}`,
    "",
    `Coche: ${vehicle.brand} ${vehicle.model} ${vehicle.version}`,
    `Kilómetros: ${offer.kilometers.toLocaleString("es-ES")} km/año`,
    `Duración: ${offer.duration} meses`,
    `Precio: ${offer.monthlyPrice.toLocaleString("es-ES")} €/mes ${offer.priceIncludesVat ? "IVA incluido" : "+ IVA"}`,
    `Entrada: ${offer.initialPayment.toLocaleString("es-ES")} €`,
    `Proveedor: ${offer.provider}`,
    `Referencia: ${offer.id}`,
  ].join("\n");
}

export function buildFormSubmitPayload(contact: LeadContact, vehicle: Vehicle, offer: Offer, pageUrl: string, honey = "") {
  return {
    _subject: `Nueva solicitud de renting · ${vehicle.brand} ${vehicle.model}`,
    _template: "table",
    _captcha: "false",
    _honey: honey,
    _replyto: contact.email.trim(),
    Nombre: contact.name.trim(),
    Apellidos: contact.lastName.trim(),
    Teléfono: contact.phone.trim(),
    Email: contact.email.trim(),
    Ciudad: contact.city.trim(),
    "Tipo de cliente": audienceLabel[offer.audience],
    Coche: `${vehicle.brand} ${vehicle.model} ${vehicle.version}`,
    "Kilómetros anuales": `${offer.kilometers.toLocaleString("es-ES")} km/año`,
    Plazo: `${offer.duration} meses`,
    Cuota: `${offer.monthlyPrice.toLocaleString("es-ES")} €/mes ${offer.priceIncludesVat ? "IVA incluido" : "+ IVA"}`,
    Entrada: `${offer.initialPayment.toLocaleString("es-ES")} €`,
    Proveedor: offer.provider,
    Referencia: offer.id,
    "URL de la oferta": pageUrl,
  };
}

export function buildLeadEvent(channel: LeadChannel, vehicle: Vehicle, offer: Offer) {
  return {
    event: "generate_lead",
    lead_channel: channel,
    customer_type: offer.audience,
    vehicle_id: vehicle.id,
    vehicle_name: `${vehicle.brand} ${vehicle.model}`,
    offer_id: offer.id,
    monthly_price: offer.monthlyPrice,
    duration_months: offer.duration,
    annual_kilometers: offer.kilometers,
    currency: "EUR",
  };
}
