"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { ListenButton } from "@/components/listen-button";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getArticle, type Article } from "@/lib/api";
import {
  ArrowLeft,
  ExternalLink,
  AlertCircle,
  Twitter,
  Linkedin,
  Facebook,
  Link2,
} from "lucide-react";

function ArticleDetailSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-4 w-16" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-3/4" />
      <div className="flex gap-2">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-5 w-32" />
      </div>
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

export default function ArticleDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function fetchArticle() {
      setLoading(true);
      setError(null);
      try {
        const data = await getArticle(id);
        setArticle(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load article"
        );
      } finally {
        setLoading(false);
      }
    }
    fetchArticle();
  }, [id]);

  function shareToTwitter() {
    if (!article) return;
    const text = encodeURIComponent(article.title);
    const url = encodeURIComponent(window.location.href);
    window.open(
      `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function shareToLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    window.open(
      `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function shareToFacebook() {
    const url = encodeURIComponent(window.location.href);
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${url}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  async function copyLink() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container mx-auto max-w-3xl px-4 py-8">
        <Link
          href="/"
          className="mb-6 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to feed
        </Link>

        {loading && <ArticleDetailSkeleton />}

        {!loading && error && (
          <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <div>
              <h2 className="text-lg font-semibold">Failed to load article</h2>
              <p className="mt-1 text-sm text-muted-foreground">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && article && (
          <article className="space-y-6">
            <div className="space-y-3">
              {article.source && (
                <Badge variant="secondary">{article.source}</Badge>
              )}
              <h1 className="text-2xl font-bold leading-tight sm:text-3xl">
                {article.title}
              </h1>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                {article.author && <span>By {article.author}</span>}
                {article.published_at && (
                  <span>
                    {new Date(article.published_at).toLocaleDateString(
                      "en-GB",
                      {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      }
                    )}
                  </span>
                )}
              </div>
            </div>

            {article.summary && (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="text-base leading-relaxed">{article.summary}</p>
              </div>
            )}

            <div className="flex flex-wrap gap-3">
              {article.url && (
                <Button asChild>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    Read full article
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              )}
              <ListenButton />
            </div>

            <div className="border-t pt-6">
              <p className="mb-3 text-sm font-medium">Share</p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={shareToTwitter}
                  className="flex items-center gap-2"
                >
                  <Twitter className="h-4 w-4" />
                  Twitter
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={shareToLinkedIn}
                  className="flex items-center gap-2"
                >
                  <Linkedin className="h-4 w-4" />
                  LinkedIn
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={shareToFacebook}
                  className="flex items-center gap-2"
                >
                  <Facebook className="h-4 w-4" />
                  Facebook
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyLink}
                  className="flex items-center gap-2"
                >
                  <Link2 className="h-4 w-4" />
                  {copied ? "Copied!" : "Copy link"}
                </Button>
              </div>
            </div>
          </article>
        )}
      </main>
      <Footer />
    </div>
  );
}
