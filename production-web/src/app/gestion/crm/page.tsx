import type { Metadata } from "next";
import { CrmApp } from "@/components/crm/CrmApp";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "CRM comercial | MyRenting", robots: { index: false, follow: false, nocache: true } };

export default function CrmPage() { return <main id="contenido-principal"><CrmApp /></main>; }
