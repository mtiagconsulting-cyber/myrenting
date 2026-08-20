"use client";

import { useSearchParams } from "next/navigation";
import { ReviewForm } from "@/components/reviews/ReviewForm";

export function ReviewInvite() {
  const token = useSearchParams().get("token") ?? "";
  return token
    ? <ReviewForm token={token} />
    : <div className="rounded-xl border border-line bg-slate-50 p-6 text-sm leading-6 text-copy">Este formulario necesita un enlace personal de invitación. Solicítalo a tu contacto de MyRenting.</div>;
}
