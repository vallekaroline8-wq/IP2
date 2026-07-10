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
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { confirmDelete, ok, fail } from "@/utils/ui";

export default function Departamentos() {
  const { can } = useAuth();
  const L = useList("departamentos");

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    nombre: "",
    descripcion: "",
  });

  const [saving, setSaving] = useState(false);

  const openNew = () => {
    setEditing(null);
    setForm({
      nombre: "",
      descripcion: "",
    });
    setOpen(true);
  };

  const openEdit = (d) => {
    setEditing(d);
    setForm({
      nombre: d.nombre,
      descripcion: d.descripcion || "",
    });
    setOpen(true);
  };

  const save = async () => {
    if (!form.nombre.trim()) {
      return fail({
        response: {
          data: {
            detail: "El nombre es obligatorio",
          },
        },
      });
    }

    setSaving(true);

    try {
      if (editing) {
        await api.put(
          `/departamentos/${editing.id_departamento}`,
          form
        );
        ok("Departamento actualizado");
      } else {
        await api.post("/departamentos", {
          nombre: form.nombre,
        });
        ok("Departamento creado");
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
        `Se eliminará el departamento "${d.nombre}"`
      ))
    )
      return;

    try {
      await api.delete(
        `/departamentos/${d.id_departamento}`
      );
      ok("Departamento eliminado");
      L.refetch();
    } catch (e) {
      fail(e);
    }
  };

  return (
    <div>
      <PageHeader
        title="Departamentos"
        subtitle="Gestión de departamentos del hospital"
      />

      <TableWrap>
        <Toolbar
          search={L.search}
          setSearch={L.setSearch}
          onAdd={openNew}
          addLabel="Nuevo Departamento"
          canAdd={can("administrador", "tecnico")}
        />

        {L.loading ? (
          <TableSkeleton cols={3} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40">
                <tr>
                  <Th>Nombre</Th>
                  <Th>Descripción</Th>
                  <Th className="text-right">
                    Acciones
                  </Th>
                </tr>
              </thead>

              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? (
                  <EmptyRow cols={3} />
                ) : (
                  L.items.map((d) => (
                    <tr
                      key={d.id_departamento}
                      className="hover:bg-accent/40 transition-colors"
                      data-testid={`dep-row-${d.id_departamento}`}
                    >
                      <Td className="font-medium">
                        {d.nombre}
                      </Td>

                      <Td className="text-muted-foreground">
                        {d.descripcion || "-"}
                      </Td>

                      <Td className="text-right">
                        {can(
                          "administrador",
                          "tecnico"
                        ) && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() =>
                              openEdit(d)
                            }
                            data-testid={`edit-${d.id_departamento}`}
                          >
                            <Pencil className="w-4 h-4" />
                          </Button>
                        )}

                        {can("administrador") && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() =>
                              del(d)
                            }
                            data-testid={`del-${d.id_departamento}`}
                          >
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </Button>
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
        onOpenChange={setOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing
                ? "Editar"
                : "Nuevo"}{" "}
              Departamento
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div>
              <Label>Nombre</Label>

              <Input
                className="mt-1.5"
                value={form.nombre}
                onChange={(e) =>
                  setForm({
                    ...form,
                    nombre: e.target.value,
                  })
                }
                data-testid="form-nombre"
              />
            </div>

            <div>
              <Label>Descripción</Label>

              <Textarea
                className="mt-1.5"
                value={form.descripcion}
                onChange={(e) =>
                  setForm({
                    ...form,
                    descripcion:
                      e.target.value,
                  })
                }
                data-testid="form-descripcion"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() =>
                setOpen(false)
              }
            >
              Cancelar
            </Button>

            <Button
              onClick={save}
              disabled={saving}
              data-testid="save-btn"
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