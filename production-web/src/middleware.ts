import { NextResponse, type NextRequest } from "next/server";
import p0Redirects from "@/data/p0-redirects.json";
import p1Redirects from "@/data/p1-redirects.json";

const auditRedirects = new Map([...p0Redirects, ...p1Redirects].map(({ source, destination }) => [source, destination]));
const contentConsolidations = new Map([
  ["/blog/mejores-coches-renting-baratos.html", "/blog/renting-barato-2026.html"],
]);

const legacyLandings: Record<string, string> = {
  "/renting-suv": "/renting/suv",
  "/renting-hibridos": "/renting/hibridos",
  "/renting-electricos": "/renting/electricos",
  "/renting-barato": "/renting/baratos",
  "/renting-sin-entrada": "/renting/sin-entrada",
  "/renting-entrega-inmediata": "/renting/entrega-inmediata",
  "/renting-autonomos": "/renting/autonomos",
  "/renting-automaticos": "/renting/automaticos",
  "/renting-etiqueta-eco": "/renting/etiqueta-eco",
  "/renting-etiqueta-cero": "/renting/etiqueta-cero",
  "/renting-furgonetas": "/renting/furgonetas",
  "/renting-gasolina.html": "/renting/gasolina",
  "/renting/furgonetas/menos-de-500-euros": "/renting/furgonetas",
  "/renting-menos-300-euros": "/renting/menos-de-300-euros",
  "/renting-menos-350-euros": "/renting/menos-de-400-euros",
  "/renting-menos-450-euros": "/renting/menos-de-500-euros",
  "/renting-menos-500-euros": "/renting/menos-de-500-euros",
  "/renting-menos-600-euros": "/renting/menos-de-500-euros",
  "/renting-menos-700-euros": "/renting/menos-de-500-euros",
  "/renting/skoda/fabia": "/renting/skoda",
};

function legacyDestination(pathname: string) {
  const audited = auditRedirects.get(pathname);
  if (audited) return audited;
  const consolidated = contentConsolidations.get(pathname);
  if (consolidated) return consolidated;
  if (legacyLandings[pathname]) return legacyLandings[pathname];
  return null;
}

export function middleware(request: NextRequest) {
  const destination = legacyDestination(request.nextUrl.pathname);
  if (!destination || destination === request.nextUrl.pathname) return NextResponse.next();
  return NextResponse.redirect(new URL(destination, request.url), 301);
}

export const config = {
  matcher: ["/:path*.html", "/blog/:path*", "/renting/:path*", "/renting-:path*", "/coches/:path*", "/marcas/:path*", "/modelos/:path*", "/categorias/:path*", "/combustibles/:path*"],
};
