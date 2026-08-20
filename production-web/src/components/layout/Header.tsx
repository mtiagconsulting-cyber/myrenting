import Link from "next/link";
import { GitCompareArrows } from "lucide-react";
import { Logo } from "@/components/layout/logo";

const navigation = [
  { href: "/coches", label: "Coches" },
  { href: "/renting/suv", label: "SUV" },
  { href: "/renting/hibridos", label: "Híbridos" },
  { href: "/renting/electricos", label: "Eléctricos" },
  { href: "/guias", label: "Guías" },
];

export function Header() {
  return (
    <header className="sticky top-0 z-40 hidden border-b border-line bg-surface/95 backdrop-blur-sm md:block">
      <div className="mx-auto flex h-18 max-w-7xl items-center px-8">
        <Logo className="mr-10 shrink-0" />

        <nav className="flex h-full items-center gap-1" aria-label="Navegación principal">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="inline-flex h-full items-center px-3 text-sm font-semibold text-copy transition-colors hover:text-ink"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <Link
          href="/comparar"
          className="ml-auto inline-flex h-11 items-center gap-2 rounded-lg bg-brand px-4 text-sm font-bold text-white transition-colors hover:bg-brand-hover"
        >
          <GitCompareArrows aria-hidden="true" size={17} strokeWidth={2.2} />
          Comparar coches
        </Link>
      </div>
    </header>
  );
}
