import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

export const Pagination = ({ page, pages, total, onChange }) => (
  <div className="flex items-center justify-between px-4 py-3 border-t border-border text-sm">
    <span className="text-muted-foreground" data-testid="pagination-info">
      {total} registro{total !== 1 ? "s" : ""} · Página {page} de {pages}
    </span>
    <div className="flex items-center gap-1.5">
      <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onChange(page - 1)} data-testid="page-prev">
        <ChevronLeft className="w-4 h-4" />
      </Button>
      <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => onChange(page + 1)} data-testid="page-next">
        <ChevronRight className="w-4 h-4" />
      </Button>
    </div>
  </div>
);

export const TableSkeleton = ({ cols = 4, rows = 5 }) => (
  <div className="p-4 space-y-3">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex gap-4">
        {Array.from({ length: cols }).map((_, j) => (
          <div key={j} className="h-5 flex-1 rounded bg-muted animate-pulse" />
        ))}
      </div>
    ))}
  </div>
);
