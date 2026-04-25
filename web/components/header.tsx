import Link from "next/link";
import Image from "next/image";
import { ThemeToggle } from "@/components/theme-toggle";
import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="flex h-14 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Image
              src="/logo.svg"
              alt="Pulse AI"
              width={32}
              height={32}
              priority
            />
            <span className="font-bold text-lg">Pulse AI</span>
          </Link>
          <div className="flex items-center gap-1">
            <ThemeToggle />
            <Button variant="ghost" size="icon" asChild>
              <Link href="/settings" aria-label="Settings">
                <Settings className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
