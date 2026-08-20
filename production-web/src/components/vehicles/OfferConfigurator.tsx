"use client";

import { useMemo, useState, type FormEvent } from "react";
import { useSearchParams } from "next/navigation";
import { Check, CheckCircle2, Mail, MessageCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Offer, OfferAudience } from "@/types/offer";
import type { Vehicle } from "@/types/vehicle";
import { buildFormSubmitPayload, buildLeadEvent, buildLeadMessage, type LeadChannel } from "@/lib/lead";

const audienceLabel: Record<OfferAudience, string> = { particular: "Particular", autonomo: "Autónomo", empresa: "Empresa" };
const fieldClass = "h-11 w-full rounded-lg border border-line bg-white px-3 text-sm font-semibold text-ink outline-none focus:border-brand";

export function OfferConfigurator({ vehicle, offers, initialOffer }: { vehicle: Vehicle; offers: Offer[]; initialOffer: Offer }) {
  const searchParams = useSearchParams();
  const requestedAudience = searchParams.get("publico");
  const requestedOffer = offers.find((item) => item.audience === requestedAudience) ?? initialOffer;
  const [selectedId, setSelectedId] = useState(requestedOffer.id);
  const [name, setName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [city, setCity] = useState("");
  const [sendState, setSendState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [sendMessage, setSendMessage] = useState("");
  const [leadReference, setLeadReference] = useState("");
  const [honey, setHoney] = useState("");
  const selected = offers.find((offer) => offer.id === selectedId) ?? initialOffer;
  const audiences = useMemo(() => [...new Set(offers.map((offer) => offer.audience))], [offers]);
  const durations = useMemo(() => [...new Set(offers.filter((offer) => offer.audience === selected.audience).map((offer) => offer.duration))].sort((a, b) => a - b), [offers, selected.audience]);
  const kilometers = useMemo(() => [...new Set(offers.filter((offer) => offer.audience === selected.audience && offer.duration === selected.duration).map((offer) => offer.kilometers))].sort((a, b) => a - b), [offers, selected.audience, selected.duration]);

  function choose(criteria: Partial<Pick<Offer, "audience" | "duration" | "kilometers">>) {
    const desired = { audience: selected.audience, duration: selected.duration, kilometers: selected.kilometers, ...criteria };
    const match = offers.find((offer) => offer.audience === desired.audience && offer.duration === desired.duration && offer.kilometers === desired.kilometers)
      ?? offers.find((offer) => offer.audience === desired.audience && offer.duration === desired.duration)
      ?? offers.find((offer) => offer.audience === desired.audience);
    if (match) setSelectedId(match.id);
  }

  function trackLead(channel: LeadChannel) {
    const dataLayer = (window as typeof window & { dataLayer?: Array<Record<string, unknown>> }).dataLayer ?? [];
    let attribution: Record<string, unknown> = {};
    try { attribution = JSON.parse(window.sessionStorage.getItem("myrenting_attribution") ?? "{}"); } catch {}
    dataLayer.push({ ...buildLeadEvent(channel, vehicle, selected), ...attribution });
    (window as typeof window & { dataLayer?: Array<Record<string, unknown>> }).dataLayer = dataLayer;
  }

  async function openChannel(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (![name, lastName, phone, email, city].every((value) => value.trim())) return;
    const channel = ((event.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null)?.value === "whatsapp" ? "whatsapp" : "email";
    if (honey) {
      setSendState("sent");
      setSendMessage("Solicitud enviada correctamente. Te contactaremos lo antes posible.");
      return;
    }
    const contact = { name, lastName, phone, email, city };
    const text = buildLeadMessage(contact, vehicle, selected);
    let reference = "";
    try {
      const leadResponse = await fetch("/api/leads", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ firstName: name, lastName, phone, email, city, customerType: selected.audience, vehicleId: vehicle.id, vehicleName: `${vehicle.brand} ${vehicle.model} ${vehicle.version}`, offerId: selected.id, provider: selected.provider, duration: selected.duration, kilometers: selected.kilometers, monthlyPrice: selected.monthlyPrice, priceIncludesVat: selected.priceIncludesVat, initialPayment: selected.initialPayment, channel, pageUrl: window.location.href, website: honey }) });
      const leadResult = await leadResponse.json().catch(() => null) as { reference?: string } | null;
      if (leadResponse.ok && leadResult?.reference) { reference = leadResult.reference; setLeadReference(reference); }
    } catch {}
    if (channel === "whatsapp") {
      trackLead("whatsapp");
      window.location.href = `https://wa.me/34691766768?text=${encodeURIComponent(reference ? `${text}\nReferencia MyRenting: ${reference}` : text)}`;
      return;
    }

    setSendState("sending");
    setSendMessage("");
    try {
      const response = await fetch("https://formsubmit.co/ajax/mtiagconsulting@gmail.com", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(buildFormSubmitPayload(contact, vehicle, selected, window.location.href, honey)),
      });
      const result = await response.json().catch(() => null) as { success?: string | boolean; message?: string } | null;
      if (!response.ok || result?.success === false || result?.success === "false") throw new Error(result?.message || "No se pudo enviar la solicitud.");
      trackLead("email");
      setSendState("sent");
      setSendMessage(reference ? `Solicitud enviada correctamente. Referencia: ${reference}. Te contactaremos lo antes posible.` : "Solicitud enviada correctamente. Te contactaremos lo antes posible.");
    } catch {
      setSendState("error");
      setSendMessage("No hemos podido enviar la solicitud. Inténtalo de nuevo o utiliza WhatsApp.");
    }
  }

  return <aside id="oferta" className="rounded-xl border border-line bg-surface p-5 shadow-card lg:sticky lg:top-26 sm:p-7">
    <div className="flex items-center justify-between gap-3"><Badge tone={selected.availability === "Disponible" ? "positive" : "neutral"}>{selected.availability}</Badge><span className="font-data text-[0.625rem] font-semibold tracking-wide text-muted">{selected.provider}</span></div>
    <p className="mt-6 text-xs font-bold tracking-wide text-muted uppercase">Configura tu cuota</p>
    <p className="font-data mt-1 text-5xl font-semibold tracking-[-0.07em] text-ink tabular-nums">{selected.monthlyPrice} €<span className="font-sans text-sm font-semibold tracking-normal text-muted">/mes</span></p>
    <p className="mt-2 text-xs font-bold text-muted">{audienceLabel[selected.audience]} · {selected.priceIncludesVat ? "IVA incluido" : "+ IVA"}</p>

    <div className="mt-6 grid grid-cols-2 gap-3">
      {audiences.length > 1 && <label className="col-span-2 text-xs font-bold text-muted">Perfil<select className={`${fieldClass} mt-1.5`} value={selected.audience} onChange={(event) => choose({ audience: event.target.value as OfferAudience })}>{audiences.map((audience) => <option key={audience} value={audience}>{audienceLabel[audience]}</option>)}</select></label>}
      <label className="text-xs font-bold text-muted">Duración<select className={`${fieldClass} mt-1.5`} value={selected.duration} onChange={(event) => choose({ duration: Number(event.target.value) })}>{durations.map((duration) => <option key={duration} value={duration}>{duration} meses</option>)}</select></label>
      <label className="text-xs font-bold text-muted">Kilómetros/año<select className={`${fieldClass} mt-1.5`} value={selected.kilometers} onChange={(event) => choose({ kilometers: Number(event.target.value) })}>{kilometers.map((km) => <option key={km} value={km}>{km.toLocaleString("es-ES")} km</option>)}</select></label>
    </div>

    <dl className="mt-5 divide-y divide-line border-y border-line text-sm"><Row label="Entrada" value={selected.initialPayment === 0 ? "0 €" : `${selected.initialPayment.toLocaleString("es-ES")} €`} /><Row label="Coste estimado" value={`${(selected.monthlyPrice * selected.duration + selected.initialPayment).toLocaleString("es-ES")} €`} /></dl>
    <div className="mt-5 space-y-2 text-xs font-semibold text-copy"><Included label="Seguro" active={selected.insurance} /><Included label="Mantenimiento" active={selected.maintenance} /><Included label="Neumáticos" active={selected.tyres} /></div>
    <div className="mt-5 rounded-lg bg-slate-50 px-3 py-3 text-[0.6875rem] leading-5 text-muted"><p>Fuente: {selected.sourceUrl ? <a href={selected.sourceUrl} target="_blank" rel="noreferrer noopener nofollow" className="font-bold text-copy underline">oferta del proveedor</a> : <span className="font-semibold text-copy">documentación facilitada por el proveedor</span>}.</p>{selected.verifiedAt ? <p>Verificada el <time dateTime={selected.verifiedAt}>{new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "long", year: "numeric" }).format(new Date(selected.verifiedAt))}</time>.</p> : null}</div>

    <form className="mt-6 border-t border-line pt-6" onSubmit={openChannel}>
      <p className="font-display text-xl font-semibold tracking-[-0.03em] text-ink">Solicita esta configuración</p>
      <p className="mt-1 text-xs leading-5 text-muted">La oferta elegida se incluirá automáticamente en el mensaje.</p>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <label className="absolute -left-[10000px] top-auto size-px overflow-hidden" aria-hidden="true">Sitio web<input tabIndex={-1} autoComplete="off" value={honey} onChange={(event) => setHoney(event.target.value)} /></label>
        <label className="text-xs font-bold text-muted">Nombre<input required autoComplete="given-name" className={`${fieldClass} mt-1.5`} value={name} onChange={(event) => setName(event.target.value)} placeholder="Nombre" /></label>
        <label className="text-xs font-bold text-muted">Apellidos<input required autoComplete="family-name" className={`${fieldClass} mt-1.5`} value={lastName} onChange={(event) => setLastName(event.target.value)} placeholder="Apellidos" /></label>
        <label className="text-xs font-bold text-muted">Teléfono<input required type="tel" inputMode="tel" autoComplete="tel" className={`${fieldClass} mt-1.5`} value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="600 000 000" /></label>
        <label className="text-xs font-bold text-muted">Email<input required type="email" inputMode="email" autoComplete="email" className={`${fieldClass} mt-1.5`} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="nombre@email.com" /></label>
        <label className="col-span-2 text-xs font-bold text-muted">Ciudad<input required autoComplete="address-level2" className={`${fieldClass} mt-1.5`} value={city} onChange={(event) => setCity(event.target.value)} placeholder="Tu ciudad" /></label>
      </div>
      <label className="mt-4 flex items-start gap-2.5 text-[0.6875rem] leading-5 text-muted"><input required type="checkbox" className="mt-1 size-4 shrink-0 accent-[var(--brand)]" />Acepto que MyRenting utilice estos datos para responder a esta solicitud.</label>
      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        <button disabled={sendState === "sending" || sendState === "sent"} type="submit" name="channel" value="email" className="flex h-12 items-center justify-center gap-2 rounded-lg bg-brand px-3 text-sm font-bold text-white hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-60">{sendState === "sent" ? <CheckCircle2 size={17} /> : <Mail size={17} />}{sendState === "sending" ? "Enviando…" : sendState === "sent" ? "Enviado" : "Enviar solicitud"}</button>
        <button type="submit" name="channel" value="whatsapp" className="flex h-12 items-center justify-center gap-2 rounded-lg bg-[#087443] px-3 text-sm font-bold text-white hover:bg-[#066238]"><MessageCircle size={17} />Abrir WhatsApp</button>
      </div>
      {sendMessage && <p role="status" className={`mt-3 rounded-lg px-3 py-2 text-xs font-semibold ${sendState === "sent" ? "bg-emerald-50 text-positive" : "bg-red-50 text-red-700"}`}>{sendMessage}</p>}
      {leadReference ? <p className="mt-2 font-data text-[0.625rem] text-muted">Guarda tu referencia: {leadReference}</p> : null}
      <p className="mt-3 text-[0.625rem] leading-4 text-muted">La solicitud se envía directamente a MyRenting sin abrir tu correo. WhatsApp permanece disponible como alternativa.</p>
    </form>
  </aside>;
}

function Row({ label, value }: { label: string; value: string }) { return <div className="flex items-center justify-between gap-4 py-3"><dt className="text-muted">{label}</dt><dd className="font-data text-xs font-semibold text-ink">{value}</dd></div>; }
function Included({ label, active }: { label: string; active: boolean | null }) { return <p className="flex items-center justify-between"><span className="flex items-center gap-2"><Check size={14} className={active ? "text-positive" : "text-slate-300"} aria-hidden="true" />{label}</span><span className={active ? "text-positive" : "text-muted"}>{active === null ? "No consta" : active ? "Incluido" : "No incluido"}</span></p>; }
