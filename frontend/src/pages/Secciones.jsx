import { useState } from "react";
import { Pencil, Trash2, Loader2 } from "lucide-react";
import api from "@/services/api";
import { useList, useOptions } from "@/hooks/useList";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { Toolbar, TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { confirmDelete, ok, fail } from "@/utils/ui";

export default function Secciones() {
  const { can } = useAuth();
  const L = useList("secciones");
  const deps = useOptions("departamentos");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ nombre: "", departamento_id: "" });
  const [saving, setSaving] = useState(false);
  const depName = (id) => deps.find((d) => d.id === id)?.nombre || "-";

  const openNew = () => { setEditing(null); setForm({ nombre: "", departamento_id: "" }); setOpen(true); };
  const openEdit = (s) => { setEditing(s); setForm({ nombre: s.nombre, departamento_id: s.departamento_id }); setOpen(true); };

  const save = async () => {
    if (!form.nombre.trim() || !form.departamento_id) return fail({ response: { data: { detail: "Complete todos los campos" } } });
    setSaving(true);
    try {
      if (editing) await api.put(`/secciones/${editing.id}`, form);
      else await api.post("/secciones", form);
      ok(editing ? "Sección actualizada" : "Sección creada");
      setOpen(false); L.refetch();
    } catch (e) { fail(e); } finally { setSaving(false); }
  };

  const del = async (s) => {
    if (!(await confirmDelete(`Se eliminará la sección "${s.nombre}"`))) return;
    try { await api.delete(`/secciones/${s.id}`); ok("Sección eliminada"); L.refetch(); } catch (e) { fail(e); }
  };

  return (
    <div>
      <PageHeader title="Secciones" subtitle="Secciones asociadas a cada departamento" />
      <TableWrap>
        <Toolbar search={L.search} setSearch={L.setSearch} onAdd={openNew} addLabel="Nueva Sección" canAdd={can("administrador", "tecnico")} />
        {L.loading ? <TableSkeleton cols={3} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Nombre</Th><Th>Departamento</Th><Th className="text-right">Acciones</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? <EmptyRow cols={3} /> : L.items.map((s) => (
                  <tr key={s.id} className="hover:bg-accent/40 transition-colors">
                    <Td className="font-medium">{s.nombre}</Td>
                    <Td className="text-muted-foreground">{depName(s.departamento_id)}</Td>
                    <Td className="text-right">
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
          <DialogHeader><DialogTitle>{editing ? "Editar" : "Nueva"} Sección</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div><Label>Nombre</Label><Input className="mt-1.5" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} data-testid="form-nombre" /></div>
            <div>
              <Label>Departamento</Label>
              <Select value={form.departamento_id} onValueChange={(v) => setForm({ ...form, departamento_id: v })}>
                <SelectTrigger className="mt-1.5" data-testid="form-departamento"><SelectValue placeholder="Seleccione" /></SelectTrigger>
                <SelectContent>{deps.map((d) => <SelectItem key={d.id} value={d.id}>{d.nombre}</SelectItem>)}</SelectContent>
              </Select>
            </div>
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
