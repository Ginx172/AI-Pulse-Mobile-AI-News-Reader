"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  getSources,
  toggleSource,
  addCustomSource,
  deleteCustomSource,
  type Source,
} from "@/lib/api";
import { useTheme } from "next-themes";
import { Plus, Trash2, ExternalLink, AlertCircle, Loader2 } from "lucide-react";

function SourceRow({
  source,
  onToggle,
  onDelete,
}: {
  source: Source;
  onToggle: (id: string, active: boolean) => Promise<void>;
  onDelete?: (id: string) => Promise<void>;
}) {
  const [toggling, setToggling] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function handleToggle() {
    setToggling(true);
    try {
      await onToggle(source.id, !source.active);
    } finally {
      setToggling(false);
    }
  }

  async function handleDelete() {
    if (!onDelete) return;
    setDeleting(true);
    try {
      await onDelete(source.id);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="flex items-center justify-between gap-3 py-3 border-b last:border-0">
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{source.name}</p>
        {source.url && (
          <p className="text-xs text-muted-foreground truncate">{source.url}</p>
        )}
        {source.type && (
          <Badge variant="outline" className="mt-1 text-xs">
            {source.type}
          </Badge>
        )}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Switch
          checked={source.active}
          onCheckedChange={handleToggle}
          disabled={toggling}
          aria-label={`Toggle ${source.name}`}
        />
        {onDelete && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDelete}
            disabled={deleting}
            className="text-destructive hover:text-destructive"
            aria-label={`Delete ${source.name}`}
          >
            {deleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

function AddSourceDialog({
  onAdd,
}: {
  onAdd: (name: string, url: string, type: string) => Promise<void>;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [type, setType] = useState("rss");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || !url.trim()) {
      setError("Name and URL are required");
      return;
    }
    setAdding(true);
    setError("");
    try {
      await onAdd(name.trim(), url.trim(), type);
      setOpen(false);
      setName("");
      setUrl("");
      setType("rss");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add source");
    } finally {
      setAdding(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add custom source
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add custom source</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="source-name">Name</Label>
            <Input
              id="source-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. My AI Blog"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="source-url">URL</Label>
            <Input
              id="source-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/feed.xml"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="source-type">Type</Label>
            <Select value={type} onValueChange={setType}>
              <SelectTrigger id="source-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="rss">RSS</SelectItem>
                <SelectItem value="atom">Atom</SelectItem>
                <SelectItem value="html">HTML</SelectItem>
                <SelectItem value="reddit">Reddit</SelectItem>
                <SelectItem value="youtube">YouTube</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {error && (
            <p className="text-sm text-destructive flex items-center gap-1">
              <AlertCircle className="h-4 w-4" />
              {error}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={adding}>
              {adding && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Add source
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function SettingsPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loadingSources, setLoadingSources] = useState(true);
  const [sourcesError, setSourcesError] = useState<string | null>(null);
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    async function fetchSources() {
      try {
        const data = await getSources();
        setSources(data);
      } catch (err) {
        setSourcesError(
          err instanceof Error ? err.message : "Failed to load sources"
        );
      } finally {
        setLoadingSources(false);
      }
    }
    fetchSources();
  }, []);

  async function handleToggle(id: string, active: boolean) {
    await toggleSource(id);
    setSources((prev) =>
      prev.map((s) => (s.id === id ? { ...s, active } : s))
    );
  }

  async function handleAdd(name: string, url: string, type: string) {
    const newSource = await addCustomSource(name, url, type);
    setSources((prev) => [...prev, newSource]);
  }

  async function handleDelete(id: string) {
    await deleteCustomSource(id);
    setSources((prev) => prev.filter((s) => s.id !== id));
  }

  const officialSources = sources.filter((s) => !s.is_custom);
  const customSources = sources.filter((s) => s.is_custom);

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container mx-auto max-w-2xl px-4 py-8">
        <h1 className="text-2xl font-bold mb-8">Settings</h1>

        {/* About */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">About Pulse AI</h2>
          <div className="rounded-lg border p-4 text-sm text-muted-foreground space-y-2">
            <p>
              Pulse AI is your AI news heartbeat — aggregating stories from
              100+ trusted AI sources, deduplicating, ranking and summarising
              them daily.
            </p>
            <p>
              Every day you get the top 25 most important AI stories, curated
              automatically. No noise, just signal.
            </p>
          </div>
        </section>

        {/* Pipeline */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Pipeline</h2>
          <div className="rounded-lg border p-4 text-sm text-muted-foreground space-y-2">
            <p>
              The daily pipeline runs at <strong>08:00</strong> (configurable
              via the <code>DAILY_RUN_HOUR</code> env var, default timezone
              Europe/Bucharest) and fetches
              articles from all active sources, deduplicates by URL, ranks by
              recency + source weight + keyword relevance, and summarises the
              top 25 with an LLM.
            </p>
            <p>
              Articles are cached until the next run. If you see an empty feed,
              check back after 08:00.
            </p>
          </div>
        </section>

        {/* Theme */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Theme</h2>
          <div className="rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="theme-select">Color theme</Label>
              <Select value={theme ?? "system"} onValueChange={setTheme}>
                <SelectTrigger id="theme-select" className="w-36">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </section>

        {/* Manage Sources */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Manage Sources</h2>
            <AddSourceDialog onAdd={handleAdd} />
          </div>

          {loadingSources && (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Loading sources...
            </div>
          )}

          {!loadingSources && sourcesError && (
            <div className="flex items-center gap-2 py-4 text-destructive text-sm">
              <AlertCircle className="h-4 w-4" />
              {sourcesError}
            </div>
          )}

          {!loadingSources && !sourcesError && (
            <div className="space-y-6">
              {customSources.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                    Custom sources ({customSources.length})
                  </h3>
                  <div className="rounded-lg border px-4">
                    {customSources.map((source) => (
                      <SourceRow
                        key={source.id}
                        source={source}
                        onToggle={handleToggle}
                        onDelete={handleDelete}
                      />
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-2 uppercase tracking-wide">
                  Official sources ({officialSources.length})
                </h3>
                <div className="rounded-lg border px-4 max-h-96 overflow-y-auto">
                  {officialSources.map((source) => (
                    <SourceRow
                      key={source.id}
                      source={source}
                      onToggle={handleToggle}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Connect */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Connect</h2>
          <div className="rounded-lg border p-4">
            <a
              href="https://www.facebook.com/profile.php?id=61566524544669&locale=en_GB"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm font-medium hover:underline text-primary"
            >
              More AI insights on Future Mind
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
