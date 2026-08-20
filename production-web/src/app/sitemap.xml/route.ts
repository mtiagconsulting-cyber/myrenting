import { sitemapIndexXml, xmlHeaders } from "@/lib/sitemaps";
export const dynamic = "force-static";
export function GET() { return new Response(sitemapIndexXml(), { headers: xmlHeaders }); }
