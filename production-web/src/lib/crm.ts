export const CRM_STATUSES = ["NUEVO", "CONTACTADO", "RESPONDIO", "CUALIFICADO", "BUSCANDO", "OFERTA_ENVIADA", "DOCUMENTACION", "ESTUDIO", "APROBADO", "FIRMADO", "ENTREGADO", "NURTURE", "PERDIDO"] as const;
export type CrmStatus = (typeof CRM_STATUSES)[number];

export const CRM_STATUS_LABELS: Record<CrmStatus, string> = {
  NUEVO: "Nuevo", CONTACTADO: "Contactado", RESPONDIO: "Respondió", CUALIFICADO: "Cualificado",
  BUSCANDO: "Buscando", OFERTA_ENVIADA: "Oferta enviada", DOCUMENTACION: "Documentación",
  ESTUDIO: "En estudio", APROBADO: "Aprobado", FIRMADO: "Firmado", ENTREGADO: "Entregado",
  NURTURE: "Seguimiento futuro", PERDIDO: "Perdido",
};

export const NEXT_ACTIONS = ["WhatsApp", "Llamar", "Buscar vehículo", "Enviar oferta", "Follow-up oferta", "Solicitar documentación", "Consultar proveedor", "Follow-up documentación", "Follow-up aprobación", "Otro"] as const;
export const LOST_REASONS = ["No responde", "Precio", "Vehículo/oferta no disponible", "Condiciones", "Timing", "Competencia", "Rechazado financieramente", "Ha comprado un vehículo", "Ya no busca coche", "Otro"] as const;
export const TERMINAL_STATUSES = new Set<CrmStatus>(["ENTREGADO", "PERDIDO"]);

export function isCrmStatus(value: unknown): value is CrmStatus {
  return CRM_STATUSES.includes(String(value) as CrmStatus);
}

export function cleanCrmText(value: unknown, max = 500) {
  return String(value ?? "").trim().slice(0, max);
}

export function leadPriority(lead: { status: string; next_action_at?: string | null }, now = new Date()) {
  if (lead.status === "ENTREGADO" || lead.status === "PERDIDO") return 4;
  if (!lead.next_action_at) return 3;
  const action = new Date(lead.next_action_at);
  if (action.getTime() < now.getTime()) return 0;
  if (action.toLocaleDateString("es-ES", { timeZone: "Europe/Madrid" }) === now.toLocaleDateString("es-ES", { timeZone: "Europe/Madrid" })) return 1;
  return 2;
}
