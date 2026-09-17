"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { CalendarClock, ChevronRight, CircleDollarSign, LogOut, Phone, Plus, RefreshCw, Search, UserRound, X } from "lucide-react";
import { CRM_STATUSES, CRM_STATUS_LABELS, LOST_REASONS, NEXT_ACTIONS, TERMINAL_STATUSES, leadPriority, type CrmStatus } from "@/lib/crm";

type Lead = {
  id: string; created_at: string; updated_at: string; first_name: string; last_name: string; phone: string; email: string; city: string;
  customer_type: string; vehicle_name: string; vehicle_id?: string; offer_id: string; provider: string; channel: string; status: CrmStatus;
  last_contact_at: string | null; next_action: string | null; next_action_at: string | null; expected_commission: number | null;
  final_commission: number | null; lost_reason: string | null; lost_reason_other?: string | null; lead_type: string; duration_months?: number;
  annual_kilometers?: number; monthly_price?: number; price_includes_vat?: number; initial_payment?: number; page_url?: string;
  budget_range?: string; purchase_timing?: string; source_page?: string; utm_source?: string; utm_medium?: string; utm_campaign?: string;
  notes?: string | null; chosen_offer_id?: string | null;
  chosen_vehicle_name?: string | null;
};
type Activity = { id: number; activity_type: string; description: string; actor: string; created_at: string };
type Proposal = { id: number; offer_id: string; vehicle_id: string; created_at: string; vehicle: { brand: string; model: string; version: string } | null; offer: { provider: string; audience: string; duration: number; kilometers: number; monthlyPrice: number; priceIncludesVat: boolean } | null };
type Detail = { lead: Lead; activities: Activity[]; proposals: Proposal[] };
type CatalogueItem = { offerId: string; vehicleId: string; name: string; provider: string; audience: string; duration: number; kilometers: number; monthlyPrice: number; priceIncludesVat: boolean };

const inputClass = "h-11 w-full rounded-lg border border-line bg-white px-3 text-sm font-semibold text-ink outline-none focus:border-brand";
const labelClass = "text-xs font-bold text-muted";
const statusTone: Record<CrmStatus, string> = {
  NUEVO: "bg-orange-50 text-brand", CONTACTADO: "bg-blue-50 text-blue-700", RESPONDIO: "bg-cyan-50 text-cyan-700", CUALIFICADO: "bg-violet-50 text-violet-700",
  BUSCANDO: "bg-indigo-50 text-indigo-700", OFERTA_ENVIADA: "bg-amber-50 text-amber-800", DOCUMENTACION: "bg-yellow-50 text-yellow-800", ESTUDIO: "bg-fuchsia-50 text-fuchsia-700",
  APROBADO: "bg-emerald-50 text-emerald-700", FIRMADO: "bg-green-100 text-green-800", ENTREGADO: "bg-green-700 text-white", NURTURE: "bg-slate-100 text-slate-700", PERDIDO: "bg-red-50 text-red-700",
};

function dateTime(value?: string | null) { return value ? new Intl.DateTimeFormat("es-ES", { dateStyle: "short", timeStyle: "short" }).format(new Date(value)) : "—"; }
function money(value?: number | null) { return value == null ? "—" : `${value.toLocaleString("es-ES", { maximumFractionDigits: 2 })} €`; }
function localInput(value?: string | null) { if (!value) return ""; const date = new Date(value); const offset = date.getTimezoneOffset() * 60000; return new Date(date.getTime() - offset).toISOString().slice(0, 16); }
function actionKind(lead: Lead) {
  if (!lead.next_action_at || TERMINAL_STATUSES.has(lead.status)) return "none";
  const action = new Date(lead.next_action_at); const now = new Date();
  if (action < now) return "overdue";
  return action.toDateString() === now.toDateString() ? "today" : "upcoming";
}
function Status({ value }: { value: CrmStatus }) { return <span className={`inline-flex rounded-md px-2.5 py-1 text-[0.6875rem] font-bold ${statusTone[value]}`}>{CRM_STATUS_LABELS[value]}</span>; }

