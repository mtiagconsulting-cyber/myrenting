"use client";

import Link from "next/link";
import type { ComponentProps } from "react";
import { trackAnalyticsEvent } from "@/lib/analytics";

type Props = ComponentProps<typeof Link> & {
  ctaName: string;
  journeyStage?: string;
};

export function TrackedLink({ ctaName, journeyStage = "navigation", href, onClick, ...props }: Props) {
  const destination = typeof href === "string" ? href : href.pathname ?? "";

  return (
    <Link
      {...props}
      href={href}
      onClick={(event) => {
        trackAnalyticsEvent("cta_click", {
          journey_stage: journeyStage,
          cta_name: ctaName,
          destination_path: destination,
        });
        onClick?.(event);
      }}
    />
  );
}
