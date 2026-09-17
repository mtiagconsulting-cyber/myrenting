"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Check, CheckCircle2, X } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { trackAnalyticsEvent } from "@/lib/analytics";
import type { AssistedSearchContext, AssistedSearchVehicleOption } from "@/lib/assisted-search";

type SearchType = "specific" | "type" | "unsure";
type Recommendation = { id: string; name: string; href: string; image: string | null; price: number; priceLabel: string };
type FormState = {
  searchType: SearchType | ""; brand: string; model: string; vehicleType: string; budgetRange: string;
  annualKm: string; customerType: string; purchaseTiming: string; name: string; phone: string; email: string; legal: boolean;
};

const initialForm = (context: AssistedSearchContext): FormState => ({
  searchType: context.model || context.brand ? "specific" : "", brand: context.brand ?? "", model: context.model ?? "",
  vehicleType: "", budgetRange: "", annualKm: "", customerType: "", purchaseTiming: "", name: "", phone: "", email: "", legal: false,
});
const optionClass = "flex min-h-14 w-full items-center justify-between rounded-lg border border-line bg-white px-4 py-3 text-left text-sm font-bold text-ink outline-none transition-colors hover:border-brand focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2";
const fieldClass = "mt-1.5 h-12 w-full rounded-lg border border-line bg-white px-3 text-base font-semibold text-ink outline-none focus:border-brand focus-visible:ring-2 focus-visible:ring-brand/30";

function eventDetails(context: AssistedSearchContext, form: FormState) {
  return { source_page: context.sourcePage, brand: form.brand || undefined, model: form.model || undefined, customer_type: form.customerType || undefined, budget_range: form.budgetRange || undefined };
}