export function CrmApp() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [catalogue, setCatalogue] = useState<CatalogueItem[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [search, setSearch] = useState(""); const [status, setStatus] = useState(""); const [customer, setCustomer] = useState(""); const [action, setAction] = useState(""); const [timing, setTiming] = useState("");
  const [notice, setNotice] = useState(""); const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true); setNotice("");
    const [leadResponse, catalogueResponse] = await Promise.all([fetch("/api/crm/leads", { cache: "no-store" }), fetch("/api/crm/catalogue", { cache: "no-store" })]);
    if (leadResponse.status === 401) { setAuthenticated(false); setLoading(false); return; }
    const leadData = await leadResponse.json() as { leads?: Lead[]; error?: string };
    const catalogueData = await catalogueResponse.json() as { catalogue?: CatalogueItem[] };
    setLeads(leadData.leads ?? []); setCatalogue(catalogueData.catalogue ?? []); setAuthenticated(true); setLoading(false);
  }
  useEffect(() => { void load(); }, []);
  useEffect(() => { if (!selected) { setDetail(null); return; } void fetch(`/api/crm/leads/${encodeURIComponent(selected)}`, { cache: "no-store" }).then(async (response) => { if (response.ok) setDetail(await response.json() as Detail); }); }, [selected]);

  const filtered = useMemo(() => leads.filter((lead) => {
    const needle = search.toLocaleLowerCase("es"); const haystack = `${lead.first_name} ${lead.last_name} ${lead.email} ${lead.phone} ${lead.vehicle_name}`.toLocaleLowerCase("es");
    return (!needle || haystack.includes(needle)) && (!status || lead.status === status) && (!customer || lead.customer_type === customer) && (!action || lead.next_action === action) && (!timing || actionKind(lead) === timing);
  }).sort((a, b) => leadPriority(a) - leadPriority(b) || new Date(a.next_action_at ?? a.created_at).getTime() - new Date(b.next_action_at ?? b.created_at).getTime()), [leads, search, status, customer, action, timing]);
  const counts = useMemo(() => Object.fromEntries(CRM_STATUSES.map((item) => [item, leads.filter((lead) => lead.status === item).length])) as Record<CrmStatus, number>, [leads]);
  const overdue = leads.filter((lead) => actionKind(lead) === "overdue").length; const today = leads.filter((lead) => actionKind(lead) === "today").length;
  const finalRevenue = leads.reduce((sum, lead) => sum + (lead.final_commission ?? 0), 0);

  async function logout() { await fetch("/api/crm/session", { method: "DELETE" }); setAuthenticated(false); setLeads([]); setSelected(null); }
  async function refreshDetail() { if (!selected) return; const response = await fetch(`/api/crm/leads/${encodeURIComponent(selected)}`, { cache: "no-store" }); if (response.ok) setDetail(await response.json() as Detail); await load(); }

  if (authenticated === null) return <div className="grid min-h-[55vh] place-items-center"><p className="text-sm font-bold text-muted">Cargando CRM…</p></div>;
  if (!authenticated) return <Login onSuccess={load} />;

  return <div className="mx-auto max-w-[1500px] px-5 py-8 sm:px-8 lg:py-10">
    <header className="flex flex-wrap items-end justify-between gap-5 border-b border-line pb-7">
      <div><p className="text-sm font-bold text-brand">MyRenting · uso interno</p><h1 className="font-display mt-2 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-5xl">Pipeline comercial</h1><p className="mt-2 text-sm text-muted">Prioridad: acciones vencidas, seguimientos de hoy y nuevos leads.</p></div>
      <div className="flex gap-2"><button onClick={() => void load()} className="inline-flex h-11 items-center gap-2 rounded-lg border border-line bg-white px-4 text-sm font-bold text-ink"><RefreshCw size={16} className={loading ? "animate-spin" : ""}/>Actualizar</button><button onClick={() => void logout()} className="inline-flex h-11 items-center gap-2 rounded-lg border border-line bg-white px-4 text-sm font-bold text-ink"><LogOut size={16}/>Salir</button></div>
    </header>

    <section className="grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-5 mt-7">
      <Metric label="Leads totales" value={leads.length} icon={<UserRound size={17}/>} />
      <Metric label="Nuevos" value={counts.NUEVO} />
      <Metric label="Acciones hoy" value={today} icon={<CalendarClock size={17}/>} accent={today > 0} />
      <Metric label="Acciones vencidas" value={overdue} icon={<CalendarClock size={17}/>} danger={overdue > 0} />
      <Metric label="Ingresos registrados" value={money(finalRevenue)} icon={<CircleDollarSign size={17}/>} />
    </section>
    <section className="mt-3 flex gap-2 overflow-x-auto pb-2">{["CONTACTADO", "RESPONDIO", "CUALIFICADO", "OFERTA_ENVIADA", "DOCUMENTACION", "APROBADO", "FIRMADO", "ENTREGADO", "PERDIDO"].map((item) => <button key={item} onClick={() => setStatus(status === item ? "" : item)} className={`shrink-0 rounded-lg border px-3 py-2 text-xs font-bold ${status === item ? "border-ink bg-ink text-white" : "border-line bg-white text-copy"}`}>{CRM_STATUS_LABELS[item as CrmStatus]} · {counts[item as CrmStatus]}</button>)}</section>

    <section className="mt-5 rounded-xl border border-line bg-white p-4">
      <div className="grid gap-3 md:grid-cols-[1.5fr_repeat(4,0.75fr)]">
        <label className="relative"><Search size={16} className="absolute top-3.5 left-3 text-muted"/><input aria-label="Buscar leads" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Nombre, email, teléfono o vehículo" className={`${inputClass} pl-9`}/></label>
        <select aria-label="Filtrar por estado" className={inputClass} value={status} onChange={(event) => setStatus(event.target.value)}><option value="">Todos los estados</option>{CRM_STATUSES.map((item) => <option key={item} value={item}>{CRM_STATUS_LABELS[item]}</option>)}</select>
        <select aria-label="Filtrar por cliente" className={inputClass} value={customer} onChange={(event) => setCustomer(event.target.value)}><option value="">Todos los perfiles</option><option value="particular">Particular</option><option value="autonomo">Autónomo</option><option value="empresa">Empresa</option></select>
        <select aria-label="Filtrar por acción" className={inputClass} value={action} onChange={(event) => setAction(event.target.value)}><option value="">Todas las acciones</option>{NEXT_ACTIONS.map((item) => <option key={item}>{item}</option>)}</select>
        <select aria-label="Filtrar por fecha de acción" className={inputClass} value={timing} onChange={(event) => setTiming(event.target.value)}><option value="">Cualquier fecha</option><option value="overdue">Vencidas</option><option value="today">Hoy</option><option value="upcoming">Próximas</option><option value="none">Sin acción</option></select>
      </div>
      <p className="mt-3 text-xs text-muted">{filtered.length} resultados · ordenados por urgencia comercial</p>
    </section>

    {notice ? <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{notice}</p> : null}
    <div className="mt-5 overflow-hidden rounded-xl border border-line bg-white">
      <div className="hidden grid-cols-[1.1fr_1.3fr_0.7fr_0.75fr_1fr_1fr_auto] gap-4 border-b border-line bg-slate-50 px-5 py-3 text-[0.6875rem] font-bold text-muted lg:grid"><span>Cliente</span><span>Vehículo</span><span>Estado</span><span>Entrada</span><span>Último contacto</span><span>Próxima acción</span><span/></div>
      {filtered.map((lead) => <button key={lead.id} onClick={() => setSelected(lead.id)} className="grid w-full gap-3 border-b border-line px-5 py-4 text-left last:border-0 hover:bg-slate-50 lg:grid-cols-[1.1fr_1.3fr_0.7fr_0.75fr_1fr_1fr_auto] lg:items-center lg:gap-4">
        <span><strong className="block text-sm text-ink">{lead.first_name} {lead.last_name}</strong><small className="mt-1 block text-xs text-muted">{lead.customer_type} · {lead.phone}</small></span>
        <span className="text-sm font-semibold text-copy">{lead.chosen_vehicle_name ? <><strong className="block text-ink">{lead.chosen_vehicle_name}</strong><small className="mt-1 block text-xs font-medium text-muted">Elegido · originalmente {lead.vehicle_name || "búsqueda personalizada"}</small></> : (lead.vehicle_name || "Búsqueda personalizada")}</span><span><Status value={lead.status}/></span><span className="text-xs text-muted">{dateTime(lead.created_at)}</span><span className="text-xs text-copy">{dateTime(lead.last_contact_at)}</span>
        <span><strong className={`block text-xs ${actionKind(lead) === "overdue" ? "text-red-700" : actionKind(lead) === "today" ? "text-brand" : "text-ink"}`}>{lead.next_action ?? "Sin programar"}</strong><small className="mt-1 block text-xs text-muted">{dateTime(lead.next_action_at)}</small></span><ChevronRight size={17} className="text-muted"/>
      </button>)}
      {!filtered.length ? <div className="px-6 py-16 text-center"><p className="font-display text-xl font-semibold text-ink">No hay leads con estos filtros</p><p className="mt-2 text-sm text-muted">Limpia algún filtro para ampliar los resultados.</p></div> : null}
    </div>
    {selected ? <LeadPanel detail={detail} catalogue={catalogue} onClose={() => setSelected(null)} onChanged={() => void refreshDetail()} setNotice={setNotice}/> : null}
  </div>;
}

