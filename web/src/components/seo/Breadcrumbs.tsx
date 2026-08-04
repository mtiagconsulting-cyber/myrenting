import Link from "next/link";
import { JsonLd } from "./JsonLd";

export type Crumb = { name: string; href?: string };

const SITE = "https://myrenting.es";

export default function Breadcrumbs({ items }: { items: Crumb[] }) {
  const all: Crumb[] = [{ name: "Inicio", href: "/" }, ...items];
  const ld = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: all.map((c, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: c.name,
      ...(c.href ? { item: SITE + c.href } : {}),
    })),
  };
  return (
    <>
      <nav className="pb-2 pt-6 text-[12.5px] text-muted" aria-label="Migas de pan">
        {all.map((c, i) => (
          <span key={i}>
            {c.href && i < all.length - 1 ? (
              <Link href={c.href} className="hover:text-ink">{c.name}</Link>
            ) : (
              <b className="text-ink">{c.name}</b>
            )}
            {i < all.length - 1 && " › "}
          </span>
        ))}
      </nav>
      <JsonLd data={ld} />
    </>
  );
}
