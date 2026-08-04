import Link from "next/link";
import { vehicles, sortedByPrice } from "@/lib/data";
import VehicleCard from "@/components/vehicles/VehicleCard";

const pick = (t: string) => vehicles.find(v => v.title === t);
const withImg = sortedByPrice.filter(v => v.img);

export default function Home() {
  const hero = [pick("Hyundai Tucson"), pick("Seat Leon"), pick("Opel Corsa")].filter(Boolean).slice(0,3) as typeof vehicles;
  const heroImgs = (hero.length===3 ? hero : withImg.slice(0,3));
  const quick = [pick("Renault Captur"), pick("Hyundai Tucson"), pick("Peugeot 208")].filter(Boolean) as typeof vehicles;
  const q = quick.length===3 ? quick : withImg.slice(0,3);
  const cats = [
    ["SUV","Espacio y versatilidad","suv"],["Familiares","Comodidad para todos","fam"],
    ["Urbanos","Ágiles y eficientes","urb"],["Eléctricos","Cero emisiones","ele"],
    ["Empresas y autónomos","Deducible y flexible","emp"],
  ] as const;
  const catImg: Record<string,string|undefined> = {
    suv: pick("Hyundai Tucson")?.img, fam: pick("Seat Leon")?.img, urb: pick("Peugeot 208")?.img,
    ele: withImg.find(v=>v.fuel.toLowerCase().includes("eléctr"))?.img, emp: pick("Citroen Berlingo")?.img,
  };
  const pairs = [
    [pick("Renault Captur"), pick("Toyota Yaris")],
    [pick("Hyundai Tucson"), pick("Opel Frontera")],
    [pick("Peugeot 208"), pick("Opel Corsa")],
    [withImg.find(v=>v.fuel.toLowerCase().includes("eléctr")), withImg.filter(v=>v.fuel.toLowerCase().includes("eléctr"))[1]],
  ].map(p=>p.filter(Boolean)).filter(p=>p.length===2) as (typeof vehicles)[];

  return (
    <div className="mx-auto max-w-[1200px] px-6">
      {/* HERO */}
      <section className="grid md:grid-cols-[1fr_1.12fr] gap-9 items-center py-12">
        <div>
          <h1 className="text-[clamp(38px,4.6vw,60px)] font-extrabold text-ink leading-[1.05] tracking-tight">
            El renting perfecto empieza con una <span className="text-orange">buena comparación.</span>
          </h1>
          <p className="text-lg text-muted mt-5 max-w-[42ch] leading-relaxed">
            Comparamos cientos de ofertas reales de las mejores gestoras para que encuentres el coche que mejor encaja contigo. Sin letra pequeña. Sin sorpresas.
          </p>
          <div className="bg-white border border-line rounded-xl2 p-2.5 grid md:grid-cols-[1.5fr_1fr_1fr_auto] gap-1 mt-7 shadow-card">
            <label className="px-3.5 py-2.5"><span className="block text-[11.5px] font-semibold text-muted mb-0.5">¿Qué coche necesitas?</span><input placeholder="Marca, modelo o tipo…" className="w-full text-[14.5px] font-semibold text-ink outline-none bg-transparent" /></label>
            <label className="px-3.5 py-2.5"><span className="block text-[11.5px] font-semibold text-muted mb-0.5">Presupuesto</span><select className="w-full text-[14.5px] font-semibold text-ink outline-none bg-transparent"><option>Máx. €/mes</option><option>300 €</option><option>500 €</option></select></label>
            <label className="px-3.5 py-2.5"><span className="block text-[11.5px] font-semibold text-muted mb-0.5">Km al año</span><select className="w-full text-[14.5px] font-semibold text-ink outline-none bg-transparent"><option>Todos</option><option>10.000</option><option>15.000</option><option>20.000</option></select></label>
            <Link href="/coches" className="bg-orange text-white rounded-xl font-bold text-[15px] px-6 flex items-center justify-center hover:bg-orange-dark">Buscar ofertas</Link>
          </div>
          <div className="flex gap-6 flex-wrap mt-6">
            {[["Ofertas reales","de gestoras oficiales"],["Cuotas con y sin IVA","particular o empresa"],["Sin compromiso","ni registro"],["Datos actualizados","cada semana"]].map(([a,b],i)=>(
              <div key={i} className="flex gap-2.5 items-start text-[13px] text-muted max-w-[180px]">
                <span className="w-6 h-6 flex-none rounded-lg bg-orange-soft text-orange grid place-items-center font-black text-xs">✓</span>
                <span><b className="block text-ink font-semibold">{a}</b>{b}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="relative">
          <div className="flex items-center justify-center px-2.5">
            {heroImgs.map((v,i)=>(
              <img key={i} src={v.img} alt={v.title}
                className={`object-contain drop-shadow-[0_24px_26px_rgba(16,24,40,.20)] ${i===1?"w-[48%] z-20":"w-[40%] z-10"} ${i===0?"mr-[-9%]":""} ${i===2?"ml-[-9%]":""}`} />
            ))}
          </div>
          <div className="bg-white border border-line rounded-xl2 p-5 shadow-pop -mt-7 relative z-30 max-w-[560px] mx-auto">
            <div className="flex justify-between items-center mb-1.5"><b className="text-ink text-[15.5px]">Comparativa rápida</b><Link href="/comparar" className="text-orange text-[12.5px] font-semibold">Ver todas ›</Link></div>
            <div className="grid grid-cols-3 gap-3">
              {q.map((v,i)=>(
                <div key={i} className={`text-center pt-2 ${i>0?"border-l border-line":""}`}>
                  {v.img && <img src={v.img} alt={v.title} className="w-[88%] h-[52px] object-contain mx-auto" />}
                  <div className="font-semibold text-ink text-[13px] mt-1">{v.title}</div>
                  <div className="text-[11px] text-muted">{v.fuel}</div>
                  <div className="text-[10.5px] text-muted mt-1.5">Desde</div>
                  <div className="font-extrabold text-ink text-base mono">{v.precio}<small className="text-[10px] text-muted">€/mes</small></div>
                  <Link href={`/coches/${v.slug}`} className="text-orange text-[11.5px] font-semibold mt-1 block">Ver oferta ›</Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CATEGORÍAS */}
      <section className="py-7">
        <h2 className="text-[clamp(23px,2.4vw,30px)] font-extrabold text-ink mb-4.5">Explora por lo que necesitas</h2>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3.5">
          {cats.map(([n,s,k],i)=>(
            <Link key={i} href="/coches" className="bg-white border border-line rounded-xl2 px-4 pt-4.5 pb-0 min-h-[158px] flex flex-col hover:border-orange hover:shadow-card transition overflow-hidden">
              <b className="text-ink text-[15px]">{n}</b><span className="text-xs text-muted">{s}</span>
              {catImg[k] && <img src={catImg[k]} alt={n} className="w-full h-[70px] object-contain mt-auto" />}
            </Link>
          ))}
          <div className="bg-orange-soft border border-[#ffdcc2] rounded-xl2 p-4.5 flex flex-col">
            <b className="text-ink text-[15px]">¿No sabes qué elegir?</b>
            <p className="text-[12.5px] text-body my-1.5 leading-snug">Te ayudamos a encontrar el coche ideal según tu caso en menos de 1 minuto.</p>
            <Link href="/coches" className="mt-auto bg-orange text-white font-bold text-[13px] rounded-[10px] py-2.5 text-center">Ayúdame a elegir ›</Link>
          </div>
        </div>
      </section>

      {/* COMPARATIVAS POPULARES */}
      <section className="py-7">
        <div className="flex justify-between items-center mb-4.5">
          <h2 className="text-[clamp(23px,2.4vw,30px)] font-extrabold text-ink">Comparativas populares</h2>
          <Link href="/comparar" className="text-orange font-semibold text-[13.5px]">Ver todas las comparativas ›</Link>
        </div>
        <div className="grid md:grid-cols-[2.4fr_1fr] gap-4.5 items-start">
          <div className="grid md:grid-cols-2 gap-3.5">
            {pairs.map((p,i)=>(
              <Link key={i} href={`/comparar/${p[0].slug}-vs-${p[1].slug}`} className="bg-white border border-line rounded-xl2 p-4 hover:border-orange">
                <div className="flex items-center gap-2">
                  {[p[0],p[1]].map((v,j)=>(<div key={j} className="flex-1 text-center">{v.img && <img src={v.img} alt={v.title} className="w-full h-[52px] object-contain" />}<b className="block text-ink text-[13px] mt-1">{v.title}</b><span className="text-[11px] text-muted">Desde</span><div className="text-ink font-bold text-[12.5px]">{v.precio}€/mes</div></div>))}
                  {p.length===2 && <div className="order-2 w-[30px] h-[30px] rounded-full bg-paper border border-line grid place-items-center font-black text-xs text-muted">VS</div>}
                </div>
              </Link>
            ))}
          </div>
          <div className="bg-white border border-line rounded-xl2 p-5">
            <b className="text-ink text-[15px]">¿Por qué comparar en myrenting?</b>
            <ul className="mt-3 mb-4 space-y-0 text-[13.5px] text-body">
              {["Información independiente y objetiva","Todas las ofertas en un solo lugar","Cuota real por km y plazo","Ahorra tiempo y dinero"].map((t,i)=>(<li key={i} className="pl-6 relative py-1.5 before:content-['✓'] before:absolute before:left-0 before:text-orange before:font-black">{t}</li>))}
            </ul>
          </div>
        </div>
      </section>

      {/* CIFRAS */}
      <section className="py-7">
        <div className="grid grid-cols-2 md:grid-cols-5 bg-white border border-line rounded-xl2 overflow-hidden">
          {[["63","Modelos comparados"],["190","Ofertas actualizadas"],["3","Gestoras oficiales"],["Semanal","Actualización"],["0€","De entrada"]].map(([n,l],i)=>(
            <div key={i} className="p-6 text-center border-r border-line last:border-0"><div className="text-[26px] font-extrabold text-orange tracking-tight">{n}</div><div className="text-[12.5px] text-muted mt-1">{l}</div></div>
          ))}
        </div>
      </section>
    </div>
  );
}
