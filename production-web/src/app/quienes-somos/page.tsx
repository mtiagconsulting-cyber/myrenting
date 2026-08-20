import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumb } from "@/components/seo/Breadcrumb";

export const metadata: Metadata = { title: "Quiénes somos", description: "Conoce a MTIAG Consulting, responsable de MyRenting, cómo compara ofertas de renting y cómo se financia.", alternates: { canonical: "/quienes-somos" } };

export default function AboutPage() {
  return <main className="mx-auto max-w-5xl px-5 py-8 sm:px-8 sm:py-12">
    <Breadcrumb items={[{ name: "Inicio", path: "/" }, { name: "Quiénes somos", path: "/quienes-somos" }]} />
    <p className="text-xs font-bold tracking-[0.1em] text-brand uppercase">La organización detrás de los datos</p>
    <h1 className="font-display mt-3 max-w-4xl text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">MyRenting compara condiciones para que una cuota tenga contexto</h1>
    <p className="mt-6 max-w-3xl text-lg leading-8 text-copy">MyRenting es un proyecto de MTIAG Consulting, S.L. dedicado a ordenar ofertas de renting para particulares, autónomos y empresas en España.</p>
    <div className="mt-12 grid gap-8 border-y border-line py-10 md:grid-cols-2">
      <section><h2 className="font-display text-2xl font-semibold">Qué hacemos y cómo funciona</h2><p className="mt-4 text-sm leading-7 text-copy">Recopilamos campañas de M‑Renting, Quadis y otros proveedores incorporados al inventario; normalizamos precio, IVA, entrada, duración, kilometraje y coberturas. MyRenting facilita la comparación y genera solicitudes comerciales, pero la contratación y disponibilidad final dependen del proveedor.</p><h3 className="mt-6 font-bold text-ink">Cómo se financia</h3><p className="mt-2 text-sm leading-7 text-copy">MyRenting puede recibir una comisión cuando una solicitud termina en contratación. Esa relación no altera el precio publicado ni determina el orden de las ofertas, que se basa en criterios visibles.</p><h3 className="mt-6 font-bold text-ink">Cobertura</h3><p className="mt-2 text-sm leading-7 text-copy">El servicio se dirige a clientes en España. No afirmamos disponer de oficinas locales ni publicamos disponibilidad por ciudad hasta que la cobertura de entrega esté confirmada.</p></section>
      <section><h2 className="font-display text-2xl font-semibold">Quién responde</h2><dl className="mt-4 space-y-3 text-sm"><div><dt className="text-muted">Titular</dt><dd className="font-bold text-ink">MTIAG Consulting, S.L.</dd></div><div><dt className="text-muted">CIF</dt><dd className="font-data text-ink">B62559976</dd></div><div><dt className="text-muted">Email</dt><dd><a href="mailto:mtiagconsulting@gmail.com" className="font-bold text-brand">mtiagconsulting@gmail.com</a></dd></div><div><dt className="text-muted">Teléfono</dt><dd><a href="tel:+34691766768" className="font-bold text-brand">691 766 768</a></dd></div></dl></section>
    </div>
    <section className="mt-12 rounded-xl bg-ink p-7 text-white sm:p-9"><p className="text-xs font-bold tracking-[0.1em] text-orange-400 uppercase">Principio editorial</p><h2 className="font-display mt-3 text-3xl font-semibold">No gana el coche que paga más</h2><p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">No utilizamos puntuaciones universales ni presentamos contenido patrocinado como recomendación independiente. Si existe una relación comercial, debe identificarse. Ordenamos ofertas con criterios visibles y corregimos los errores documentados.</p><div className="mt-6 flex flex-wrap gap-5"><Link href="/metodologia" className="font-bold text-orange-400">Metodología →</Link><Link href="/politica-editorial" className="font-bold text-orange-400">Política editorial →</Link></div></section>
  </main>;
}
