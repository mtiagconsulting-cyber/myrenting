import type { Metadata } from "next";
import { Suspense } from "react";
import { ReviewInvite } from "@/components/reviews/ReviewInvite";

export const metadata:Metadata={title:"Comparte tu experiencia",description:"Envía tu opinión verificada sobre tu experiencia con MyRenting.",robots:{index:false,follow:false}};
export default function ReviewPage(){return <main className="mx-auto max-w-3xl px-5 py-10 sm:px-8 sm:py-16"><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Opinión verificada</p><h1 className="font-display mt-3 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Tu experiencia ayuda a decidir mejor</h1><p className="mt-5 mb-9 max-w-2xl text-base leading-7 text-muted">Queremos publicar experiencias reales, incluidas las críticas. Utiliza el enlace personal que te hemos enviado; nunca mostraremos tu email ni tu teléfono.</p><Suspense fallback={<div className="rounded-xl border border-line bg-slate-50 p-6 text-sm text-copy">Preparando el formulario…</div>}><ReviewInvite/></Suspense></main>}
