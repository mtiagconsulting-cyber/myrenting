import openNextWorker from "./.open-next/worker.js";
import vehicleAliases from "./src/data/vehicle-aliases.json";

function withDeliveryHeaders(response, url) {
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  if (url.pathname.startsWith("/_next/static/")) {
    headers.set("Cache-Control", "public, max-age=31536000, immutable");
  } else if (["/robots.txt", "/sitemap.xml", "/llms.txt"].includes(url.pathname)) {
    headers.set("Cache-Control", "public, max-age=3600, stale-while-revalidate=86400");
  }
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
}

export {
  BucketCachePurge,
  DOQueueHandler,
  DOShardedTagCache,
} from "./.open-next/worker.js";

const worker = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.hostname === "www.myrenting.es") {
      url.hostname = "myrenting.es";
      return Response.redirect(url.toString(), 308);
    }

    if (url.pathname === "/marcas/lynk&co") {
      url.pathname = "/marcas/lynk-co";
      return Response.redirect(url.toString(), 308);
    }

    if (url.pathname === "/sitemap-nuevas.xml") {
      url.pathname = "/sitemap.xml";
      return Response.redirect(url.toString(), 308);
    }

    const duplicateSlug = url.pathname.startsWith("/coches/") ? url.pathname.slice("/coches/".length) : "";
    if (vehicleAliases[duplicateSlug]) {
      url.pathname = `/coches/${vehicleAliases[duplicateSlug]}`;
      return Response.redirect(url.toString(), 308);
    }

    // Keep database-backed endpoints on OpenNext. Every public page is served
    // directly from the asset binding, avoiding the Next.js server runtime and
    // its CPU cost on the Workers Free plan.
    if (url.pathname.startsWith("/api/")) {
      return openNextWorker.fetch(request, env, ctx);
    }

    // Next.js client navigation requests the RSC representation of a static
    // page. It is generated at build time alongside the HTML document.
    if (request.headers.get("rsc") === "1" || url.searchParams.has("_rsc")) {
      const rscUrl = new URL(`${url.pathname.replace(/\/$/, "") || "/index"}.rsc`, url.origin);
      const rscResponse = await env.ASSETS.fetch(new Request(rscUrl, request));
      if (rscResponse.status !== 404) {
        const headers = new Headers(rscResponse.headers);
        headers.set("Content-Type", "text/x-component; charset=utf-8");
        return withDeliveryHeaders(new Response(rscResponse.body, { status: rscResponse.status, headers }), url);
      }
    }

    const assetResponse = await env.ASSETS.fetch(request);
    if (assetResponse.status !== 404) return withDeliveryHeaders(assetResponse, url);

    // Preserve the small set of legacy redirects and generated metadata that
    // do not have a prerendered asset.
    return openNextWorker.fetch(request, env, ctx);
  },
};

export default worker;
