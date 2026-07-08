import { useState } from "react";
import { Pencil, Trash2, Loader2, Phone } from "lucide-react";
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { confirmDelete, ok, fail } from "@/utils/ui";

const empty = { nombre: "", marca: "", modelo: "", tipo_id: "", departamento_id: "", seccion_id: "", es_telefono_ip: false };

export default function Equipos() {
  const { can } = useAuth();
  const L = useList("equipos");
  const tipos = useOptions("tipo_dispositivo");
  const deps = useOptions("departamentos");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);

  const openNew = () => { setEditing(null); setForm(empty); setOpen(true); };
  const openEdit = (e) => { setEditing(e); setForm({ ...empty, ...e }); setOpen(true); };

  const save = async () => {
    if (!form.nombre.trim() || !form.tipo_id || !form.departamento_id) return fail({ response: { data: { detail: "Nombre, tipo y departamento son obligatorios" } } });
    setSaving(true);
    const payload = { nombre: form.nombre, marca: form.marca, modelo: form.modelo, tipo_id: form.tipo_id, departamento_id: form.departamento_id, seccion_id: form.seccion_id || "", es_telefono_ip: form.es_telefono_ip };
    try {
      if (editing) await api.put(`/equipos/${editing.id}`, payload);
      else await api.post("/equipos", payload);
      ok(editing ? "Equipo actualizado" : "Equipo registrado");
      setOpen(false); L.refetch();
    } catch (e) { fail(e); } finally { setSaving(false); }
  };

  const del = async (e) => {
    if (!(await confirmDelete(`Se eliminará el equipo "${e.nombre}"`))) return;
    try { await api.delete(`/equipos/${e.id}`); ok("Equipo eliminado"); L.refetch(); } catch (err) { fail(err); }
  };

  return (
    <div>
      <PageHeader title="Equipos" subtitle="Dispositivos institucionales (incluye teléfonos IP)" exportResource="equipos" />
      <TableWrap>
        <Toolbar search={L.search} setSearch={L.setSearch} onAdd={openNew} addLabel="Nuevo Equipo" canAdd={can("administrador", "tecnico")} />
        {L.loading ? <TableSkeleton cols={5} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Nombre</Th><Th>Tipo</Th><Th>Marca / Modelo</Th><Th>Departamento</Th><Th>IP Activa</Th><Th className="text-right">Acciones</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? <EmptyRow cols={6} /> : L.items.map((e) => (
                  <tr key={e.id} className="hover:bg-accent/40 transition-colors">
                    <Td className="font-medium flex items-center gap-2">{e.es_telefono_ip && <Phone className="w-3.5 h-3.5 text-amber-600" />}{e.nombre}</Td>
                    <Td className="text-muted-foreground">{e.tipo_nombre}</Td>
                    <Td className="text-muted-foreground">{e.marca} {e.modelo}</Td>
                    <Td className="text-muted-foreground">{e.departamento_nombre}</Td>
                    <Td className="font-mono-ip">{e.ip_activa || <span className="text-muted-foreground font-sans">-</span>}</Td>
                    <Td className="text-right">
                      {can("administrador", "tecnico") && <Button variant="ghost" size="icon" onClick={() => openEdit(e)}><Pencil className="w-4 h-4" /></Button>}
                      {can("administrador") && <Button variant="ghost" size="icon" onClick={() => del(e)}><Trash2 className="w-4 h-4 text-destructive" /></Button>}
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
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>{editing ? "Editar" : "Nuevo"} Equipo</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-3 py-2">
            <div className="col-span-2"><Label>Nombre</Label><Input className="mt-1.5" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} data-testid="form-nombre" /></div>
            <div><Label>Marca</Label><Input className="mt-1.5" value={form.marca} onChange={(e) => setForm({ ...form, marca: e.target.value })} /></div>
            <div><Label>Modelo</Label><Input className="mt-1.5" value={form.modelo} onChange={(e) => setForm({ ...form, modelo: e.target.value })} /></div>
            <div>
              <Label>Tipo</Label>
              <Select value={form.tipo_id} onValueChange={(v) => setForm({ ...form, tipo_id: v, es_telefono_ip: tipos.find((t) => t.id === v)?.nombre === "Teléfono IP" })}>
                <SelectTrigger className="mt-1.5" data-testid="form-tipo"><SelectValue placeholder="Seleccione" /></SelectTrigger>
                <SelectContent>{tipos.map((t) => <SelectItem key={t.id} value={t.id}>{t.nombre}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <Label>Departamento</Label>
              <Select value={form.departamento_id} onValueChange={(v) => setForm({ ...form, departamento_id: v })}>
                <SelectTrigger className="mt-1.5" data-testid="form-departamento"><SelectValue placeholder="Seleccione" /></SelectTrigger>
                <SelectContent>{deps.map((d) => <SelectItem key={d.id} value={d.id}>{d.nombre}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <label className="col-span-2 flex items-center gap-2 text-sm cursor-pointer mt-1">
              <Checkbox checked={form.es_telefono_ip} onCheckedChange={(v) => setForm({ ...form, es_telefono_ip: !!v })} data-testid="form-telefono" /> Es teléfono IP
            </label>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button onClick={save} disabled={saving} data-testid="save-btn">{saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
