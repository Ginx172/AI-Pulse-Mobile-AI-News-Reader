"use client";

import { Button } from "@/components/ui/button";
import { Headphones } from "lucide-react";
import { useState } from "react";

export function ListenButton() {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative inline-block">
      <Button
        size="sm"
        variant="outline"
        disabled
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        className="flex items-center gap-1"
        aria-label="Listen (coming soon)"
      >
        <Headphones className="h-3 w-3" />
        Listen
      </Button>
      {showTooltip && (
        <div
          role="tooltip"
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 whitespace-nowrap rounded bg-foreground px-2 py-1 text-xs text-background z-50"
        >
          Audio narration coming soon
        </div>
      )}
    </div>
  );
}
