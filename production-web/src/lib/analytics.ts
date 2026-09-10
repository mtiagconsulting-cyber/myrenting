"use client";

export function trackAnalyticsEvent(event: string, details: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;
  const dataLayer = (window as typeof window & { dataLayer?: Array<Record<string, unknown>> }).dataLayer ?? [];
  let attribution: Record<string, unknown> = {};
  try { attribution = JSON.parse(window.sessionStorage.getItem("myrenting_attribution") ?? "{}"); } catch {}
  dataLayer.push({ event, ...details, ...attribution, page_path: window.location.pathname });
  (window as typeof window & { dataLayer?: Array<Record<string, unknown>> }).dataLayer = dataLayer;
}
