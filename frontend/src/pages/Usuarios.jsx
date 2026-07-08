import { useState } from "react";
import { Pencil, Trash2, Loader2, KeyRound } from "lucide-react";
import api from "@/services/api";
import { useList } from "@/hooks/useList";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { Toolbar, TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { confirmDelete, ok, fail } from "@/utils/ui";

const roleLabels = { administrador: "Administrador", tecnico: "Técnico", consulta: "Consulta" };
const empty = { nombre: "", username: "", password: "", role: "consulta", activo: true };

export default function Usuarios() {
  const L = useList("usuarios");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  const [pwOpen, setPwOpen] = useState(false);
  const [pwUser, setPwUser] = useState(null);
  const [pw, setPw] = useState("");

  const openNew = () => { setEditing(null); setForm(empty); setOpen(true); };
  const openEdit = (u) => { setEditing(u); setForm({ nombre: u.nombre, username: u.username, password: "", role: u.role, activo: u.activo }); setOpen(true); };

  const save = async () => {
    if (!form.nombre.trim() || !form.username.trim() || (!editing && !form.password)) return fail({ response: { data: { detail: "Complete nombre, usuario y contraseña" } } });
    setSaving(true);
    try {
      if (editing) await api.put(`/usuarios/${editing.id}`, form);
      else await api.post("/usuarios", form);
      ok(editing ? "Usuario actualizado" : "Usuario creado");
      setOpen(false); L.refetch();
    } catch (e) { fail(e); } finally { setSaving(false); }
  };

  const del = async (u) => {
    if (!(await confirmDelete(`Se desactivará el usuario "${u.username}"`))) return;
    try { await api.delete(`/usuarios/${u.id}`); ok("Usuario desactivado"); L.refetch(); } catch (e) { fail(e); }
  };

  const savePw = async () => {
    if (!pw) return fail({ response: { data: { detail: "Ingrese la nueva contraseña" } } });
    try { await api.put(`/usuarios/${pwUser.id}/password`, { password: pw }); ok("Contraseña actualizada"); setPwOpen(false); setPw(""); } catch (e) { fail(e); }
  };

  return (
    <div>
      <PageHeader title="Usuarios" subtitle="Gestión de usuarios y roles del sistema" />
      <TableWrap>
        <Toolbar search={L.search} setSearch={L.setSearch} onAdd={openNew} addLabel="Nuevo Usuario" />
        {L.loading ? <TableSkeleton cols={4} /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40"><tr><Th>Nombre</Th><Th>Usuario</Th><Th>Rol</Th><Th>Estado</Th><Th className="text-right">Acciones</Th></tr></thead>
              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? <EmptyRow cols={5} /> : L.items.map((u) => (
                  <tr key={u.id} className="hover:bg-accent/40 transition-colors">
                    <Td className="font-medium">{u.nombre}</Td>
                    <Td className="font-mono-ip">{u.username}</Td>
                    <Td><span className="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs font-medium">{roleLabels[u.role]}</span></Td>
                    <Td><StatusBadge status={u.activo ? "activa" : "liberada"} label={u.activo ? "Activo" : "Inactivo"} /></Td>
                    <Td className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => { setPwUser(u); setPw(""); setPwOpen(true); }} title="Cambiar contraseña"><KeyRound className="w-4 h-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => openEdit(u)}><Pencil className="w-4 h-4" /></Button>
                      {u.username !== "admin" && <Button variant="ghost" size="icon" onClick={() => del(u)}><Trash2 className="w-4 h-4 text-destructive" /></Button>}
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
          <DialogHeader><DialogTitle>{editing ? "Editar" : "Nuevo"} Usuario</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div><Label>Nombre completo</Label><Input className="mt-1.5" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} data-testid="form-nombre" /></div>
            <div><Label>Usuario</Label><Input className="mt-1.5" value={form.username} disabled={!!editing} onChange={(e) => setForm({ ...form, username: e.target.value })} data-testid="form-username" /></div>
            <div><Label>Contraseña {editing && <span className="text-muted-foreground text-xs">(dejar vacío para no cambiar)</span>}</Label><Input type="password" className="mt-1.5" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} data-testid="form-password" /></div>
            <div>
              <Label>Rol</Label>
              <Select value={form.role} onValueChange={(v) => setForm({ ...form, role: v })}>
                <SelectTrigger className="mt-1.5" data-testid="form-role"><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="administrador">Administrador</SelectItem><SelectItem value="tecnico">Técnico</SelectItem><SelectItem value="consulta">Consulta</SelectItem></SelectContent>
              </Select>
            </div>
            <label className="flex items-center justify-between"><span className="text-sm">Usuario activo</span><Switch checked={form.activo} onCheckedChange={(v) => setForm({ ...form, activo: v })} data-testid="form-activo" /></label>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button onClick={save} disabled={saving} data-testid="save-btn">{saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={pwOpen} onOpenChange={setPwOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader><DialogTitle>Cambiar Contraseña · {pwUser?.username}</DialogTitle></DialogHeader>
          <div className="py-2"><Label>Nueva contraseña</Label><Input type="password" className="mt-1.5" value={pw} onChange={(e) => setPw(e.target.value)} data-testid="new-password" /></div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPwOpen(false)}>Cancelar</Button>
            <Button onClick={savePw} data-testid="save-password-btn">Actualizar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
