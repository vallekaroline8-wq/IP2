import { useState } from "react";
import { Pencil, Trash2, Loader2 } from "lucide-react";

import api from "@/services/api";
import { useList, useOptions } from "@/hooks/useList";
import { useAuth } from "@/context/AuthContext";

import { PageHeader } from "@/components/PageHeader";
import { Pagination, TableSkeleton } from "@/components/Pagination";
import {
  Toolbar,
  TableWrap,
  Th,
  Td,
  EmptyRow,
} from "@/components/Toolbar";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

import {
  confirmDelete,
  ok,
  fail,
} from "@/utils/ui";

export default function Secciones() {
  const { can } = useAuth();

  const L = useList("secciones");
  const deps = useOptions("departamentos");

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const [form, setForm] = useState({
    nombre: "",
    id_departamento: "",
  });

  const [saving, setSaving] = useState(false);

  const openNew = () => {
    setEditing(null);

    setForm({
      nombre: "",
      id_departamento: "",
    });

    setOpen(true);
  };

  const openEdit = (s) => {
    setEditing(s);

    setForm({
      nombre: s.nombre,
      id_departamento: String(s.id_departamento),
    });

    setOpen(true);
  };

  const save = async () => {
    if (!form.nombre.trim() || !form.id_departamento) {
      return fail({
        response: {
          data: {
            detail: "Complete todos los campos.",
          },
        },
      });
    }

    setSaving(true);

    try {
      const datos = {
        nombre: form.nombre,
        id_departamento: Number(form.id_departamento),
      };

      if (editing) {
        await api.put(
          `/secciones/${editing.id_seccion}`,
          datos
        );

        ok("Sección actualizada correctamente.");
      } else {
        await api.post(
          "/secciones",
          datos
        );

        ok("Sección creada correctamente.");
      }

      setOpen(false);

      L.refetch();
    } catch (e) {
      fail(e);
    } finally {
      setSaving(false);
    }
  };

  const del = async (s) => {
    if (
      !(await confirmDelete(
        `Se eliminará la sección "${s.nombre}"`
      ))
    )
      return;

    try {
      await api.delete(
        `/secciones/${s.id_seccion}`
      );

      ok("Sección eliminada correctamente.");

      L.refetch();
    } catch (e) {
      fail(e);
    }
  };

  return (
    <div>
      <PageHeader
        title="Secciones"
        subtitle="Secciones asociadas a cada departamento"
      />

      <TableWrap>
        <Toolbar
          search={L.search}
          setSearch={L.setSearch}
          onAdd={openNew}
          addLabel="Nueva Sección"
          canAdd={can(
            "administrador",
            "tecnico"
          )}
        />

        {L.loading ? (
          <TableSkeleton cols={3} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40">
                <tr>
                  <Th>Nombre</Th>
                  <Th>Departamento</Th>
                  <Th className="text-right">
                    Acciones
                  </Th>
                </tr>
              </thead>

              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? (
                  <EmptyRow cols={3} />
                ) : (
                  L.items.map((s) => (
                    <tr
                      key={s.id_seccion}
                      className="hover:bg-accent/40 transition-colors"
                    >
                      <Td className="font-medium">
                        {s.nombre}
                      </Td>

                      <Td className="text-muted-foreground">
                        {s.departamento}
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
                              openEdit(s)
                            }
                          >
                            <Pencil className="w-4 h-4" />
                          </Button>
                        )}

                        {can("administrador") && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() =>
                              del(s)
                            }
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
                : "Nueva"}{" "}
              Sección
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
              />
            </div>

            <div>
              <Label>Departamento</Label>

              <Select
                value={form.id_departamento}
                onValueChange={(value) =>
                  setForm({
                    ...form,
                    id_departamento: value,
                  })
                }
              >
                <SelectTrigger className="mt-1.5">
                  <SelectValue placeholder="Seleccione un departamento" />
                </SelectTrigger>

                <SelectContent>
                  {deps.map((d) => (
                    <SelectItem
                      key={d.id_departamento}
                      value={String(
                        d.id_departamento
                      )}
                    >
                      {d.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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