function Login({ onSuccess }: { onSuccess: () => Promise<void> }) {
  const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [sending, setSending] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); setSending(true); setError(""); const response = await fetch("/api/crm/session", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password }) }); if (!response.ok) { setError("La clave no es correcta."); setSending(false); return; } await onSuccess(); setSending(false); }
  return <main className="mx-auto grid min-h-[65vh] max-w-md place-items-center px-5 py-12"><form onSubmit={submit} className="w-full rounded-xl border border-line bg-white p-7 shadow-card"><p className="text-sm font-bold text-brand">MyRenting · área privada</p><h1 className="font-display mt-2 text-3xl font-semibold tracking-[-0.04em] text-ink">Acceso al CRM</h1><p className="mt-3 text-sm leading-6 text-muted">Introduce la clave de gestión para consultar información comercial.</p><label className="mt-6 block text-xs font-bold text-ink">Clave de acceso<input type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} className={`${inputClass} mt-2`}/></label>{error ? <p role="alert" className="mt-3 text-sm font-bold text-red-700">{error}</p> : null}<button disabled={sending} className="mt-5 h-12 w-full rounded-lg bg-brand text-sm font-bold text-white disabled:opacity-50">{sending ? "Comprobando…" : "Entrar al CRM"}</button></form></main>;
}

