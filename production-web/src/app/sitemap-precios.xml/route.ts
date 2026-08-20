import { sitemapUrls, urlsetXml, xmlHeaders } from "@/lib/sitemaps";
export const dynamic = "force-static";
export function GET() { return new Response(urlsetXml(sitemapUrls("sitemap-precios.xml")), { headers: xmlHeaders }); }
