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

import { confirmDelete, ok, fail } from "@/utils/ui";

const empty = {
  nombre_equipo: "",
  marca: "",
  modelo: "",
  id_tipo: "",
  id_departamento: "",
};

export default function Equipos() {
  const { can } = useAuth();

  const L = useList("equipos");

  const tipos = useOptions("tipo_dispositivo");
  const departamentos = useOptions("departamentos");

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);

  const openNew = () => {
    setEditing(null);
    setForm(empty);
    setOpen(true);
  };

  const openEdit = (equipo) => {
    setEditing(equipo);

    setForm({
      nombre_equipo: equipo.nombre_equipo || "",
      marca: equipo.marca || "",
      modelo: equipo.modelo || "",
      id_tipo: String(equipo.id_tipo),
      id_departamento: String(equipo.id_departamento),
    });

    setOpen(true);
  };

  const save = async () => {
    if (
      !form.nombre_equipo.trim() ||
      !form.id_tipo ||
      !form.id_departamento
    ) {
      return fail({
        response: {
          data: {
            detail:
              "Nombre, tipo y departamento son obligatorios.",
          },
        },
      });
    }

    setSaving(true);

    const payload = {
      nombre_equipo: form.nombre_equipo.trim(),
      marca: form.marca,
      modelo: form.modelo,
      id_tipo: Number(form.id_tipo),
      id_departamento: Number(form.id_departamento),
    };

    try {
      if (editing) {
        await api.put(
          `/equipos/${editing.id_equipo}`,
          payload
        );

        ok("Equipo actualizado correctamente.");
      } else {
        await api.post("/equipos", payload);

        ok("Equipo creado correctamente.");
      }

      setOpen(false);
      setForm(empty);
      setEditing(null);

      L.refetch();
    } catch (e) {
      fail(e);
    } finally {
      setSaving(false);
    }
  };

  const del = async (equipo) => {
    const confirmar = await confirmDelete(
      `Se eliminará el equipo "${equipo.nombre_equipo}".`
    );

    if (!confirmar) return;

    try {
      await api.delete(`/equipos/${equipo.id_equipo}`);

      ok("Equipo eliminado correctamente.");

      L.refetch();
    } catch (e) {
      fail(e);
    }
  };

  return (
        <div>
      <PageHeader
        title="Equipos"
        subtitle="Administración de equipos"
        exportResource="equipos"
      />

      <TableWrap>
        <Toolbar
          search={L.search}
          setSearch={L.setSearch}
          onAdd={openNew}
          addLabel="Nuevo Equipo"
          canAdd={can("administrador", "tecnico")}
        />

        {L.loading ? (
          <TableSkeleton cols={6} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40">
                <tr>
                  <Th>Nombre</Th>
                  <Th>Tipo</Th>
                  <Th>Marca</Th>
                  <Th>Modelo</Th>
                  <Th>Departamento</Th>
                  <Th>Estado</Th>
                  <Th className="text-right">Acciones</Th>
                </tr>
              </thead>

              <tbody className="divide-y divide-border">
                {L.items.length === 0 ? (
                  <EmptyRow cols={7} />
                ) : (
                  L.items.map((e) => (
                    <tr
                      key={e.id_equipo}
                      className="hover:bg-accent/40 transition-colors"
                    >
                      <Td className="font-medium">
                        {e.nombre_equipo}
                      </Td>

                      <Td className="text-muted-foreground">
                        {e.tipo}
                      </Td>

                      <Td className="text-muted-foreground">
                        {e.marca || "-"}
                      </Td>

                      <Td className="text-muted-foreground">
                        {e.modelo || "-"}
                      </Td>

                      <Td className="text-muted-foreground">
                        {e.departamento}
                      </Td>

                      <Td>{e.estado}</Td>

                      <Td className="text-right">
                        {can("administrador", "tecnico") && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => openEdit(e)}
                          >
                            <Pencil className="w-4 h-4" />
                          </Button>
                        )}

                        {can("administrador") && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => del(e)}
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

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg">

          <DialogHeader>
            <DialogTitle>
              {editing ? "Editar Equipo" : "Nuevo Equipo"}
            </DialogTitle>
          </DialogHeader>

          <div className="grid grid-cols-2 gap-3 py-2">

            <div className="col-span-2">
              <Label>Nombre</Label>

              <Input
                className="mt-1.5"
                value={form.nombre_equipo}
                onChange={(e) =>
                  setForm({
                    ...form,
                    nombre_equipo: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <Label>Marca</Label>

              <Input
                className="mt-1.5"
                value={form.marca}
                onChange={(e) =>
                  setForm({
                    ...form,
                    marca: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <Label>Modelo</Label>

              <Input
                className="mt-1.5"
                value={form.modelo}
                onChange={(e) =>
                  setForm({
                    ...form,
                    modelo: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <Label>Tipo</Label>

              <Select
                value={form.id_tipo}
                onValueChange={(v) =>
                  setForm({
                    ...form,
                    id_tipo: v,
                  })
                }
              >
                <SelectTrigger className="mt-1.5">
                  <SelectValue placeholder="Seleccione" />
                </SelectTrigger>

                <SelectContent>
                  {tipos.map((t) => (
                    <SelectItem
                      key={t.id_tipo}
                      value={String(t.id_tipo)}
                    >
                      {t.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Departamento</Label>

              <Select
                value={form.id_departamento}
                onValueChange={(v) =>
                  setForm({
                    ...form,
                    id_departamento: v,
                  })
                }
              >
                <SelectTrigger className="mt-1.5">
                  <SelectValue placeholder="Seleccione" />
                </SelectTrigger>

                <SelectContent>
                  {departamentos.map((d) => (
                    <SelectItem
                      key={d.id_departamento}
                      value={String(d.id_departamento)}
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

