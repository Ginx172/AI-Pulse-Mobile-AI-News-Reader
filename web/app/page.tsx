"use client";

import { useEffect, useState, useCallback } from "react";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { ArticleCard } from "@/components/article-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getArticlesToday, type Article } from "@/lib/api";
import { RefreshCw, AlertCircle, Clock } from "lucide-react";

function FeedSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="rounded-lg border p-4 space-y-3">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-6 w-full" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-20 w-full" />
          <div className="flex gap-2">
            <Skeleton className="h-9 w-24" />
            <Skeleton className="h-9 w-20" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function FeedPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchArticles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getArticlesToday();
      setArticles(data);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load articles");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchArticles();
    const interval = setInterval(fetchArticles, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchArticles]);

  const today = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container mx-auto max-w-7xl px-4 py-8">
        <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold sm:text-3xl">
              Today&apos;s Top 25 AI Stories
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">{today}</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchArticles}
            disabled={loading}
            className="flex items-center gap-2 self-start sm:self-auto"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {lastRefresh && !loading && (
          <p className="mb-4 flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            Last updated: {lastRefresh.toLocaleTimeString()}
          </p>
        )}

        {loading && <FeedSkeleton />}

        {!loading && error && (
          <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <div>
              <h2 className="text-lg font-semibold">Failed to load articles</h2>
              <p className="mt-1 text-sm text-muted-foreground">{error}</p>
            </div>
            <Button onClick={fetchArticles}>Try again</Button>
          </div>
        )}

        {!loading && !error && articles.length === 0 && (
          <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
            <Clock className="h-12 w-12 text-muted-foreground" />
            <div>
              <h2 className="text-lg font-semibold">No stories yet today</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Pipeline runs at 08:00 — check back later
              </p>
            </div>
          </div>
        )}

        {!loading && !error && articles.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((article, index) => (
              <ArticleCard key={article.id} article={article} rank={index + 1} />
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
