import Link from "next/link";
import { sortedByPrice, offerCount, sourceCount } from "@/lib/data";
export const metadata = { title: `Renting de coches en España — ${sortedByPrice.length} modelos comparados`, description: `Compara ${sortedByPrice.length} modelos de renting de ${sourceCount} gestoras. Filtra por combustible, etiqueta y carrocería. Cuotas reales, sin entrada.` };

export default function Coches() {
  const list = sortedByPrice;
  return (
    <div className="mx-auto max-w-[1200px] px-6">
      <div className="text-[12.5px] text-muted pt-6 pb-2"><Link href="/">Inicio</Link> › <b className="text-ink">Coches</b></div>
      <h1 className="text-[34px] font-extrabold text-ink tracking-tight">Renting de coches en España</h1>
      <div className="bg-white border border-line border-l-[3px] border-l-orange rounded-xl2 px-4.5 py-3.5 text-[15px] text-ink mt-3.5 max-w-[74ch]">Comparamos <b>{list.length} modelos</b> de {sourceCount} gestoras. Cuotas reales, con seguro y mantenimiento incluidos y sin entrada.</div>
      <div className="grid md:grid-cols-[250px_1fr] gap-6 items-start mt-5">
        <aside className="bg-white border border-line rounded-xl2 p-4.5 text-[13.5px] sticky top-[84px]">
          {[["Combustible",["Eléctrico","Híbrido","Gasolina","Diésel"]],["Etiqueta",["CERO","ECO","C"]],["Carrocería",["SUV","Urbano","Familiar"]]].map(([h,opts]:any,i)=>(
            <div key={i}><h4 className="mt-4 first:mt-0 mb-2 text-[11px] uppercase tracking-wide text-muted">{h}</h4>
              {opts.map((o:string,j:number)=>(<label key={j} className="flex gap-2 py-1 text-ink"><input type="checkbox" className="accent-orange" />{o}</label>))}
            </div>
          ))}
        </aside>
        <div>
          <div className="flex justify-between mb-3.5 text-sm text-muted"><span><b className="text-ink">{list.length}</b> coches · {offerCount} ofertas</span><span>Ordenar: <b className="text-ink">precio ↑</b></span></div>
          {list.map(v=>(
            <Link key={v.slug} href={`/coches/${v.slug}`} className="grid md:grid-cols-[190px_1fr_210px] gap-5 bg-white border border-line rounded-xl2 p-4 mb-3.5 items-center hover:border-orange hover:shadow-card transition">
              <div className="aspect-[16/11] bg-paper rounded-[10px] grid place-items-center">{v.img && <img src={v.img} alt={v.title} className="w-[94%] h-[90%] object-contain" />}</div>
              <div>
                <div className="font-semibold text-ink text-lg">{v.title}</div>
                <div className="text-[13px] text-muted">{v.fuel}</div>
                <div className="mt-3 flex gap-4.5 flex-wrap text-[12.5px] text-muted">{[v.cv,v.seats,v.cons,v.dgt&&v.dgt!=="—"?"Etiqueta "+v.dgt:""].filter(x=>x&&x!=="—").map((x,i)=>(<span key={i}>{x}</span>))}</div>
              </div>
              <div className="text-right">
                <div className="text-[11px] text-muted">desde</div>
                <div className="mono text-[26px] font-extrabold text-ink">{v.precio}<small className="text-xs text-muted font-bold"> €/mes</small></div>
                <div className="text-[11px] text-muted mb-3">IVA incl · sin entrada</div>
                <span className="inline-block bg-orange text-white font-bold text-sm rounded-[11px] px-4.5 py-3">Ver ofertas</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
