"use client";

export function trackAnalyticsEvent(event: string, details: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;
  const analyticsWindow = window as typeof window & {
    dataLayer?: Array<Record<string, unknown>>;
    gtag?: (command: "event", eventName: string, parameters: Record<string, unknown>) => void;
  };
  const dataLayer = analyticsWindow.dataLayer ?? [];
  let attribution: Record<string, unknown> = {};
  try { attribution = JSON.parse(window.sessionStorage.getItem("myrenting_attribution") ?? "{}"); } catch {}
  let journeyEntryPath = window.location.pathname;
  let previousPagePath = "";
  let journeySequence = 1;
  try {
    journeyEntryPath = window.sessionStorage.getItem("myrenting_journey_entry") || window.location.pathname;
    previousPagePath = window.sessionStorage.getItem("myrenting_previous_page") || "";
    journeySequence = Number(window.sessionStorage.getItem("myrenting_journey_sequence") || "0") + 1;
    window.sessionStorage.setItem("myrenting_journey_entry", journeyEntryPath);
    window.sessionStorage.setItem("myrenting_journey_sequence", String(journeySequence));
  } catch {}
  const parameters = {
    ...details,
    ...attribution,
    page_path: window.location.pathname,
    journey_entry_path: journeyEntryPath,
    previous_page_path: previousPagePath,
    journey_sequence: journeySequence,
  };
  if (analyticsWindow.gtag) {
    analyticsWindow.gtag("event", event, parameters);
  } else {
    dataLayer.push({ event, ...parameters });
    analyticsWindow.dataLayer = dataLayer;
  }
}

export function trackJourneyPageView(path: string, pageType: string) {
  if (typeof window === "undefined") return;
  const previousPagePath = window.sessionStorage.getItem("myrenting_previous_page") || "";
  if (previousPagePath === path) return;
  trackAnalyticsEvent("journey_page_view", { page_type: pageType, previous_page_path: previousPagePath, journey_stage: "page_view" });
  try { window.sessionStorage.setItem("myrenting_previous_page", path); } catch {}
}
