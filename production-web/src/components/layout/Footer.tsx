import Link from "next/link";
import { Logo } from "@/components/layout/logo";

const columns = [
  {
    title: "Encontrar renting",
    links: [
      ["Todos los coches", "/coches"],
      ["SUV", "/renting/suv"],
      ["Híbridos", "/renting/hibridos"],
      ["Eléctricos", "/renting/electricos"],
    ],
  },
  {
    title: "Decidir mejor",
    links: [
      ["Comparar coches", "/comparar"],
      ["Guías", "/guias"],
      ["Cómo comparamos", "/metodologia"],
      ["Preguntas frecuentes", "/preguntas-frecuentes"],
      ["Centro de respuestas", "/respuestas"],
      ["Informe 2026", "/informes/renting-espana-2026"],
    ],
  },
  {
    title: "MyRenting",
    links: [
      ["Quiénes somos", "/quienes-somos"],
      ["Opiniones", "/opiniones"],
      ["Política editorial", "/politica-editorial"],
      ["Metodología", "/metodologia"],
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-line bg-surface pb-20 md:pb-0">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-12 sm:px-8 md:grid-cols-[1.25fr_2fr] md:py-16">
        <div>
          <Logo />
          <p className="mt-5 max-w-xs text-sm leading-6 text-muted">
            Comparamos vehículos, ofertas y condiciones para ayudarte a elegir tu renting con criterio.
          </p>
          <p className="font-data mt-5 text-xs text-muted">Datos claros · Sin puntuaciones inventadas</p>
        </div>

        <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
          {columns.map((column) => (
            <div key={column.title}>
              <h2 className="text-xs font-bold tracking-[0.08em] text-ink uppercase">{column.title}</h2>
              <ul className="mt-4 space-y-3">
                {column.links.map(([label, href]) => (
                  <li key={href}>
                    <Link href={href} className="-my-2 inline-flex min-h-11 items-center py-2 text-sm text-muted transition-colors hover:text-ink">
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-line">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-5 py-5 text-xs text-muted sm:px-8 md:flex-row md:items-center md:justify-between">
          <p>© {new Date().getFullYear()} MyRenting</p>
          <div className="flex flex-wrap gap-4"><Link href="/legal/aviso-legal" className="hover:text-ink">Aviso legal</Link><Link href="/legal/privacidad" className="hover:text-ink">Privacidad</Link><Link href="/legal/cookies" className="hover:text-ink">Cookies</Link></div>
        </div>
      </div>
    </footer>
  );
}
