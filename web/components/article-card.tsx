import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ListenButton } from "@/components/listen-button";
import type { Article } from "@/lib/api";
import { ArrowRight } from "lucide-react";

interface ArticleCardProps {
  article: Article;
  rank: number;
}

export function ArticleCard({ article, rank }: ArticleCardProps) {
  return (
    <div className="flex flex-col rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-xs font-bold text-primary bg-primary/10 rounded px-2 py-0.5">
          #{rank}
        </span>
        {article.source && (
          <Badge variant="secondary" className="text-xs shrink-0">
            {article.source}
          </Badge>
        )}
      </div>
      <h2 className="font-semibold leading-snug mb-1 line-clamp-3">
        {article.title}
      </h2>
      {article.summary && (
        <p className="text-sm text-muted-foreground line-clamp-4 mb-4 flex-1">
          {article.summary}
        </p>
      )}
      <div className="flex items-center gap-2 mt-auto pt-2">
        <Button asChild size="sm" variant="default">
          <Link
            href={`/article/${article.id}`}
            className="flex items-center gap-1"
          >
            Read
            <ArrowRight className="h-3 w-3" />
          </Link>
        </Button>
        <ListenButton />
      </div>
    </div>
  );
}
