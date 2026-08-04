import { notFound } from "next/navigation";
import { getVehicle } from "@/lib/data";
import { pairs, parsePair, pairSlug } from "@/lib/pairs";
import Breadcrumbs from "@/components/seo/Breadcrumbs";

export function generateStaticParams() { return pairs.map(([a,b]) => ({ slug: pairSlug(a,b) })); }
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params; const p = parsePair(slug); if(!p) return {};
  const A=getVehicle(p[0]), B=getVehicle(p[1]); if(!A||!B) return {};
  return { title: `${A.title} vs ${B.title} en renting — ¿cuál elegir?`, description: `Comparativa de renting entre ${A.title} (${A.precio}€/mes) y ${B.title} (${B.precio}€/mes): precio, consumo, etiqueta y para quién es cada uno.`, alternates: { canonical: `/comparar/${slug}/` } };
}

export default async function Comp({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params; const p = parsePair(slug); if(!p) notFound();
  const A=getVehicle(p[0]), B=getVehicle(p[1]); if(!A||!B) notFound();
  const cheaper = A.precio<=B.precio ? A : B;
  const rows: [string,string,string,("A"|"B"|"")][] = [
    ["Precio /mes", `${A.precio}€`, `${B.precio}€`, A.precio<B.precio?"A":(B.precio<A.precio?"B":"")],
    ["Combustible", A.fuel, B.fuel, ""],
    ["Etiqueta DGT", A.dgt||"—", B.dgt||"—", ""],
    ["Potencia", A.cv||"—", B.cv||"—", ""],
    ["Plazas", A.seats||"—", B.seats||"—", ""],
    ["Consumo", A.cons||"—", B.cons||"—", ""],
  ];
  const ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":`¿${A.title} o ${B.title} en renting?`,"acceptedAnswer":{"@type":"Answer","text":`El ${cheaper.title} tiene la cuota más baja (${cheaper.precio}€/mes). Elige según uso: ${A.title} y ${B.title} encajan en perfiles distintos.`}}]};
  return (
    <div className="mx-auto max-w-[1000px] px-6">
      <script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify(ld)}} />
      <Breadcrumbs items={[{ name: "Comparativas", href: "/comparar" }, { name: `${A.title} vs ${B.title}` }]} />
      <h1 className="text-[34px] font-extrabold text-ink tracking-tight">{A.title} vs {B.title}</h1>
      <div className="bg-white border border-line border-l-[3px] border-l-orange rounded-xl2 px-4.5 py-3.5 text-[15px] text-ink mt-3.5"><b>¿Cuál elegir?</b> El <b>{cheaper.title}</b> es más económico ({cheaper.precio}€/mes). La decisión final depende del uso: mira consumo, etiqueta y plazas.</div>
      <table className="w-full border-collapse bg-white border border-line rounded-xl2 overflow-hidden text-sm mt-4">
        <thead><tr>
          <th className="p-3.5 border-b border-r border-line bg-paper w-[150px]"></th>
          {[A,B].map((v,i)=>(<th key={i} className="p-3.5 border-b border-line text-left border-r last:border-r-0">{v.img&&<img src={v.img} className="w-full max-w-[120px] mb-1.5 object-contain" alt={v.title}/>}<b className="text-ink">{v.title}</b></th>))}
        </tr></thead>
        <tbody>{rows.map(([l,a,b,w],i)=>(<tr key={i}>
          <td className="p-3.5 border-b border-r border-line bg-paper text-muted font-semibold text-[12.5px] uppercase">{l}</td>
          <td className={`p-3.5 border-b border-r border-line ${w==="A"?"text-orange font-extrabold":""}`}>{a}</td>
          <td className={`p-3.5 border-b border-line ${w==="B"?"text-orange font-extrabold":""}`}>{b}</td>
        </tr>))}</tbody>
      </table>
      <div className="grid gap-4 mt-4 md:grid-cols-2">
        <div className="rounded-xl2 border border-line bg-white p-5">
          <h3 className="mb-1.5 text-[15.5px] font-extrabold text-ink">Elegiría el {A.title} si…</h3>
          <p className="m-0 text-[14px] leading-relaxed text-body">
            {A.precio <= B.precio ? "buscas la cuota más ajustada" : "prefieres su combustible o etiqueta"}
            {A.dgt && A.dgt !== "—" ? `, quieres etiqueta ${A.dgt}` : ""} y encaja tu uso ({A.fuel.toLowerCase()}, {A.seats}).
          </p>
        </div>
        <div className="rounded-xl2 border border-line bg-white p-5">
          <h3 className="mb-1.5 text-[15.5px] font-extrabold text-ink">Elegiría el {B.title} si…</h3>
          <p className="m-0 text-[14px] leading-relaxed text-body">
            {B.precio <= A.precio ? "buscas la cuota más ajustada" : "prefieres su combustible o etiqueta"}
            {B.dgt && B.dgt !== "—" ? `, quieres etiqueta ${B.dgt}` : ""} y encaja tu uso ({B.fuel.toLowerCase()}, {B.seats}).
          </p>
        </div>
      </div>
      <div className="bg-orange-soft border border-[#ffdcc2] rounded-xl2 p-5.5 mt-4"><h3 className="text-ink font-extrabold mb-2">Veredicto</h3><p className="text-body text-[14.5px] m-0">Por cuota, gana el <b>{cheaper.title}</b>. Si tu prioridad es otra (espacio, etiqueta, potencia), revisa la tabla: ambos son buenas opciones según el perfil de uso.</p></div>
    </div>
  );
}
