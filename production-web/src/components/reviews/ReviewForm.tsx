"use client";

import { useState, type FormEvent } from "react";
import { CheckCircle2, Star } from "lucide-react";

export function ReviewForm({ token }: { token: string }) {
  const [rating, setRating] = useState(5);
  const [state, setState] = useState<"idle" | "sending" | "done" | "error">("idle");
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("sending");
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/reviews", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ token, rating, firstName: form.get("firstName"), lastName: form.get("lastName"), city: form.get("city"), title: form.get("title"), comment: form.get("comment"), website: form.get("website"), consent: form.get("consent") === "on" }) });
    const data = await response.json() as { error?: string };
    if (!response.ok) { setMessage(data.error ?? "No se pudo guardar la opinión."); setState("error"); return; }
    setState("done");
  }

  if (state === "done") return <div className="rounded-xl border border-positive/20 bg-emerald-50 p-7"><CheckCircle2 className="text-positive" size={28} /><h2 className="font-display mt-4 text-2xl font-semibold text-ink">Gracias por contarlo</h2><p className="mt-3 text-sm leading-6 text-copy">Tu opinión ha quedado pendiente de revisión. Publicaremos el texto sin modificar su significado y nunca mostraremos tus datos de contacto.</p></div>;

  return <form onSubmit={submit} className="rounded-xl border border-line bg-surface p-5 shadow-card sm:p-8">
    <fieldset><legend className="text-sm font-bold text-ink">¿Cómo valorarías tu experiencia?</legend><div className="mt-3 flex gap-1" aria-label={`${rating} de 5 estrellas`}>{[1,2,3,4,5].map((value)=><button key={value} type="button" onClick={()=>setRating(value)} className="rounded-md p-1 focus:outline-none focus:ring-2 focus:ring-brand" aria-label={`${value} estrellas`}><Star size={28} className={value<=rating?"fill-brand text-brand":"text-slate-300"}/></button>)}</div></fieldset>
    <div className="mt-6 grid gap-4 sm:grid-cols-2"><Field label="Nombre" name="firstName" required/><Field label="Apellido" name="lastName"/><Field label="Ciudad" name="city"/><Field label="Título de la opinión" name="title" required/></div>
    <label className="mt-4 block"><span className="text-xs font-bold text-ink">Cuéntanos tu experiencia</span><textarea name="comment" required minLength={30} maxLength={1500} rows={7} className="mt-2 w-full rounded-lg border border-line bg-white p-3 text-sm text-ink outline-none focus:border-brand" placeholder="¿Qué te ayudó a decidir? ¿Cómo fue la atención? ¿Qué mejorarías?"/></label>
    <label className="sr-only">No rellenar<input name="website" tabIndex={-1} autoComplete="off"/></label>
    <label className="mt-4 flex items-start gap-3 text-xs leading-5 text-muted"><input name="consent" required type="checkbox" className="mt-0.5 size-4 accent-orange-600"/><span>Autorizo a MyRenting a publicar esta opinión mostrando mi nombre, inicial del apellido, ciudad, vehículo y tipo de cliente. Confirmo que describe una experiencia real.</span></label>
    {state==="error"&&<p role="alert" className="mt-4 text-sm font-semibold text-red-700">{message}</p>}
    <button disabled={state==="sending"} className="mt-6 h-12 rounded-lg bg-brand px-6 text-sm font-bold text-white hover:bg-brand-hover disabled:opacity-60">{state==="sending"?"Guardando…":"Enviar mi opinión"}</button>
    <p className="mt-4 text-[0.6875rem] leading-5 text-muted">Todas las opiniones se revisan únicamente para eliminar datos personales, contenido ilícito o spam. No se rechazan por ser negativas.</p>
  </form>;
}

function Field({label,name,required=false}:{label:string;name:string;required?:boolean}) { return <label><span className="text-xs font-bold text-ink">{label}</span><input name={name} required={required} maxLength={100} className="mt-2 h-11 w-full rounded-lg border border-line bg-white px-3 text-sm text-ink outline-none focus:border-brand"/></label>; }