function Metric({ label, value, icon, accent, danger }: { label: string; value: string | number; icon?: React.ReactNode; accent?: boolean; danger?: boolean }) { return <div className="bg-white p-5"><div className={`flex items-center gap-2 text-xs font-bold ${danger ? "text-red-700" : accent ? "text-brand" : "text-muted"}`}>{icon}{label}</div><p className={`font-data mt-3 text-3xl font-semibold tracking-[-0.05em] ${danger ? "text-red-700" : "text-ink"}`}>{value}</p></div>; }

function LeadPanel({ detail, catalogue, onClose, onChanged, setNotice }: { detail: Detail | null; catalogue: CatalogueItem[]; onClose: () => void; onChanged: () => void; setNotice: (value: string) => void }) {
  const [saving, setSaving] = useState(false); const [proposalSearch, setProposalSearch] = useState(""); const [activityText, setActivityText] = useState(""); const [activityType, setActivityType] = useState("note");
  const lead = detail?.lead;
  async function patch(values: Record<string, unknown>) { if (!lead) return; setSaving(true); setNotice(""); const response = await fetch(`/api/crm/leads/${encodeURIComponent(lead.id)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(values) }); const data = await response.json() as { error?: string }; if (!response.ok) setNotice(data.error ?? "No se pudo guardar"); else onChanged(); setSaving(false); }
  async function submitOverview(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); await patch({ status: form.get("status"), lastContactAt: form.get("lastContactAt"), nextAction: form.get("nextAction"), nextActionAt: form.get("nextActionAt"), expectedCommission: form.get("expectedCommission"), finalCommission: form.get("finalCommission"), notes: form.get("notes"), lostReason: form.get("lostReason"), lostReasonOther: form.get("lostReasonOther"), chosenOfferId: form.get("chosenOfferId") }); }
  async function addActivity(event: FormEvent) { event.preventDefault(); if (!lead || !activityText.trim()) return; const response = await fetch(`/api/crm/leads/${encodeURIComponent(lead.id)}/activities`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: activityType, description: activityText }) }); if (response.ok) { setActivityText(""); onChanged(); } }
  async function addProposal(offerId: string) { if (!lead) return; const response = await fetch(`/api/crm/leads/${encodeURIComponent(lead.id)}/proposals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ offerId }) }); if (response.ok) { setProposalSearch(""); onChanged(); } }
  async function removeProposal(offerId: string) { if (!lead) return; await fetch(`/api/crm/leads/${encodeURIComponent(lead.id)}/proposals`, { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ offerId }) }); onChanged(); }
  const proposalResults = proposalSearch.length > 1 ? catalogue.filter((item) => `${item.name} ${item.provider}`.toLocaleLowerCase("es").includes(proposalSearch.toLocaleLowerCase("es"))).slice(0, 8) : [];
  return <div className="fixed inset-0 z-[100] bg-ink/45" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><aside role="dialog" aria-modal="true" aria-label="Ficha del lead" className="ml-auto h-full w-full max-w-3xl overflow-y-auto bg-canvas shadow-2xl">
    <header className="sticky top-0 z-10 flex items-start justify-between border-b border-line bg-white px-5 py-4 sm:px-7"><div>{lead ? <><div className="flex flex-wrap items-center gap-3"><h2 className="font-display text-2xl font-semibold text-ink">{lead.first_name} {lead.last_name}</h2><Status value={lead.status}/></div><p className="mt-1 font-data text-xs text-muted">{lead.id}</p></> : <p className="font-bold text-muted">Cargando ficha…</p>}</div><button onClick={onClose} aria-label="Cerrar ficha" className="grid size-11 place-items-center rounded-full border border-line bg-white text-ink"><X size={20}/></button></header>
    {lead && detail ? <form key={`${lead.id}-${lead.updated_at}`} onSubmit={submitOverview} className="space-y-5 p-5 sm:p-7">
      <Panel title="Cliente"><div className="grid gap-4 sm:grid-cols-2"><Read label="Teléfono" value={lead.phone}/><Read label="Email" value={lead.email}/><Read label="Ciudad" value={lead.city}/><Read label="Perfil" value={lead.customer_type}/></div><div className="mt-4 flex flex-wrap gap-2"><a href={`tel:${lead.phone}`} className="inline-flex h-10 items-center gap-2 rounded-lg bg-ink px-4 text-xs font-bold text-white"><Phone size={15}/>Llamar</a><a href={`https://wa.me/${lead.phone.replace(/\D/g, "")}`} target="_blank" rel="noreferrer" className="inline-flex h-10 items-center rounded-lg border border-line bg-white px-4 text-xs font-bold text-ink">Abrir WhatsApp</a><a href={`mailto:${lead.email}`} className="inline-flex h-10 items-center rounded-lg border border-line bg-white px-4 text-xs font-bold text-ink">Enviar email</a></div></Panel>
      <Panel title="Necesidad y solicitud original"><div className="grid gap-4 sm:grid-cols-2"><Read label="Vehículo solicitado" value={lead.vehicle_name || "Búsqueda personalizada"}/><Read label="Proveedor" value={lead.provider}/><Read label="Cuota original" value={money(lead.monthly_price)}/><Read label="Plazo y kilómetros" value={`${lead.duration_months || "—"} meses · ${(lead.annual_kilometers ?? 0).toLocaleString("es-ES")} km/año`}/><Read label="Presupuesto máximo" value={lead.budget_range || "—"}/><Read label="Cuándo lo necesita" value={lead.purchase_timing || "—"}/><Read label="Canal" value={lead.channel}/><Read label="Campaña" value={[lead.utm_source, lead.utm_medium, lead.utm_campaign].filter(Boolean).join(" / ") || "—"}/></div>{lead.page_url ? <a href={lead.page_url} target="_blank" rel="noreferrer" className="mt-4 inline-block break-all text-xs font-bold text-brand underline">Abrir página de origen</a> : null}</Panel>
      <Panel title="Pipeline y seguimiento"><div className="grid gap-4 sm:grid-cols-2"><label className={labelClass}>Estado<select name="status" defaultValue={lead.status} disabled={saving} onChange={(event) => { if (event.target.value !== "PERDIDO") void patch({ status: event.target.value }); }} className={`${inputClass} mt-2`} >{CRM_STATUSES.map((item) => <option key={item} value={item}>{CRM_STATUS_LABELS[item]}</option>)}</select><small className="mt-1 block font-medium text-muted">Se guarda automáticamente al cambiarlo. Para “Perdido”, indica el motivo y pulsa Guardar ficha.</small></label><label className={labelClass}>Último contacto<input name="lastContactAt" type="datetime-local" defaultValue={localInput(lead.last_contact_at)} className={`${inputClass} mt-2`}/></label><label className={labelClass}>Próxima acción<select name="nextAction" defaultValue={lead.next_action ?? ""} className={`${inputClass} mt-2`}><option value="">Sin programar</option>{NEXT_ACTIONS.map((item) => <option key={item}>{item}</option>)}</select></label><label className={labelClass}>Fecha próxima acción<input name="nextActionAt" type="datetime-local" defaultValue={localInput(lead.next_action_at)} className={`${inputClass} mt-2`}/></label></div><div className="mt-4 grid gap-4 sm:grid-cols-2"><label className={labelClass}>Motivo de pérdida<select name="lostReason" defaultValue={lead.lost_reason ?? ""} className={`${inputClass} mt-2`}><option value="">Seleccionar</option>{LOST_REASONS.map((item) => <option key={item}>{item}</option>)}</select></label><label className={labelClass}>Detalle si es “Otro”<input name="lostReasonOther" defaultValue={lead.lost_reason_other ?? ""} className={`${inputClass} mt-2`}/></label></div></Panel>
      <Panel title="Economía y notas"><div className="grid gap-4 sm:grid-cols-2"><label className={labelClass}>Comisión esperada<input name="expectedCommission" type="number" min="0" step="0.01" defaultValue={lead.expected_commission ?? ""} className={`${inputClass} mt-2`}/></label><label className={labelClass}>Comisión final/cobrada<input name="finalCommission" type="number" min="0" step="0.01" defaultValue={lead.final_commission ?? ""} className={`${inputClass} mt-2`}/></label></div><label className={`${labelClass} mt-4 block`}>Notas comerciales<textarea name="notes" defaultValue={lead.notes ?? ""} rows={5} className="mt-2 w-full rounded-lg border border-line bg-white p-3 text-sm text-ink outline-none focus:border-brand"/></label></Panel>
      <Panel title="Ofertas propuestas"><div className="relative"><label className={labelClass}>Buscar vehículo u oferta<input value={proposalSearch} onChange={(event) => setProposalSearch(event.target.value)} placeholder="Escribe modelo o proveedor" className={`${inputClass} mt-2`}/></label>{proposalResults.length ? <div className="absolute z-10 mt-1 max-h-72 w-full overflow-y-auto rounded-lg border border-line bg-white shadow-xl">{proposalResults.map((item) => <button type="button" key={item.offerId} onClick={() => void addProposal(item.offerId)} className="flex w-full items-center justify-between gap-4 border-b border-line px-4 py-3 text-left last:border-0 hover:bg-slate-50"><span><strong className="block text-sm text-ink">{item.name}</strong><small className="text-xs text-muted">{item.provider} · {item.duration} meses · {item.kilometers.toLocaleString("es-ES")} km</small></span><span className="font-data text-sm font-bold text-ink">{money(item.monthlyPrice)}</span></button>)}</div> : null}</div><div className="mt-4 space-y-2">{detail.proposals.map((proposal) => <div key={proposal.id} className="flex items-center justify-between gap-4 rounded-lg border border-line p-3"><div><p className="text-sm font-bold text-ink">{proposal.vehicle ? `${proposal.vehicle.brand} ${proposal.vehicle.model}` : proposal.offer_id}</p><p className="mt-1 text-xs text-muted">{proposal.offer?.provider} · {money(proposal.offer?.monthlyPrice)}{proposal.offer_id === lead.chosen_offer_id ? " · Elegida" : ""}</p></div><button type="button" onClick={() => void removeProposal(proposal.offer_id)} className="text-xs font-bold text-red-700">Eliminar</button></div>)}{!detail.proposals.length ? <p className="text-sm text-muted">Todavía no se han propuesto alternativas.</p> : null}</div><label className={`${labelClass} mt-4 block`}>Oferta finalmente elegida<select name="chosenOfferId" defaultValue={lead.chosen_offer_id ?? ""} className={`${inputClass} mt-2`}><option value="">Sin seleccionar</option>{detail.proposals.map((proposal) => <option key={proposal.offer_id} value={proposal.offer_id}>{proposal.vehicle ? `${proposal.vehicle.brand} ${proposal.vehicle.model}` : proposal.offer_id}</option>)}</select></label><p className="mt-2 text-xs text-muted">La solicitud original se conserva en el histórico; la tabla principal mostrará el vehículo elegido al guardar.</p></Panel>
      <button disabled={saving} className="sticky bottom-4 h-12 w-full rounded-lg bg-brand text-sm font-bold text-white shadow-xl disabled:opacity-50">{saving ? "Guardando…" : "Guardar ficha"}</button>
      <Panel title="Añadir actividad"><div className="grid gap-3 sm:grid-cols-[0.6fr_1.4fr_auto]"><select value={activityType} onChange={(event) => setActivityType(event.target.value)} className={inputClass}><option value="note">Nota</option><option value="whatsapp">WhatsApp</option><option value="call">Llamada</option><option value="email">Email</option><option value="provider">Proveedor</option><option value="document">Documentación</option><option value="other">Otro</option></select><input value={activityText} onChange={(event) => setActivityText(event.target.value)} placeholder="Qué ha ocurrido" className={inputClass}/><button type="button" onClick={(event) => void addActivity(event as unknown as FormEvent)} className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-ink px-4 text-sm font-bold text-white"><Plus size={16}/>Añadir</button></div></Panel>
      <Panel title="Histórico"><ol className="space-y-4">{detail.activities.map((activity) => <li key={activity.id} className="grid grid-cols-[12px_1fr] gap-3"><span className="mt-1.5 size-2.5 rounded-full bg-brand"/><div><p className="text-sm font-semibold text-ink">{activity.description}</p><p className="mt-1 font-data text-[0.6875rem] text-muted">{dateTime(activity.created_at)} · {activity.actor}</p></div></li>)}</ol></Panel>
    </form> : <div className="p-8 text-sm font-bold text-muted">Cargando datos…</div>}
  </aside></div>;
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <section className="rounded-xl border border-line bg-white p-5 sm:p-6"><h3 className="font-display mb-5 text-xl font-semibold text-ink">{title}</h3>{children}</section>; }
function Read({ label, value }: { label: string; value: string }) { return <div><p className="text-xs font-bold text-muted">{label}</p><p className="mt-1 break-words text-sm font-semibold text-ink">{value}</p></div>; }
