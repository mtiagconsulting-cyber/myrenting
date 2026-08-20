"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  CarFront,
  GitCompareArrows,
  Heart,
  House,
  Menu,
  X,
  type LucideIcon,
} from "lucide-react";
import { Logo } from "@/components/layout/logo";
import { cn } from "@/lib/utils";

type NavigationItem = {
  href: string;
  label: string;
  icon: LucideIcon;
};

const navigation: NavigationItem[] = [
  { href: "/", label: "Inicio", icon: House },
  { href: "/coches", label: "Coches", icon: CarFront },
  { href: "/comparar", label: "Comparar", icon: GitCompareArrows },
  { href: "/favoritos", label: "Favoritos", icon: Heart },
];

const menuLinks = [
  { href: "/renting/suv", label: "Renting SUV" },
  { href: "/renting/hibridos", label: "Renting híbrido" },
  { href: "/renting/electricos", label: "Renting eléctrico" },
  { href: "/renting-barato", label: "Renting barato" },
  { href: "/guias", label: "Guías para elegir" },
];

export function MobileNav() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <>
      <div className="sticky top-0 z-40 flex h-16 items-center border-b border-line bg-surface/95 px-5 backdrop-blur-sm md:hidden">
        <Logo />
        <Link
          href="/comparar"
          className="ml-auto inline-flex min-h-11 items-center rounded-md bg-orange-50 px-3 py-2 text-xs font-bold text-brand"
        >
          Comparar
        </Link>
      </div>

      {menuOpen ? (
        <div className="fixed inset-0 z-50 bg-ink/30 md:hidden" role="presentation">
          <section
            className="absolute inset-x-3 bottom-22 rounded-2xl border border-line bg-surface p-5 shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-label="Menú"
          >
            <div className="flex items-center justify-between border-b border-line pb-4">
              <p className="font-display text-xl font-semibold tracking-tight text-ink">Explorar MyRenting</p>
              <button
                type="button"
                className="grid size-10 place-items-center rounded-lg text-copy hover:bg-slate-100"
                onClick={() => setMenuOpen(false)}
                aria-label="Cerrar menú"
              >
                <X aria-hidden="true" size={20} />
              </button>
            </div>
            <nav className="grid grid-cols-2 gap-2 pt-4" aria-label="Más secciones">
              {menuLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMenuOpen(false)}
                  className="rounded-lg border border-line px-3 py-3 text-sm font-semibold text-ink hover:bg-slate-50"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </section>
        </div>
      ) : null}

      <nav
        className="fixed inset-x-0 bottom-0 z-[60] border-t border-line bg-surface px-2 pb-[env(safe-area-inset-bottom)] shadow-[0_-8px_24px_rgb(16_24_40/0.06)] md:hidden"
        aria-label="Navegación móvil"
      >
        <div className="grid h-17 grid-cols-5">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative flex flex-col items-center justify-center gap-1 text-[0.625rem] font-bold",
                  active ? "text-brand" : "text-muted",
                )}
              >
                <Icon aria-hidden="true" size={20} strokeWidth={active ? 2.4 : 1.8} />
                {item.label}
                {active ? <span className="absolute top-0 h-0.5 w-5 rounded-full bg-brand" /> : null}
              </Link>
            );
          })}

          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            className={cn(
              "relative flex flex-col items-center justify-center gap-1 text-[0.625rem] font-bold",
              menuOpen ? "text-brand" : "text-muted",
            )}
          >
            {menuOpen ? <X aria-hidden="true" size={20} /> : <Menu aria-hidden="true" size={20} />}
            Menú
            {menuOpen ? <span className="absolute top-0 h-0.5 w-5 rounded-full bg-brand" /> : null}
          </button>
        </div>
      </nav>
    </>
  );
}