export function AssistedSearchCTA({ context, catalogue, compact = false }: { context: AssistedSearchContext; catalogue: AssistedSearchVehicleOption[]; compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormState>(() => initialForm(context));
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [message, setMessage] = useState("");
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [honey, setHoney] = useState("");
  const ctaRef = useRef<HTMLElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const viewed = useRef(false);
  const submissionKey = useRef("");
  const brandModels = catalogue.find((item) => item.brand === form.brand)?.models ?? [];
  const knownName = [context.brand, context.model].filter(Boolean).join(" ");
  const title = context.model ? `¿No encuentras el ${knownName} que buscas?` : context.brand ? `¿Buscas un ${context.brand}?` : "¿No encuentras el coche que buscas?";
  const button = context.model ? `Encontrar mi ${knownName}` : context.brand ? `Encontrar mi ${context.brand}` : "Ayúdame a encontrar coche";

  useEffect(() => {
    const node = ctaRef.current;
    if (!node || viewed.current) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting || viewed.current) return;
      viewed.current = true;
      trackAnalyticsEvent("assisted_search_cta_view", eventDetails(context, form));
      observer.disconnect();
    }, { threshold: 0.35 });
    observer.observe(node);
    return () => observer.disconnect();
  }, [context, form]);

  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const values = Object.fromEntries(["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"].map((key) => [key, params.get(key) ?? ""]));
      if (Object.values(values).some(Boolean)) window.sessionStorage.setItem("myrenting_utm", JSON.stringify(values));
    } catch {}
  }, []);

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    const trigger = triggerRef.current;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    const handleKeyboard = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
      if (event.key !== "Tab") return;
      const focusable = [...(dialogRef.current?.querySelectorAll<HTMLElement>('button:not([disabled]), a[href], input:not([disabled]), select:not([disabled])') ?? [])];
      if (!focusable.length) return;
      const first = focusable[0]; const last = focusable.at(-1)!;
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    window.addEventListener("keydown", handleKeyboard);
    return () => { document.body.style.overflow = previous; window.removeEventListener("keydown", handleKeyboard); trigger?.focus(); };
  }, [open]);

  function start() {
    setOpen(true);
    trackAnalyticsEvent("assisted_search_started", { ...eventDetails(context, form), journey_stage: "assisted_search_start" });
  }

  function patch(values: Partial<FormState>) { setForm((current) => ({ ...current, ...values })); }
  function canContinue() {
    if (step === 1) return Boolean(form.searchType && (form.searchType !== "specific" || form.brand) && (form.searchType !== "type" || form.vehicleType));
    if (step === 2) return Boolean(form.budgetRange);
    if (step === 3) return Boolean(form.annualKm);
    if (step === 4) return Boolean(form.customerType && form.purchaseTiming);
    return true;
  }
  function next() {
    if (!canContinue()) return;
    trackAnalyticsEvent(`assisted_search_step_${step}`, { ...eventDetails(context, form), journey_stage: `assisted_search_step_${step}` });
    const nextStep = Math.min(step + 1, 5);
    setStep(nextStep);
    if (nextStep === 5) trackAnalyticsEvent("assisted_search_contact_view", eventDetails(context, form));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!form.name.trim() || !form.phone.trim() || !form.email.includes("@") || !form.legal) return;
    setState("sending"); setMessage("");
    trackAnalyticsEvent("lead_submit_attempt", { ...eventDetails(context, form), journey_stage: "lead_submit_attempt", form_name: "assisted_search" });
    const params = new URLSearchParams(window.location.search);
    let storedUtm: Record<string, string> = {};
    try { storedUtm = JSON.parse(window.sessionStorage.getItem("myrenting_utm") ?? "{}"); } catch {}
    const utm = (key: string) => params.get(key) ?? storedUtm[key] ?? "";
    if (!submissionKey.current) submissionKey.current = crypto.randomUUID();
    try {
      const response = await fetch("/api/leads", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
        leadType: "assisted_search", name: form.name, phone: form.phone, email: form.email, customerType: form.customerType,
        searchType: form.searchType, brand: form.brand, model: form.model, vehicleType: form.vehicleType, budgetRange: form.budgetRange,
        annualKm: form.annualKm, purchaseTiming: form.purchaseTiming, sourcePage: context.sourcePage, pageUrl: window.location.href,
        referrer: document.referrer, utmSource: utm("utm_source"), utmMedium: utm("utm_medium"), utmCampaign: utm("utm_campaign"),
        utmContent: utm("utm_content"), utmTerm: utm("utm_term"), legalAccepted: form.legal, website: honey, submissionKey: submissionKey.current,
      }) });
      const result = await response.json().catch(() => null) as { reference?: string; recommendations?: Recommendation[]; error?: string } | null;
      if (!response.ok) throw new Error(result?.error ?? "No se pudo registrar la solicitud.");
      await fetch("https://formsubmit.co/ajax/mtiagconsulting@gmail.com", { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify({
        nombre: form.name, telefono: form.phone, email: form.email, perfil: form.customerType, busqueda: form.searchType,
        marca: form.brand || "Sin definir", modelo: form.model || "Sin definir", tipo_coche: form.vehicleType || "Sin definir",
        presupuesto: form.budgetRange, kilometros_anuales: form.annualKm, cuando_lo_necesita: form.purchaseTiming,
        pagina_origen: context.sourcePage, referencia: result?.reference ?? "", tipo_lead: "assisted_search",
        _subject: `Nueva búsqueda asistida MyRenting — ${form.name}`, _template: "table", _captcha: "false",
      }) }).catch(() => null);
      setRecommendations(result?.recommendations ?? []); setState("sent");
      const successDetails = { ...eventDetails(context, form), journey_stage: "lead_submit_success", form_name: "assisted_search", lead_reference: result?.reference };
      trackAnalyticsEvent("lead_submit_success", successDetails);
      trackAnalyticsEvent("assisted_search_lead", successDetails);
      trackAnalyticsEvent("generate_lead", { ...successDetails, lead_channel: "email" });
    } catch (error) {
      trackAnalyticsEvent("lead_submit_error", { ...eventDetails(context, form), journey_stage: "lead_submit_error", form_name: "assisted_search", error_type: "database_failed" });
      setState("error"); setMessage(error instanceof Error ? error.message : "No se pudo registrar la solicitud.");
    }
  }

  return <>
    <section ref={ctaRef} className={compact ? "rounded-xl border border-line bg-ink p-6 text-white sm:p-8" : "rounded-xl border border-line bg-ink p-6 text-white shadow-card sm:p-8"}>
      <div className="grid gap-5 sm:grid-cols-[1fr_auto] sm:items-center">
        <div><h2 className="font-display text-2xl font-semibold tracking-[-0.035em] sm:text-3xl">{title}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">{context.model ? "Dinos presupuesto, kilómetros y cuándo lo necesitas. Te ayudamos a encontrar las opciones que mejor encajen contigo." : "Dinos qué necesitas y te ayudamos a encontrar las opciones de renting que mejor encajen contigo."}</p></div>
        <button ref={triggerRef} type="button" onClick={start} className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-bold text-white hover:bg-brand-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-ink">{button}<ArrowRight size={17} aria-hidden="true" /></button>
      </div>
    </section>

    {open ? <div className="fixed inset-0 z-[100] flex items-end bg-ink/55 sm:items-center sm:justify-center sm:p-5" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
      <section ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="assisted-search-title" className="flex h-[100dvh] w-full flex-col bg-canvas sm:h-auto sm:max-h-[min(92dvh,760px)] sm:max-w-2xl sm:rounded-2xl sm:border sm:border-line sm:shadow-2xl">
        <header className="flex items-center justify-between border-b border-line px-5 py-4 sm:px-7"><div><p className="text-xs font-bold text-brand">Paso {step} de 5</p><div className="mt-2 flex gap-1.5" aria-label={`Progreso: paso ${step} de 5`}>{[1,2,3,4,5].map((item) => <span key={item} className={`h-1.5 w-8 rounded-full ${item <= step ? "bg-brand" : "bg-slate-200"}`} />)}</div></div><button ref={closeRef} type="button" onClick={() => setOpen(false)} aria-label="Cerrar" className="grid size-11 place-items-center rounded-full border border-line bg-white text-ink hover:border-slate-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"><X size={20} /></button></header>
        <div className="flex-1 overflow-y-auto px-5 py-6 sm:px-8 sm:py-8">
          {state === "sent" ? <Confirmation recommendations={recommendations} /> : <form id="assisted-search-form" onSubmit={submit}>
            {step === 1 ? <StepOne form={form} patch={patch} catalogue={catalogue} models={brandModels} /> : null}
            {step === 2 ? <ChoiceStep title="¿Cuánto quieres pagar como máximo al mes?" note="IVA incluido para particulares." value={form.budgetRange} choose={(value) => patch({ budgetRange: value })} options={["Menos de 250 €","250–300 €","300–400 €","400–500 €","500–700 €","Más de 700 €","No tengo un presupuesto definido"]} /> : null}
            {step === 3 ? <ChoiceStep title="¿Cuántos kilómetros haces aproximadamente al año?" value={form.annualKm} choose={(value) => patch({ annualKm: value })} options={["10.000 km","15.000 km","20.000 km","25.000 km","30.000 km o más","No lo sé"]} /> : null}
            {step === 4 ? <StepFour form={form} patch={patch} /> : null}
            {step === 5 ? <ContactStep form={form} patch={patch} honey={honey} setHoney={setHoney} state={state} message={message} /> : null}
          </form>}
        </div>
        {state !== "sent" ? <footer className="grid grid-cols-[auto_1fr] gap-3 border-t border-line bg-white px-5 py-4 sm:px-7"><button type="button" onClick={() => step === 1 ? setOpen(false) : setStep((current) => current - 1)} className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg border border-line px-4 text-sm font-bold text-ink hover:border-slate-300"><ArrowLeft size={17} />{step === 1 ? "Cerrar" : "Volver"}</button>{step < 5 ? <button type="button" disabled={!canContinue()} onClick={next} className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-40">Continuar<ArrowRight size={17} /></button> : <button form="assisted-search-form" type="submit" disabled={state === "sending"} className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-brand px-5 text-sm font-bold text-white disabled:opacity-50">{state === "sending" ? "Buscando…" : "Buscar mis opciones"}<ArrowRight size={17} /></button>}</footer> : null}
      </section>
    </div> : null}
  </>;
}

