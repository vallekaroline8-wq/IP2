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

const roleLabels = {
  ADMINISTRADOR: "Administrador",
  TECNICO: "Técnico",
  CONSULTA: "Consulta",
};

const empty = {
  nombre: "",
  usuario: "",
  contrasena: "",
  confirmarContrasena: "",
  rol: "TECNICO",
  id_estado: 1,
};

export default function Usuarios() {

  const L = useList("usuarios");

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);

  const [form, setForm] = useState(empty);

  const [saving, setSaving] = useState(false);

  const [pwOpen, setPwOpen] = useState(false);
  const [pwUser, setPwUser] = useState(null);
  const [pw, setPw] = useState("");

  const openNew = () => {

    setEditing(null);
    setForm(empty);
    setOpen(true);

  };

  const openEdit = (u) => {

    setEditing(u);

    setForm({
      nombre: u.nombre,
      usuario: u.usuario,
      contrasena: "",
      confirmarContrasena: "",
      rol: u.rol,
      id_estado: u.id_estado,
    });

    setOpen(true);

  };

  const save = async () => {

    if (!form.nombre.trim() || !form.usuario.trim()) {

      return fail({
        response: {
          data: {
            detail: "Complete todos los campos."
          }
        }
      });

    }

    if (!editing && !form.contrasena) {

      return fail({
        response: {
          data: {
            detail: "Ingrese la contraseña."
          }
        }
      });

    }

    if (
      form.contrasena &&
      form.contrasena !== form.confirmarContrasena
    ) {

      return fail({
        response: {
          data: {
            detail: "Las contraseñas no coinciden."
          }
        }
      });

    }

    setSaving(true);

    try {

      if (editing) {

        await api.put(
          `/usuarios/${editing.id_usuario}`,
          {
            nombre: form.nombre,
            usuario: form.usuario,
            rol: form.rol,
            id_estado: form.id_estado,
          }
        );

        ok("Usuario actualizado");

      } else {

        await api.post(
          "/usuarios",
          {
            nombre: form.nombre,
            usuario: form.usuario,
            contrasena: form.contrasena,
            rol: form.rol,
            id_estado: 1,
          }
        );

        ok("Usuario creado");

      }

      setOpen(false);
      L.refetch();

    } catch (e) {

      fail(e);

    } finally {

      setSaving(false);

    }

  };

  const del = async (u) => {

    if (
      !(await confirmDelete(
        `Se desactivará el usuario "${u.usuario}"`
      ))
    ) {
      return;
    }

    try {

      await api.delete(
        `/usuarios/${u.id_usuario}`
      );

      ok("Usuario desactivado");

      L.refetch();

    } catch (e) {

      fail(e);

    }

  };

  const savePw = async () => {

    if (!pw.trim()) {

      return fail({
        response: {
          data: {
            detail: "Ingrese la nueva contraseña."
          }
        }
      });

    }

    try {

      await api.put(
        `/usuarios/${pwUser.id_usuario}/password`,
        {
          contrasena: pw
        }
      );

      ok("Contraseña actualizada");

      setPw("");

      setPwOpen(false);

    } catch (e) {

      fail(e);

    }

  };
    return (
    <div>

      <PageHeader
        title="Usuarios"
        subtitle="Gestión de usuarios del sistema"
      />

      <TableWrap>

        <Toolbar
          search={L.search}
          setSearch={L.setSearch}
          onAdd={openNew}
          addLabel="Nuevo Usuario"
        />

        {
          L.loading ? (

            <TableSkeleton cols={5} />

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full">

                <thead className="bg-muted/40">

                  <tr>

                    <Th>Nombre</Th>

                    <Th>Usuario</Th>

                    <Th>Rol</Th>

                    <Th>Estado</Th>

                    <Th className="text-right">
                      Acciones
                    </Th>

                  </tr>

                </thead>

                <tbody className="divide-y divide-border">

                  {

                    L.items.length === 0 ? (

                      <EmptyRow cols={5} />

                    ) : (

                      L.items.map((u) => (

                        <tr
                          key={u.id_usuario}
                          className="hover:bg-accent/40 transition-colors"
                        >

                          <Td className="font-medium">
                            {u.nombre}
                          </Td>

                          <Td className="font-mono-ip">
                            {u.usuario}
                          </Td>

                          <Td>

                            <span className="px-2 py-1 rounded bg-primary/10 text-primary text-xs">

                              {roleLabels[u.rol]}

                            </span>

                          </Td>

                          <Td>

                            <StatusBadge
                              status={
                                u.id_estado === 1
                                  ? "activa"
                                  : "liberada"
                              }
                              label={u.estado}
                            />

                          </Td>

                          <Td className="text-right">

                            <Button
                              variant="ghost"
                              size="icon"
                              title="Cambiar contraseña"
                              onClick={() => {

                                setPwUser(u);
                                setPw("");
                                setPwOpen(true);

                              }}
                            >

                              <KeyRound className="w-4 h-4" />

                            </Button>

                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => openEdit(u)}
                            >

                              <Pencil className="w-4 h-4" />

                            </Button>

                            {

                              u.usuario !== "admin" && (

                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => del(u)}
                                >

                                  <Trash2 className="w-4 h-4 text-destructive" />

                                </Button>

                              )

                            }

                          </Td>

                        </tr>

                      ))

                    )

                  }

                </tbody>

              </table>

            </div>

          )

        }

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

              {

                editing
                  ? "Editar Usuario"
                  : "Nuevo Usuario"

              }

            </DialogTitle>

          </DialogHeader>

          <div className="space-y-4 py-2">

            <div>

              <Label>Nombre</Label>

              <Input
                className="mt-2"
                value={form.nombre}
                onChange={(e) =>
                  setForm({
                    ...form,
                    nombre: e.target.value
                  })
                }
              />

            </div>

            <div>

              <Label>Usuario</Label>

              <Input
                className="mt-2"
                value={form.usuario}
                disabled={!!editing}
                onChange={(e) =>
                  setForm({
                    ...form,
                    usuario: e.target.value
                  })
                }
              />

            </div>

            <div>

              <Label>

                Contraseña

                {

                  editing && (

                    <span className="text-xs text-muted-foreground">

                      {" "} (dejar vacía para no cambiar)

                    </span>

                  )

                }

              </Label>

              <Input
                type="password"
                className="mt-2"
                value={form.contrasena}
                onChange={(e) =>
                  setForm({
                    ...form,
                    contrasena: e.target.value
                  })
                }
              />

            </div>

            <div>

              <Label>

                Confirmar contraseña

              </Label>

              <Input
                type="password"
                className="mt-2"
                value={form.confirmarContrasena}
                onChange={(e) =>
                  setForm({
                    ...form,
                    confirmarContrasena: e.target.value
                  })
                }
              />

            </div>

            <div>

              <Label>Rol</Label>

              <Select
                value={form.rol}
                onValueChange={(v) =>
                  setForm({
                    ...form,
                    rol: v
                  })
                }
              >

                <SelectTrigger className="mt-2">

                  <SelectValue />

                </SelectTrigger>

                <SelectContent>

                  <SelectItem value="ADMINISTRADOR">
                    Administrador
                  </SelectItem>

                  <SelectItem value="TECNICO">
                    Técnico
                  </SelectItem>

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

              {
                saving && (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                )
              }

              Guardar

            </Button>

          </DialogFooter>

        </DialogContent>

      </Dialog>

      <Dialog
        open={pwOpen}
        onOpenChange={setPwOpen}
      >

        <DialogContent className="max-w-sm">

          <DialogHeader>

            <DialogTitle>

              Cambiar Contraseña

              {
                pwUser && (
                  <> · {pwUser.usuario}</>
                )
              }

            </DialogTitle>

          </DialogHeader>

          <div className="py-2">

            <Label>
              Nueva contraseña
            </Label>

            <Input
              type="password"
              className="mt-2"
              value={pw}
              onChange={(e) => setPw(e.target.value)}
            />

          </div>

          <DialogFooter>

            <Button
              variant="outline"
              onClick={() => setPwOpen(false)}
            >
              Cancelar
            </Button>

            <Button
              onClick={savePw}
            >
              Actualizar
            </Button>

          </DialogFooter>

        </DialogContent>

      </Dialog>

    </div>
  );

}