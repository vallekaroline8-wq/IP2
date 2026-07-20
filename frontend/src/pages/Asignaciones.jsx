import { useEffect, useState, useCallback } from "react";
import { Link2, Unlink, RefreshCw, Loader2, Plus } from "lucide-react";
import api from "@/services/api";
import { useOptions } from "@/hooks/useList";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { Command, CommandInput, CommandList, CommandEmpty, CommandItem } from "@/components/ui/command";
import { confirmAction, ok, fail } from "@/utils/ui";

export default function Asignaciones() {
  const { can } = useAuth();
  const equipos = useOptions("asignaciones/equipos");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [reasignar, setReasignar] = useState(false);
  const [form, setForm] = useState({ equipo_id: "", segmento_id: "", ip_id: "" });
  const [availIps, setAvailIps] = useState([]);
  const [equipoOpen, setEquipoOpen] = useState(false);
  const [equipoQuery, setEquipoQuery] = useState("");

  const filteredEquipos = equipos.filter((e) => e.nombre.toLowerCase().includes(equipoQuery.toLowerCase()));
  const selectedEquipoNombre = equipos.find((e) => e.id === form.equipo_id)?.nombre;

  const fetch = useCallback(async () => {
    setLoading(true);
    try { const { data } = await api.get("/asignaciones", { params: { page } }); setItems(data.items); setPages(data.pages); setTotal(data.total); }
    catch (e) { fail(e); } finally { setLoading(false); }
  }, [page]);
  useEffect(() => { fetch(); }, [fetch]);

  useEffect(() => {
    if (!form.segmento_id) { setAvailIps([]); return; }
    api.get("/ips", { params: { segmento_id: form.segmento_id, estado: "disponible", limit: 300 } })
      .then((r) => setAvailIps(r.data.items)).catch(() => setAvailIps([]));
  }, [form.segmento_id]);

  const openNew = (reasig = false) => { setReasignar(reasig); setForm({ equipo_id: "", segmento_id: "", ip_id: "" }); setOpen(true); };

  const save = async () => {
    if (!form.equipo_id || !form.ip_id) return fail({ response: { data: { detail: "Seleccione equipo e IP" } } });
    setSaving(true);
    try {
      const url = reasignar ? "/asignaciones/reasignar" : "/asignaciones";
      await api.post(url, { equipo_id: form.equipo_id, ip_id: form.ip_id });
      ok(reasignar ? "IP reasignada correctamente" : "IP asignada correctamente");
      setOpen(false); fetch();
    } catch (e) { fail(e); } finally { setSaving(false); }
  };

  const liberar = async (a) => {
    if (!(await confirmAction("Liberar IP", `Se liberará ${a.ip_direccion} del equipo ${a.equipo_nombre}`, "Liberar"))) return;
    try { await api.post(`/asignaciones/${a.id}/liberar`); ok("IP liberada"); fetch(); } catch (e) { fail(e); }
  };

  return (
    <div>
      <PageHeader title="Asignaciones de IP" subtitle="Asignar, liberar y reasignar direcciones IP" exportResource="asignaciones">
        {can("administrador", "tecnico") && (
          <>
            <Button size="sm" variant="outline" onClick={() => openNew(true)} data-testid="reassign-btn"><RefreshCw className="w-4 h-4 mr-1.5" />Reasignar</Button>
            <Button size="sm" onClick={() => openNew(false)} data-testid="assign-btn"><Plus className="w-4 h-4 mr-1.5" />Asignar IP</Button>
          </>
        )}
      </PageHeader>

      <TableWrap>
        {loading ? <TableSkeleton cols={5} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Dirección IP</Th><Th>Equipo</Th><Th>Fecha Asignación</Th><Th>Estado</Th><Th className="text-right">Acciones</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {items.length === 0 ? <EmptyRow cols={5} /> : items.map((a) => (
                  <tr key={a.id} className="hover:bg-accent/40 transition-colors" data-testid={`asig-row-${a.id}`}>
                    <Td className="font-mono-ip font-medium">{a.ip_direccion}</Td>
                    <Td>{a.equipo_nombre}</Td>
                    <Td className="text-muted-foreground">{a.fecha_asignacion?.slice(0, 16).replace("T", " ")}</Td>
                    <Td><StatusBadge status={a.activo ? "activa" : "liberada"} /></Td>
                    <Td className="text-right">
                      {can("administrador", "tecnico") && a.activo && (
                        <Button variant="ghost" size="sm" onClick={() => liberar(a)} className="text-destructive" data-testid={`liberar-${a.id}`}><Unlink className="w-4 h-4 mr-1" />Liberar</Button>
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

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Link2 className="w-5 h-5" />{reasignar ? "Reasignar IP" : "Asignar IP"}</DialogTitle>
            <DialogDescription>El sistema valida automáticamente las reglas de negocio (RN-01, RN-02, RN-05).</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Equipo</Label>
              <Popover open={equipoOpen} onOpenChange={(open) => {
                setEquipoOpen(open);
                if (!open) setEquipoQuery("");
              }}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="mt-1.5 w-full justify-between text-left"
                    data-testid="assign-equipo"
                  >
                    {selectedEquipoNombre || "Seleccione equipo"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full max-w-[24rem] p-0 overflow-hidden">
                  <Command className="rounded-md border border-border bg-popover">
                    <CommandInput
                      value={equipoQuery}
                      onValueChange={setEquipoQuery}
                      placeholder="Escriba para filtrar equipos..."
                      className="rounded-t-md"
                    />
                    <CommandList className="p-1">
                      {filteredEquipos.length === 0 ? (
                        <CommandEmpty>No hay equipos</CommandEmpty>
                      ) : (
                        filteredEquipos.map((e) => (
                          <CommandItem
                            key={e.id}
                            onSelect={() => {
                              setForm({ ...form, equipo_id: e.id });
                              setEquipoOpen(false);
                              setEquipoQuery("");
                            }}
                          >
                            {e.nombre}
                          </CommandItem>
                        ))
                      )}
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>
            <div>
              <Label>Segmento</Label>
              <Select value={form.segmento_id} onValueChange={(v) => setForm({ ...form, segmento_id: v, ip_id: "" })}>
                <SelectTrigger className="mt-1.5" data-testid="assign-segmento"><SelectValue placeholder="Seleccione segmento" /></SelectTrigger>
                <SelectContent>{segs.map((s) => <SelectItem key={s.id} value={s.id}>{s.nombre}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <Label>Dirección IP disponible</Label>
              <Select value={form.ip_id} onValueChange={(v) => setForm({ ...form, ip_id: v })} disabled={!form.segmento_id}>
                <SelectTrigger className="mt-1.5 font-mono-ip" data-testid="assign-ip"><SelectValue placeholder={form.segmento_id ? "Seleccione IP" : "Elija un segmento primero"} /></SelectTrigger>
                <SelectContent className="max-h-60">{availIps.map((ip) => <SelectItem key={ip.id} value={ip.id} className="font-mono-ip">{ip.direccion}</SelectItem>)}</SelectContent>
              </Select>
              {form.segmento_id && availIps.length === 0 && <p className="text-xs text-amber-600 mt-1">No hay IP disponibles en este segmento</p>}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button onClick={save} disabled={saving} data-testid="save-assign-btn">{saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}{reasignar ? "Reasignar" : "Asignar"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
