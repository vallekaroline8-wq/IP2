import { useState } from "react";
import { Pencil, Trash2, Loader2, Zap, RotateCcw, ShieldCheck } from "lucide-react";
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
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authSeg, setAuthSeg] = useState(null);
  const [authDeps, setAuthDeps] = useState([]);

  const getSegmentoId = (s) => s.id_segmento ?? s.id;

  const isValidIPv4 = (ip) => {
    const ipv4Regex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4Regex.test(ip?.trim() || "");
  };

  const openNew = () => { setEditing(null); setForm({ nombre: "", direccion_red: "", mascara: "255.255.255.0", gateway: "" }); setErrors({}); setOpen(true); };
  const openEdit = (s) => { setEditing({ ...s, id_segmento: getSegmentoId(s) }); setForm({ nombre: s.nombre, direccion_red: s.direccion_red, mascara: s.mascara, gateway: s.gateway || "" }); setErrors({}); setOpen(true); };

  const validateForm = () => {
    const errs = {};
    if (!form.nombre.trim()) {
      errs.nombre = "El nombre del segmento es obligatorio";
    }
    if (!form.direccion_red.trim()) {
      errs.direccion_red = "La dirección de red es obligatoria";
    } else if (!isValidIPv4(form.direccion_red)) {
      errs.direccion_red = "Formato IPv4 inválido (ej. 172.16.0.0)";
    }
    if (!form.mascara.trim()) {
      errs.mascara = "La máscara de red es obligatoria";
    } else if (!isValidIPv4(form.mascara)) {
      errs.mascara = "Formato IPv4 inválido (ej. 255.255.255.0)";
    }
    if (form.gateway.trim() && !isValidIPv4(form.gateway)) {
      errs.gateway = "Formato IPv4 inválido (ej. 172.16.0.1)";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const save = async () => {
    if (!validateForm()) return;
    setSaving(true);
    try {
      if (editing) await api.put(`/segmentos/${getSegmentoId(editing)}`, form);
      else await api.post("/segmentos", form);
      ok(editing ? "Segmento actualizado" : "Segmento creado");
      setOpen(false); L.refetch();
    } catch (e) { fail(e); } finally { setSaving(false); }
  };

  const del = async (s) => {
    if (!(await confirmDelete(`Se eliminará el segmento "${s.nombre}" y sus IP`))) return;
    try { await api.delete(`/segmentos/${getSegmentoId(s)}`); ok("Segmento eliminado"); L.refetch(); } catch (e) { fail(e); }
  };

  const generar = async (s) => {
    if (!(await confirmAction("Generar IPs Disponibles", `Se generarán las 254 direcciones IP disponibles para el segmento "${s.nombre}"`, "Generar"))) return;
    try { const { data } = await api.post(`/segmentos/${getSegmentoId(s)}/generar-ips`); ok(data.mensaje || data.message || "IPs generadas correctamente"); L.refetch(); } catch (e) { fail(e); }
  };

  const limpiar = async (s) => {
    if (!(await confirmAction("Limpiar IPs del Segmento", `Se eliminarán las direcciones IP no asignadas del segmento "${s.nombre}"`, "Limpiar"))) return;
    try { const { data } = await api.delete(`/segmentos/${getSegmentoId(s)}/limpiar-ips`); ok(data.mensaje || "IPs del segmento limpiadas"); L.refetch(); } catch (e) { fail(e); }
  };

  const openAuth = async (s) => {
    const segmentoId = getSegmentoId(s);
    setAuthSeg({ ...s, id_segmento: segmentoId });
    // cargar autorizaciones por cada departamento (comprobamos cuáles incluyen este segmento)
    const marked = [];
    for (const d of deps) {
      const { data } = await api.get(`/departamento-segmento/${d.id}`);
      if (data.segmento_ids.includes(segmentoId)) marked.push(d.id);
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
                  <tr key={s.id_segmento} className="hover:bg-accent/40 transition-colors">
                    <Td className="font-medium">{s.nombre}</Td>
                    <Td className="font-mono-ip">{s.direccion_red}/24</Td>
                    <Td className="font-mono-ip text-muted-foreground">{s.gateway || "-"}</Td>
                    <Td>
                      {s.total_ips > 0 ? (
                        <span className="text-xs"><span className="text-red-600 font-medium">{s.ocupadas}</span> / <span className="text-emerald-600 font-medium">{s.disponibles}</span> disp. ({s.total_ips})</span>
                      ) : <span className="text-xs text-amber-600 font-medium">Sin IP generadas</span>}
                    </Td>
                    <Td className="text-right whitespace-nowrap">
                      {can("administrador", "tecnico") && (
                        <Button variant="ghost" size="icon" onClick={() => generar(s)} title="Generar IPs Disponibles" data-testid={`gen-${s.id_segmento}`}><Zap className="w-4 h-4 text-amber-600" /></Button>
                      )}
                      {can("administrador", "tecnico") && s.total_ips > 0 && (
                        <Button variant="ghost" size="icon" onClick={() => limpiar(s)} title="Limpiar IPs del Segmento" data-testid={`clean-${s.id_segmento}`}><RotateCcw className="w-4 h-4 text-orange-600" /></Button>
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

      <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) setErrors({}); }}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editing ? "Editar" : "Nuevo"} Segmento</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Nombre</Label>
              <Input
                className={`mt-1.5 ${errors.nombre ? "border-destructive focus-visible:ring-destructive" : ""}`}
                value={form.nombre}
                onChange={(e) => {
                  setForm({ ...form, nombre: e.target.value });
                  if (errors.nombre) setErrors((prev) => ({ ...prev, nombre: "" }));
                }}
                data-testid="form-nombre"
              />
              {errors.nombre && <p className="text-xs text-destructive mt-1">{errors.nombre}</p>}
            </div>
            <div>
              <Label>Dirección de Red</Label>
              <Input
                className={`mt-1.5 font-mono-ip ${errors.direccion_red ? "border-destructive focus-visible:ring-destructive" : ""}`}
                placeholder="172.16.0.0"
                value={form.direccion_red}
                onChange={(e) => {
                  setForm({ ...form, direccion_red: e.target.value });
                  if (errors.direccion_red) setErrors((prev) => ({ ...prev, direccion_red: "" }));
                }}
                data-testid="form-red"
              />
              {errors.direccion_red && <p className="text-xs text-destructive mt-1">{errors.direccion_red}</p>}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Máscara</Label>
                <Input
                  className={`mt-1.5 font-mono-ip ${errors.mascara ? "border-destructive focus-visible:ring-destructive" : ""}`}
                  placeholder="255.255.255.0"
                  value={form.mascara}
                  onChange={(e) => {
                    setForm({ ...form, mascara: e.target.value });
                    if (errors.mascara) setErrors((prev) => ({ ...prev, mascara: "" }));
                  }}
                />
                {errors.mascara && <p className="text-xs text-destructive mt-1">{errors.mascara}</p>}
              </div>
              <div>
                <Label>Gateway</Label>
                <Input
                  className={`mt-1.5 font-mono-ip ${errors.gateway ? "border-destructive focus-visible:ring-destructive" : ""}`}
                  placeholder="172.16.0.1"
                  value={form.gateway}
                  onChange={(e) => {
                    setForm({ ...form, gateway: e.target.value });
                    if (errors.gateway) setErrors((prev) => ({ ...prev, gateway: "" }));
                  }}
                />
                {errors.gateway && <p className="text-xs text-destructive mt-1">{errors.gateway}</p>}
              </div>
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