function StepTitle({ children, note }: { children: string; note?: string }) { return <div className="mb-6"><h2 id="assisted-search-title" className="font-display text-3xl font-semibold tracking-[-0.04em] text-ink">{children}</h2>{note ? <p className="mt-2 text-sm text-muted">{note}</p> : null}</div>; }
function Selected({ active }: { active: boolean }) { return <span className={`grid size-6 shrink-0 place-items-center rounded-full border ${active ? "border-brand bg-brand text-white" : "border-slate-300"}`}>{active ? <Check size={14} /> : null}</span>; }
function ChoiceStep({ title, note, value, choose, options }: { title: string; note?: string; value: string; choose: (value: string) => void; options: string[] }) { return <><StepTitle note={note}>{title}</StepTitle><div className="grid gap-3 sm:grid-cols-2">{options.map((option) => <button key={option} type="button" onClick={() => choose(option)} className={optionClass} aria-pressed={value === option}><span>{option}</span><Selected active={value === option} /></button>)}</div></>; }
function StepOne({ form, patch, catalogue, models }: { form: FormState; patch: (values: Partial<FormState>) => void; catalogue: AssistedSearchVehicleOption[]; models: string[] }) { const choices: Array<[SearchType,string]> = [["specific","Tengo una marca o modelo concreto"],["type","Busco un tipo de coche"],["unsure","No lo tengo claro"]]; return <><StepTitle>¿Qué coche estás buscando?</StepTitle><div className="grid gap-3">{choices.map(([value,label]) => <button key={value} type="button" onClick={() => patch({ searchType: value })} className={optionClass} aria-pressed={form.searchType === value}><span>{label}</span><Selected active={form.searchType === value} /></button>)}</div>{form.searchType === "specific" ? <div className="mt-5 grid gap-4 sm:grid-cols-2"><label className="text-xs font-bold text-muted">Marca<select className={fieldClass} value={form.brand} onChange={(event) => patch({ brand: event.target.value, model: "" })}><option value="">Selecciona una marca</option>{catalogue.map((item) => <option key={item.brand}>{item.brand}</option>)}</select></label><label className="text-xs font-bold text-muted">Modelo<select className={fieldClass} value={form.model} onChange={(event) => patch({ model: event.target.value })} disabled={!form.brand}><option value="">Cualquier modelo</option>{models.map((model) => <option key={model}>{model}</option>)}</select></label></div> : null}{form.searchType === "type" ? <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">{["Utilitario","Compacto","SUV","Berlina","Familiar","Otro"].map((type) => <button key={type} type="button" onClick={() => patch({ vehicleType: type })} className={optionClass} aria-pressed={form.vehicleType === type}><span>{type}</span><Selected active={form.vehicleType === type} /></button>)}</div> : null}</>; }
function StepFour({ form, patch }: { form: FormState; patch: (values: Partial<FormState>) => void }) { return <><StepTitle>¿Para quién es el coche?</StepTitle><div className="grid gap-3 sm:grid-cols-3">{[["particular","Particular"],["autonomo","Autónomo"],["empresa","Empresa"]].map(([value,label]) => <button key={value} type="button" onClick={() => patch({ customerType: value })} className={optionClass} aria-pressed={form.customerType === value}><span>{label}</span><Selected active={form.customerType === value} /></button>)}</div><h3 className="font-display mt-8 text-2xl font-semibold text-ink">¿Cuándo necesitas el coche?</h3><div className="mt-4 grid gap-3 sm:grid-cols-2">{["Cuanto antes","En menos de 1 mes","En 1–3 meses","En más de 3 meses","Solo estoy mirando"].map((timing) => <button key={timing} type="button" onClick={() => patch({ purchaseTiming: timing })} className={optionClass} aria-pressed={form.purchaseTiming === timing}><span>{timing}</span><Selected active={form.purchaseTiming === timing} /></button>)}</div></>; }
function ContactStep({ form, patch, honey, setHoney, state, message }: { form: FormState; patch: (values: Partial<FormState>) => void; honey: string; setHoney: (value: string) => void; state: string; message: string }) { return <><StepTitle note="Déjanos tus datos y te contactaremos con las opciones que mejor encajen con lo que necesitas.">Ya sabemos qué buscar.</StepTitle><div className="grid gap-4"><label className="text-xs font-bold text-muted">Nombre *<input required autoComplete="name" className={fieldClass} value={form.name} onChange={(event) => patch({ name: event.target.value })} /></label><label className="text-xs font-bold text-muted">Teléfono *<input required type="tel" inputMode="tel" autoComplete="tel" className={fieldClass} value={form.phone} onChange={(event) => patch({ phone: event.target.value })} /></label><label className="text-xs font-bold text-muted">Email *<input required type="email" inputMode="email" autoComplete="email" className={fieldClass} value={form.email} onChange={(event) => patch({ email: event.target.value })} /></label><label className="absolute -left-[10000px] size-px overflow-hidden" aria-hidden="true">Web<input tabIndex={-1} autoComplete="off" value={honey} onChange={(event) => setHoney(event.target.value)} /></label></div><label className="mt-5 flex items-start gap-3 text-xs leading-5 text-muted"><input required type="checkbox" checked={form.legal} onChange={(event) => patch({ legal: event.target.checked })} className="mt-0.5 size-4 shrink-0 accent-[var(--brand)]" /><span>Acepto que MyRenting trate mis datos para responder a esta solicitud. Consulta la <Link href="/legal/privacidad" target="_blank" className="font-bold text-ink underline">política de privacidad</Link>.</span></label>{state === "error" ? <p role="alert" className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{message}</p> : null}</>; }
function Confirmation({ recommendations }: { recommendations: Recommendation[] }) { return <div><CheckCircle2 size={42} className="text-positive" /><StepTitle note="Vamos a revisar las opciones que mejor encajen con lo que buscas. Nos pondremos en contacto contigo para ayudarte a encontrar tu renting.">¡Solicitud recibida!</StepTitle>{recommendations.length ? <div className="mt-8"><h3 className="font-display text-xl font-semibold text-ink">Mientras tanto, puedes echar un vistazo a estas opciones.</h3><div className="mt-4 grid gap-3 sm:grid-cols-3">{recommendations.map((item) => <Link key={item.id} href={item.href} className="overflow-hidden rounded-xl border border-line bg-white hover:border-brand">{item.image ? <div className="relative aspect-[16/10] bg-surface"><Image src={item.image} alt="" fill sizes="200px" className="object-contain" /></div> : null}<div className="p-4"><p className="text-sm font-bold text-ink">{item.name}</p><p className="mt-1 font-data text-xs text-muted">{item.price.toLocaleString("es-ES")} €/mes {item.priceLabel}</p></div></Link>)}</div></div> : null}</div>; }
