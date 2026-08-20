import Link from "next/link";
import { notFound } from "next/navigation";
import { vehicles, getVehicle, getMatrix, alternatives } from "@/lib/data";
import VehicleCard from "@/components/VehicleCard";
import Configurator from "@/components/Configurator";

export function generateStaticParams() { return vehicles.map(v => ({ slug: v.slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params; const v = getVehicle(slug);
  if (!v) return {};
  const desc = `Renting del ${v.title} desde ${v.precio}€/mes, sin entrada y con seguro y mantenimiento incluidos. ${v.fuel}${v.dgt&&v.dgt!=="—"?", etiqueta "+v.dgt:""}.`;
  return { title: `Renting ${v.title} desde ${v.precio}€/mes`, description: desc, alternates: { canonical: `/coches/${v.slug}/` } };
}

export default async function Ficha({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params; const v = getVehicle(slug);
  if (!v) notFound();
  const matrix = getMatrix(slug);
  const alts = alternatives(v);
  const faqs = [
    ["¿Qué incluye la cuota?", "Seguro a todo riesgo, mantenimiento y averías, neumáticos, impuestos, asistencia 24 h y gestión de multas. Sin entrada."],
    ["¿Con o sin IVA?", "Particulares con IVA incluido; autónomos y empresas sin IVA (deducible según uso)."],
  ];
  const ld = { "@context":"https://schema.org","@graph":[
    { "@type":"Product","name":`Renting ${v.title}`,"brand":{"@type":"Brand","name":v.make},
      "offers":{"@type":"AggregateOffer","lowPrice":String(v.precio),"priceCurrency":"EUR","availability":"https://schema.org/InStock","url":`https://myrenting.es/coches/${v.slug}/`}},
    { "@type":"Car","name":v.title,"fuelType":v.fuel,"seatingCapacity":v.seats.replace(/\D/g,"")||"5" },
    { "@type":"FAQPage","mainEntity":faqs.map(([q,a])=>({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}})) },
  ]};
  return (
    <div className="mx-auto max-w-[1200px] px-6">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }} />
      <div className="text-[12.5px] text-muted pt-6 pb-2"><Link href="/">Inicio</Link> › <Link href="/coches">Coches</Link> › <b className="text-ink">{v.title}</b></div>
      <h1 className="text-[34px] font-extrabold text-ink tracking-tight">Renting {v.title}</h1>
      <div className="bg-white border border-line border-l-[3px] border-l-orange rounded-xl2 px-4.5 py-3.5 text-[15px] text-ink mt-3.5 max-w-[74ch]">
        El <b>{v.title}</b> ({v.fuel}{v.dgt&&v.dgt!=="—"?`, etiqueta ${v.dgt}`:""}) cuesta desde <b>{v.precio}€/mes</b>, sin entrada y con todo incluido.
      </div>
      <div className="grid md:grid-cols-[1.3fr_1fr] gap-6.5 items-start mt-4">
        <div>
          <div className="bg-white border border-line rounded-[18px] p-6 text-center">{v.img && <img src={v.img} alt={`Renting ${v.title}`} className="w-[86%] max-h-[300px] object-contain mx-auto" />}</div>
          <div className="grid grid-cols-3 border border-line rounded-xl2 overflow-hidden bg-white mt-4">
            {[["Potencia",v.cv],["Etiqueta",v.dgt],["Consumo",v.cons]].map(([k,val],i)=>(<div key={i} className="p-3.5 border-r border-line last:border-0"><div className="text-[11px] uppercase text-muted">{k}</div><div className="font-extrabold text-ink text-[15px] mt-0.5">{val||"—"}</div></div>))}
          </div>
          <div className="bg-white border border-line rounded-xl2 p-5 mt-4">
            <h2 className="text-[19px] font-extrabold text-ink">¿Para quién es?</h2>
            <div className="grid grid-cols-2 gap-3 mt-2.5">
              <div className="border border-line rounded-xl p-3.5"><h4 className="text-ink text-sm font-bold">Encaja si…</h4><p className="text-[13px] text-muted mt-1">Buscas cuota fija con todo incluido y una etiqueta favorable para circular sin restricciones.</p></div>
              <div className="border border-line rounded-xl p-3.5"><h4 className="text-ink text-sm font-bold">Quizá no si…</h4><p className="text-[13px] text-muted mt-1">Necesitas un perfil muy distinto de uso; compara con las alternativas de abajo.</p></div>
            </div>
          </div>
          <div className="bg-white border border-line rounded-xl2 p-5 mt-4">
            <h2 className="text-[19px] font-extrabold text-ink mb-2">Preguntas frecuentes</h2>
            {faqs.map(([q,a],i)=>(<details key={i} open={i===0} className="border-b border-line last:border-0 py-3"><summary className="font-bold text-ink cursor-pointer list-none">{q}</summary><p className="text-[14px] text-muted mt-2">{a}</p></details>))}
          </div>
        </div>
        <div>
          {matrix ? <Configurator name={v.title} matrices={matrix} /> :
            <div className="bg-white border border-line rounded-xl2 p-5"><div className="text-xs text-muted">Cuota desde</div><div className="mono text-[46px] font-extrabold text-ink leading-none">{v.precio}<small className="text-base text-muted"> €/mes</small></div><div className="text-[12.5px] text-muted mt-1 mb-3.5">Sin entrada</div><a href={`https://wa.me/34691766768?text=${encodeURIComponent("Hola, me interesa el renting del "+v.title)}`} target="_blank" rel="noopener" className="block text-center font-bold text-white bg-orange rounded-[11px] py-3.5">Recibir oferta</a></div>}
        </div>
      </div>
      <section className="py-9">
        <h2 className="text-2xl font-extrabold text-ink mb-4">Alternativas por precio</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{alts.map(a=><VehicleCard key={a.slug} v={a} />)}</div>
      </section>
    </div>
  );
}
