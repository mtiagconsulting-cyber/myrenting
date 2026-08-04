import Link from "next/link";
export const metadata = { title: "Guías y consejos de renting", description: "Guías prácticas de renting: qué incluye, renting vs compra, mejores híbridos, cómo calcular kilómetros." };
const guias = ["¿Qué incluye realmente un renting?","Renting vs compra: ¿qué conviene?","Mejores coches híbridos en renting","Cómo calcular tus kilómetros","Renting para autónomos y empresas","Etiquetas DGT y ZBE: qué debes saber"];
export default function Guias(){
  return (<div className="mx-auto max-w-[1200px] px-6">
    <div className="text-[12.5px] text-muted pt-6 pb-2"><Link href="/">Inicio</Link> › <b className="text-ink">Guías y consejos</b></div>
    <h1 className="text-[34px] font-extrabold text-ink tracking-tight">Guías y consejos de renting</h1>
    <div className="grid md:grid-cols-3 gap-4 mt-5">{guias.map((g,i)=>(<div key={i} className="bg-white border border-line rounded-xl2 p-5"><div className="text-[11px] font-bold text-orange uppercase tracking-wide">Guía</div><h3 className="text-ink font-extrabold mt-1.5 leading-snug">{g}</h3></div>))}</div>
  </div>);
}
