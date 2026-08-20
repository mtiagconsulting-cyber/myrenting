"use client";

import { useEffect, useState } from "react";
import { BadgeCheck, Star } from "lucide-react";

export type PublicReview = { id:number;first_name:string;last_initial:string|null;city:string|null;vehicle_name:string|null;customer_type:string|null;rating:number;title:string;comment:string;created_at:string };

export function PublicReviews() {
  const [reviews, setReviews] = useState<PublicReview[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch("/api/reviews")
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((data: { reviews?: PublicReview[] }) => setReviews(data.reviews ?? []))
      .catch(() => setReviews([]))
      .finally(() => setLoading(false));
  }, []);
  const average = reviews.length ? reviews.reduce((sum, item) => sum + item.rating, 0) / reviews.length : 0;

  return <>
    {reviews.length > 0 && <div className="mt-8 border-l-4 border-brand pl-5"><p className="font-data text-4xl font-semibold">{average.toFixed(1)}</p><p className="mt-1 text-sm text-muted">{reviews.length} opiniones verificadas</p></div>}
    {reviews.length ? <section className="mt-10 grid gap-4 md:grid-cols-2">{reviews.map(item => <article key={item.id} className="rounded-xl border border-line bg-surface p-6"><div className="flex items-center justify-between gap-4"><span className="flex gap-0.5 text-brand">{Array.from({length:5},(_,i)=><Star key={i} size={15} className={i<item.rating?"fill-brand":"text-slate-200"}/>)}</span><span className="inline-flex items-center gap-1 text-[0.6875rem] font-bold text-positive"><BadgeCheck size={14}/>Cliente verificado</span></div><h2 className="font-display mt-5 text-2xl font-semibold">{item.title}</h2><p className="mt-3 text-sm leading-6 text-copy">{item.comment}</p><div className="mt-5 border-t border-line pt-4 text-xs text-muted"><strong className="text-ink">{item.first_name} {item.last_initial?`${item.last_initial}.`:""}</strong>{item.city?` · ${item.city}`:""}{item.vehicle_name?` · ${item.vehicle_name}`:""}</div></article>)}</section>
      : <section className="mt-10 rounded-xl border border-dashed border-line bg-slate-50 p-8"><h2 className="font-display text-2xl font-semibold">{loading ? "Cargando experiencias…" : "Estamos recogiendo las primeras experiencias"}</h2>{!loading && <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">Este espacio empieza vacío a propósito: no publicaremos testimonios ficticios para aparentar autoridad.</p>}</section>}
  </>;
}
