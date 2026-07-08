import { Search, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export const Toolbar = ({ search, setSearch, onAdd, addLabel = "Nuevo", canAdd = true, children }) => (
  <div className="flex flex-col sm:flex-row gap-3 p-4 border-b border-border">
    <div className="relative flex-1 max-w-sm">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
      <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar…" className="pl-9" data-testid="search-input" />
    </div>
    <div className="flex items-center gap-2 sm:ml-auto">
      {children}
      {canAdd && onAdd && (
        <Button size="sm" onClick={onAdd} data-testid="add-btn">
          <Plus className="w-4 h-4 mr-1.5" /> {addLabel}
        </Button>
      )}
    </div>
  </div>
);

export const TableWrap = ({ children }) => (
  <div className="bg-card border border-border rounded-lg overflow-hidden animate-fade-in">
    {children}
  </div>
);

export const Th = ({ children, className = "" }) => (
  <th className={`text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide ${className}`}>{children}</th>
);

export const Td = ({ children, className = "" }) => (
  <td className={`px-4 py-3 text-sm ${className}`}>{children}</td>
);

export const EmptyRow = ({ cols, text = "No hay registros" }) => (
  <tr><td colSpan={cols} className="px-4 py-12 text-center text-muted-foreground text-sm">{text}</td></tr>
);
