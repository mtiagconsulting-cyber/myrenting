import { contentSlug } from "@/lib/content-slug";

export interface EditorialSource { title: string; publisher: string; url: string; reviewedAt: string; reviewedLabel: string; }

const aeatExpense = "https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/irpf-2025/c07-rendimientos-actividades-economicas-estimacion-directa/fase-1-determinacion-rendimiento-neto/gastos-fiscalmente-deducibles/requisitos-considerar-gasto-deducible.html";
const aeatVat = "https://sede.agenciatributaria.gob.es/Sede/iva/que-iva-soportado-puedo-deducir/que-puedo-deducir.html";
const reviewed = { reviewedAt: "2026-08-11", reviewedLabel: "11 de agosto de 2026" };

const sourcesBySlug: Record<string, EditorialSource[]> = {
  [contentSlug("¿Un autónomo puede deducir el renting?")]: [
    { title: "Requisitos para considerar un gasto como deducible", publisher: "Agencia Tributaria", url: aeatExpense, ...reviewed },
    { title: "IVA soportado deducible en vehículos", publisher: "Agencia Tributaria", url: aeatVat, ...reviewed },
  ],
  [contentSlug("¿Una empresa puede deducir la cuota?")]: [
    { title: "Requisitos para considerar un gasto como deducible", publisher: "Agencia Tributaria", url: aeatExpense, ...reviewed },
    { title: "IVA soportado deducible en vehículos", publisher: "Agencia Tributaria", url: aeatVat, ...reviewed },
  ],
  [contentSlug("¿El IVA es siempre deducible al 100 %?")]: [
    { title: "IVA soportado deducible en vehículos", publisher: "Agencia Tributaria", url: aeatVat, ...reviewed },
  ],
};

export function getEditorialSources(slug: string) { return sourcesBySlug[slug] ?? []; }
