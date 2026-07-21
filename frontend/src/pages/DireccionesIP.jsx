import { useEffect, useState, useCallback } from "react";
import { History, Loader2, RefreshCw } from "lucide-react";
import api from "@/services/api";
import { useOptions } from "@/hooks/useList";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { StatusBadge } from "@/components/StatusBadge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ok, fail } from "@/utils/ui";

export default function DireccionesIP() {
  const { can } = useAuth();
  const segs = useOptions("segmentos");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [segmento, setSegmento] = useState("all");
  const [estado, setEstado] = useState("all");
  const [histOpen, setHistOpen] = useState(false);
  const [hist, setHist] = useState([]);
  const [histIp, setHistIp] = useState("");

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, search };
      if (segmento !== "all") params.segmento_id = segmento;
      if (estado !== "all") params.estado = estado;
      const { data } = await api.get("/ips", { params });
      setItems(data.items); setPages(data.pages); setTotal(data.total);
    } catch (e) { fail(e); } finally { setLoading(false); }
  }, [page, search, segmento, estado]);

  useEffect(() => { const t = setTimeout(fetch, 250); return () => clearTimeout(t); }, [fetch]);
  useEffect(() => { setPage(1); }, [search, segmento, estado]);

  const changeState = async (ip, nuevo) => {
    try { await api.put(`/ips/${ip.id}/estado`, { estado: nuevo }); ok("Estado actualizado"); fetch(); } catch (e) { fail(e); }
  };

  const showHist = async (ip) => {
    setHistIp(ip.direccion);
    try { const { data } = await api.get(`/ips/${ip.id}/historial`); setHist(data.items); setHistOpen(true); } catch (e) { fail(e); }
  };

  return (
    <div>
      <PageHeader title="Direcciones IP" subtitle="Consulta y control de direcciones por segmento" exportResource="ips" />
      <TableWrap>
        <div className="flex flex-col sm:flex-row gap-3 p-4 border-b border-border">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar IP…" className="pl-9 font-mono-ip" data-testid="search-input" />
          </div>
          <Select value={segmento} onValueChange={setSegmento}>
            <SelectTrigger className="w-full sm:w-52" data-testid="filter-segmento"><SelectValue placeholder="Segmento" /></SelectTrigger>
            <SelectContent><SelectItem value="all">Todos los segmentos</SelectItem>{segs.map((s) => <SelectItem key={s.id_segmento} value={String(s.id_segmento)}>{s.nombre}</SelectItem>)}</SelectContent>
          </Select>
          <Select value={estado} onValueChange={setEstado}>
            <SelectTrigger className="w-full sm:w-44" data-testid="filter-estado"><SelectValue placeholder="Estado" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los estados</SelectItem>
              <SelectItem value="disponible">Disponible</SelectItem>
              <SelectItem value="ocupada">Ocupada</SelectItem>
              <SelectItem value="reservada">Reservada</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {loading ? <TableSkeleton cols={5} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Dirección IP</Th><Th>Segmento</Th><Th>Estado</Th><Th>Equipo</Th><Th className="text-right">Acciones</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {items.length === 0 ? <EmptyRow cols={5} /> : items.map((ip) => (
                  <tr key={ip.id} className="hover:bg-accent/40 transition-colors" data-testid={`ip-row-${ip.direccion}`}>
                    <Td className="font-mono-ip font-medium">{ip.direccion}</Td>
                    <Td className="text-muted-foreground">{ip.segmento_nombre}</Td>
                    <Td><StatusBadge status={ip.estado} /></Td>
                    <Td>{ip.equipo_nombre || <span className="text-muted-foreground">-</span>}</Td>
                    <Td className="text-right whitespace-nowrap">
                      <Button variant="ghost" size="icon" onClick={() => showHist(ip)} title="Historial" data-testid={`hist-${ip.direccion}`}><History className="w-4 h-4" /></Button>
                      {can("administrador", "tecnico") && ip.estado === "disponible" && (
                        <Button variant="ghost" size="sm" onClick={() => changeState(ip, "reservada")} className="text-amber-600" data-testid={`reserve-${ip.direccion}`}>Reservar</Button>
                      )}
                      {can("administrador", "tecnico") && ip.estado === "reservada" && (
                        <Button variant="ghost" size="sm" onClick={() => changeState(ip, "disponible")} className="text-emerald-600"><RefreshCw className="w-3.5 h-3.5 mr-1" />Liberar</Button>
                      )}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Pagination page={page} pages={pages} total={total} onChange={setPage} />
      </TableWrap>

      <Dialog open={histOpen} onOpenChange={setHistOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle className="font-mono-ip">Historial · {histIp}</DialogTitle></DialogHeader>
          <div className="space-y-2 py-2 max-h-80 overflow-y-auto">
            {hist.length === 0 ? <p className="text-sm text-muted-foreground py-4 text-center">Sin historial de asignaciones</p> : hist.map((h) => (
              <div key={h.id} className="p-3 rounded-md border border-border text-sm">
                <div className="flex justify-between"><span className="font-medium">{h.equipo_nombre}</span><StatusBadge status={h.activo ? "activa" : "liberada"} /></div>
                <p className="text-xs text-muted-foreground mt-1">Asignada: {h.fecha_asignacion?.slice(0, 16).replace("T", " ")}{h.fecha_liberacion ? ` · Liberada: ${h.fecha_liberacion.slice(0, 16).replace("T", " ")}` : ""}</p>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
