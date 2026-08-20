import type { Metadata } from "next";
import { ReviewManager } from "@/components/reviews/ReviewManager";
export const metadata:Metadata={title:"Gestión de opiniones",robots:{index:false,follow:false}};
export default function ReviewManagementPage(){return <main className="mx-auto max-w-5xl px-5 py-10 sm:px-8 sm:py-16"><p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">Uso interno</p><h1 className="font-display mt-3 mb-9 text-4xl font-semibold tracking-[-0.05em] text-ink">Opiniones de clientes</h1><ReviewManager/></main>}
