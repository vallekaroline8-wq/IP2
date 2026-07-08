import { useEffect, useState, useCallback } from "react";
import { Search } from "lucide-react";
import api from "@/services/api";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { Input } from "@/components/ui/input";
import { fail } from "@/utils/ui";

const accionColor = {
  "Inicio de sesión": "text-blue-600", "Alta": "text-emerald-600", "Baja": "text-red-600",
  "Modificación": "text-amber-600", "Asignación IP": "text-violet-600", "Liberación IP": "text-cyan-600",
};

export default function Bitacora() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);

  const fetch = useCallback(async () => {
    setLoading(true);
    try { const { data } = await api.get("/bitacora", { params: { search, page } }); setItems(data.items); setPages(data.pages); setTotal(data.total); }
    catch (e) { fail(e); } finally { setLoading(false); }
  }, [search, page]);
  useEffect(() => { const t = setTimeout(fetch, 250); return () => clearTimeout(t); }, [fetch]);
  useEffect(() => { setPage(1); }, [search]);

  return (
    <div>
      <PageHeader title="Bitácora de Auditoría" subtitle="Registro automático de acciones del sistema" exportResource="bitacora" />
      <TableWrap>
        <div className="p-4 border-b border-border">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar en bitácora…" className="pl-9" data-testid="search-input" />
          </div>
        </div>
        {loading ? <TableSkeleton cols={5} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Fecha / Hora</Th><Th>Usuario</Th><Th>Acción</Th><Th>Módulo</Th><Th>Detalle</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {items.length === 0 ? <EmptyRow cols={5} /> : items.map((b) => (
                  <tr key={b.id} className="hover:bg-accent/40 transition-colors">
                    <Td className="font-mono-ip text-xs text-muted-foreground whitespace-nowrap">{b.fecha?.slice(0, 19).replace("T", " ")}</Td>
                    <Td className="font-medium">{b.usuario}</Td>
                    <Td><span className={`font-medium ${accionColor[b.accion] || "text-foreground"}`}>{b.accion}</span></Td>
                    <Td className="text-muted-foreground">{b.modulo}</Td>
                    <Td className="text-muted-foreground">{b.detalle}</Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Pagination page={page} pages={pages} total={total} onChange={setPage} />
      </TableWrap>
    </div>
  );
}
