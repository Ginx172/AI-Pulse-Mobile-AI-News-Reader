import { ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t py-6 mt-auto">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="flex flex-col items-center gap-2 text-center sm:flex-row sm:justify-between">
          <p className="text-sm text-muted-foreground">
            © 2026 Pulse AI — Your AI news heartbeat
          </p>
          <a
            href="https://www.facebook.com/profile.php?id=61566524544669&locale=en_GB"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            More AI insights on Future Mind
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>
    </footer>
  );
}
