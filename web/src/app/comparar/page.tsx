import Link from "next/link";
import { getVehicle } from "@/lib/data";
import { pairs, pairSlug } from "@/lib/pairs";
export const metadata = { title: "Comparativas de renting — ¿cuál elegir?", description: "Comparativas de renting cara a cara: precio, consumo, etiqueta y para quién encaja cada coche." };
export default function Comparar() {
  return (
    <div className="mx-auto max-w-[1200px] px-6">
      <div className="text-[12.5px] text-muted pt-6 pb-2"><Link href="/">Inicio</Link> › <b className="text-ink">Comparativas</b></div>
      <h1 className="text-[34px] font-extrabold text-ink tracking-tight">Comparativas de renting</h1>
      <div className="grid md:grid-cols-2 gap-3.5 mt-5">
        {pairs.map(([a,b],i)=>{const A=getVehicle(a)!,B=getVehicle(b)!;return(
          <Link key={i} href={`/comparar/${pairSlug(a,b)}`} className="bg-white border border-line rounded-xl2 p-4 hover:border-orange flex items-center gap-2">
            {[A,B].map((v,j)=>(<div key={j} className="flex-1 text-center">{v.img&&<img src={v.img} className="w-full h-[52px] object-contain" alt={v.title}/>}<b className="block text-ink text-[13px] mt-1">{v.title}</b><div className="text-ink font-bold text-xs">{v.precio}€/mes</div></div>))}
          </Link>);})}
      </div>
    </div>
  );
}
