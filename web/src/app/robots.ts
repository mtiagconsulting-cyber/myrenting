import type { MetadataRoute } from "next";

const SITE = "https://myrenting.es";

export const dynamic = "force-static";

// Bots de IA (GEO/AEO) explícitamente permitidos para indexación generativa.
const AI_BOTS = [
  "GPTBot",
  "OAI-SearchBot",
  "ChatGPT-User",
  "PerplexityBot",
  "Perplexity-User",
  "Google-Extended",
  "GoogleOther",
  "Applebot-Extended",
  "ClaudeBot",
  "Claude-Web",
  "anthropic-ai",
  "CCBot",
  "Amazonbot",
  "Bytespider",
];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/" },
      ...AI_BOTS.map((userAgent) => ({ userAgent, allow: "/" })),
    ],
    sitemap: `${SITE}/sitemap.xml`,
    host: SITE,
  };
}
