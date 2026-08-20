import type { MetadataRoute } from "next";
import { absoluteUrl } from "@/lib/seo";

export default function robots(): MetadataRoute.Robots {
  const privatePaths = ["/api/", "/gestion/", "/opinar", "/*?*marca=", "/*?*presupuesto=", "/*?*kilometros=", "/*?*publico=", "/*?*combustible=", "/*?*carroceria="];
  return { rules: [
    { userAgent: "*", allow: "/", disallow: privatePaths },
    { userAgent: "OAI-SearchBot", allow: "/", disallow: privatePaths },
    { userAgent: "ChatGPT-User", allow: "/", disallow: privatePaths },
  ], sitemap: absoluteUrl("/sitemap.xml"), host: absoluteUrl("/") };
}
