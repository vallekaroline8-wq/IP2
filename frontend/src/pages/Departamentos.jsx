import { useState } from "react";
import { Pencil, Trash2, Loader2 } from "lucide-react";
import api from "@/services/api";
import { useList } from "@/hooks/useList";
import { useAuth } from "@/context/AuthContext";
import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import { Toolbar, TableWrap, Th, Td, EmptyRow } from "@/components/Toolbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { confirmDelete, ok, fail } from "@/utils/ui";

export default function Departamentos() {
  const { user, can } = useAuth();

  const L = useList("departamentos");

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const [form, setForm] = useState({
    nombre: "",
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const validateForm = () => {
    const errs = {};
    const nombre = form.nombre.trim();

    if (!nombre) {
      errs.nombre = "El nombre del departamento no puede estar vacío ni contener solo espacios.";
    } else if (nombre.length < 3) {
      errs.nombre = "El nombre del departamento debe tener al menos 3 caracteres.";
    } else if (nombre.length > 50) {
      errs.nombre = "El nombre del departamento no puede exceder las 50 letras.";
    } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s-]+$/.test(form.nombre)) {
      errs.nombre = "El nombre solo debe contener letras, espacios y guiones (-). No se permiten números ni caracteres especiales.";
    } else if (/^[-]|[-]$/.test(nombre)) {
      errs.nombre = "El nombre no puede comenzar ni terminar con un guión.";
    } else if (/--|\s\s/.test(form.nombre)) {
      errs.nombre = "No se permiten guiones o espacios consecutivos.";
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const openNew = () => {
    setEditing(null);
    setForm({
      nombre: "",
    });
    setErrors({});
    setOpen(true);
  };

  const openEdit = (d) => {
    setEditing(d);
    setForm({
      nombre: d.nombre,
    });
    setErrors({});
    setOpen(true);
  };

  const save = async () => {
    if (!validateForm()) return;

    setSaving(true);

    try {
      if (editing) {
        await api.put(
          `/departamentos/${editing.id_departamento}`,
          {
            nombre: form.nombre.trim(),
          }
        );

        ok("Departamento actualizado correctamente.");
      } else {
        await api.post("/departamentos", {
          nombre: form.nombre.trim(),
        });

        ok("Departamento creado correctamente.");
      }

      setOpen(false);
      L.refetch();
    } catch (e) {
      fail(e);
    } finally {
      setSaving(false);
    }
  };

  const del = async (d) => {
    if (
      !(await confirmDelete(
        `¿Desea eliminar el departamento "${d.nombre}"?`
      ))
    ) {
      return;
    }

    try {
      await api.delete(
        `/departamentos/${d.id_departamento}`
      );

      ok("Departamento eliminado correctamente.");

      L.refetch();
    } catch (e) {
      fail(e);
    }
  };

  // Solo para depuración
  console.log("========== DEPARTAMENTOS ==========");
  console.log("Usuario:", user);
  console.log("Rol:", user?.rol);
  console.log("Puede administrar:", can("ADMINISTRADOR"));
  console.log("===================================");

  return (
    <div>
      <PageHeader
        title="Departamentos"
        subtitle="Gestión de departamentos del Hospital Militar"
      />

      <TableWrap>
        <Toolbar
          search={L.search}
          setSearch={L.setSearch}
          onAdd={openNew}
          addLabel="Nuevo Departamento"
          canAdd={can("ADMINISTRADOR")}
        />

        {L.loading ? (
          <TableSkeleton cols={2} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40">
                <tr>
                  <Th>Nombre</Th>
                  <Th className="text-right">
                    Acciones
                  </Th>
                </tr>
              </thead>

              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? (
                  <EmptyRow cols={2} />
                ) : (
                  L.items.map((d) => (
                    <tr
                      key={d.id_departamento}
                      className="hover:bg-accent/40 transition-colors"
                    >
                      <Td className="font-medium">
                        {d.nombre}
                      </Td>

                      <Td className="text-right">
                        {can("ADMINISTRADOR") && (
                          <>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => openEdit(d)}
                            >
                              <Pencil className="w-4 h-4" />
                            </Button>

                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => del(d)}
                            >
                              <Trash2 className="w-4 h-4 text-destructive" />
                            </Button>
                          </>
                        )}
                      </Td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        <Pagination
          page={L.page}
          pages={L.pages}
          total={L.total}
          onChange={L.setPage}
        />
      </TableWrap>

      <Dialog
        open={open}
        onOpenChange={(v) => {
          setOpen(v);
          if (!v) setErrors({});
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing
                ? "Editar Departamento"
                : "Nuevo Departamento"}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div>
              <Label>Nombre</Label>

              <Input
                className={`mt-1.5 ${
                  errors.nombre ? "border-destructive focus-visible:ring-destructive" : ""
                }`}
                value={form.nombre}
                onChange={(e) => {
                  setForm({
                    ...form,
                    nombre: e.target.value,
                  });
                  if (errors.nombre) {
                    setErrors((prev) => ({ ...prev, nombre: "" }));
                  }
                }}
              />
              {errors.nombre && (
                <p className="text-xs text-destructive mt-1.5">{errors.nombre}</p>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancelar
            </Button>

            <Button
              onClick={save}
              disabled={saving}
            >
              {saving && (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              )}

              Guardar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}