import { useState } from "react";
import { Pencil, Trash2, Loader2, Zap, ShieldCheck } from "lucide-react";
import api from "@/services/api";
import { useList, useOptions } from "@/hooks/useList";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { Toolbar, TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { confirmDelete, confirmAction, ok, fail } from "@/utils/ui";

export default function Segmentos() {
  const { can } = useAuth();
  const L = useList("segmentos");
  const deps = useOptions("departamentos");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ nombre: "", direccion_red: "", mascara: "255.255.255.0", gateway: "" });
  const [saving, setSaving] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authSeg, setAuthSeg] = useState(null);
  const [authDeps, setAuthDeps] = useState([]);

  const openNew = () => { setEditing(null); setForm({ nombre: "", direccion_red: "", mascara: "255.255.255.0", gateway: "" }); setOpen(true); };
  const openEdit = (s) => { setEditing(s); setForm({ nombre: s.nombre, direccion_red: s.direccion_red, mascara: s.mascara, gateway: s.gateway || "" }); setOpen(true); };

  const save = async () => {
    if (!form.nombre.trim() || !form.direccion_red.trim()) return fail({ response: { data: { detail: "Nombre y dirección de red son obligatorios" } } });
    setSaving(true);
    try {
      if (editing) await api.put(`/segmentos/${editing.id}`, form);
      else await api.post("/segmentos", form);
      ok(editing ? "Segmento actualizado" : "Segmento creado");
      setOpen(false); L.refetch();
    } catch (e) { fail(e); } finally { setSaving(false); }
  };

  const del = async (s) => {
    if (!(await confirmDelete(`Se eliminará el segmento "${s.nombre}" y sus IP`))) return;
    try { await api.delete(`/segmentos/${s.id}`); ok("Segmento eliminado"); L.refetch(); } catch (e) { fail(e); }
  };

  const generar = async (s) => {
    if (!(await confirmAction("Generar 254 IP", `Se generarán las 254 direcciones IP del segmento "${s.nombre}"`, "Generar"))) return;
    try { const { data } = await api.post(`/segmentos/${s.id}/generar-ips`); ok(data.message); L.refetch(); } catch (e) { fail(e); }
  };

  const openAuth = async (s) => {
    setAuthSeg(s);
    // cargar autorizaciones por cada departamento (comprobamos cuáles incluyen este segmento)
    const marked = [];
    for (const d of deps) {
      const { data } = await api.get(`/departamento-segmento/${d.id}`);
      if (data.segmento_ids.includes(s.id)) marked.push(d.id);
    }
    setAuthDeps(marked);
    setAuthOpen(true);
  };

  const toggleDep = (id) => setAuthDeps((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);

  const saveAuth = async () => {
    try {
      // por cada departamento reconstruimos su lista de segmentos autorizados
      for (const d of deps) {
        const { data } = await api.get(`/departamento-segmento/${d.id}`);
        let segs = data.segmento_ids.filter((x) => x !== authSeg.id);
        if (authDeps.includes(d.id)) segs.push(authSeg.id);
        await api.post("/departamento-segmento", { departamento_id: d.id, segmento_ids: segs });
      }
      ok("Autorización de departamentos actualizada");
      setAuthOpen(false);
    } catch (e) { fail(e); }
  };

  return (
    <div>
      <PageHeader title="Segmentos de Red" subtitle="Subredes institucionales y generación de direcciones IP" />
      <TableWrap>
        <Toolbar search={L.search} setSearch={L.setSearch} onAdd={openNew} addLabel="Nuevo Segmento" canAdd={can("administrador", "tecnico")} />
        {L.loading ? <TableSkeleton cols={5} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Nombre</Th><Th>Dirección de Red</Th><Th>Gateway</Th><Th>Ocupación</Th><Th className="text-right">Acciones</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? <EmptyRow cols={5} /> : L.items.map((s) => (
                  <tr key={s.id} className="hover:bg-accent/40 transition-colors">
                    <Td className="font-medium">{s.nombre}</Td>
                    <Td className="font-mono-ip">{s.direccion_red}/24</Td>
                    <Td className="font-mono-ip text-muted-foreground">{s.gateway || "-"}</Td>
                    <Td>
                      {s.total_ips > 0 ? (
                        <span className="text-xs"><span className="text-red-600 font-medium">{s.ocupadas}</span> / <span className="text-emerald-600 font-medium">{s.disponibles}</span> disp. ({s.total_ips})</span>
                      ) : <span className="text-xs text-amber-600">Sin IP generadas</span>}
                    </Td>
                    <Td className="text-right whitespace-nowrap">
                      {can("administrador", "tecnico") && s.total_ips === 0 && (
                        <Button variant="ghost" size="icon" onClick={() => generar(s)} title="Generar 254 IP" data-testid={`gen-${s.id}`}><Zap className="w-4 h-4 text-amber-600" /></Button>
                      )}
                      {can("administrador") && (
                        <Button variant="ghost" size="icon" onClick={() => openAuth(s)} title="Departamentos autorizados" data-testid={`auth-${s.id}`}><ShieldCheck className="w-4 h-4 text-primary" /></Button>
                      )}
                      {can("administrador", "tecnico") && <Button variant="ghost" size="icon" onClick={() => openEdit(s)}><Pencil className="w-4 h-4" /></Button>}
                      {can("administrador") && <Button variant="ghost" size="icon" onClick={() => del(s)}><Trash2 className="w-4 h-4 text-destructive" /></Button>}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <Pagination page={L.page} pages={L.pages} total={L.total} onChange={L.setPage} />
      </TableWrap>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editing ? "Editar" : "Nuevo"} Segmento</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div><Label>Nombre</Label><Input className="mt-1.5" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} data-testid="form-nombre" /></div>
            <div><Label>Dirección de Red</Label><Input className="mt-1.5 font-mono-ip" placeholder="192.168.50.0" value={form.direccion_red} onChange={(e) => setForm({ ...form, direccion_red: e.target.value })} data-testid="form-red" /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Máscara</Label><Input className="mt-1.5 font-mono-ip" value={form.mascara} onChange={(e) => setForm({ ...form, mascara: e.target.value })} /></div>
              <div><Label>Gateway</Label><Input className="mt-1.5 font-mono-ip" placeholder="192.168.50.254" value={form.gateway} onChange={(e) => setForm({ ...form, gateway: e.target.value })} /></div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button onClick={save} disabled={saving} data-testid="save-btn">{saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={authOpen} onOpenChange={setAuthOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Departamentos Autorizados</DialogTitle>
            <DialogDescription>RN-01: seleccione qué departamentos pueden usar el segmento "{authSeg?.nombre}"</DialogDescription>
          </DialogHeader>
          <div className="space-y-2 py-2 max-h-72 overflow-y-auto">
            {deps.map((d) => (
              <label key={d.id} className="flex items-center gap-3 p-2 rounded-md hover:bg-accent cursor-pointer">
                <Checkbox checked={authDeps.includes(d.id)} onCheckedChange={() => toggleDep(d.id)} data-testid={`auth-dep-${d.id}`} />
                <span className="text-sm">{d.nombre}</span>
              </label>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAuthOpen(false)}>Cancelar</Button>
            <Button onClick={saveAuth} data-testid="save-auth-btn">Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
