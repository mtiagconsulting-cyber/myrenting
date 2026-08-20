import Link from "next/link";
import { Schema, breadcrumbSchema } from "@/components/seo/Schema";

export interface BreadcrumbItem { name: string; path: string; }

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return <><nav aria-label="Migas de pan" className="mb-8 flex items-center gap-2 overflow-hidden text-xs text-muted">{items.map((item, index) => <span key={item.path} className="flex min-w-0 items-center gap-2">{index > 0 ? <span aria-hidden="true">/</span> : null}{index === items.length - 1 ? <span className="truncate text-copy" aria-current="page">{item.name}</span> : <Link href={item.path} className="hover:text-ink">{item.name}</Link>}</span>)}</nav><Schema data={breadcrumbSchema(items)} /></>;
}
