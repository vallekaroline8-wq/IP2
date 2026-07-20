import { useState } from "react";
import {
  Pencil,
  Trash2,
  Loader2,
  Eye,
} from "lucide-react";

import api from "@/services/api";
import { useList } from "@/hooks/useList";

import { PageHeader } from "@/components/PageHeader";
import {
  Pagination,
  TableSkeleton,
} from "@/components/Pagination";

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
import { Switch } from "@/components/ui/switch";

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

  // Modal Crear / Editar
  const [open, setOpen] = useState(false);

  // Modal Ver
  const [viewOpen, setViewOpen] = useState(false);

  // Usuario seleccionado para ver
  const [viewUser, setViewUser] = useState(null);

  // Usuario en edición
  const [editing, setEditing] = useState(null);

  // Formulario
  const [form, setForm] = useState(empty);

  // Estado de guardado
  const [saving, setSaving] = useState(false);

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

  const openView = (u) => {
    setViewUser(u);
    setViewOpen(true);
  };

  const save = async () => {
    if (!form.nombre.trim() || !form.usuario.trim()) {
      return fail({
        response: {
          data: {
            detail: "Complete todos los campos.",
          },
        },
      });
    }

    if (!editing && !form.contrasena.trim()) {
      return fail({
        response: {
          data: {
            detail: "Ingrese la contraseña.",
          },
        },
      });
    }

    if (
      form.contrasena &&
      form.contrasena !== form.confirmarContrasena
    ) {
      return fail({
        response: {
          data: {
            detail: "Las contraseñas no coinciden.",
          },
        },
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

        if (form.contrasena.trim()) {
          await api.put(
            `/usuarios/${editing.id_usuario}/password`,
            {
              contrasena: form.contrasena,
            }
          );
        }

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

  const toggleEstado = async (u) => {
    try {
      await api.put(
        `/usuarios/${u.id_usuario}/estado`,
        {
          id_estado: u.id_estado === 1 ? 2 : 1,
        }
      );

      ok("Estado actualizado");
      L.refetch();
    } catch (e) {
      fail(e);
    }
  };

  const del = async (u) => {
    if (
      !(await confirmDelete(
        `Se desactivará el usuario "${u.usuario}".`
      ))
    ) {
      return;
    }

    try {
      await api.delete(`/usuarios/${u.id_usuario}`);
      ok("Usuario desactivado");
      L.refetch();
    } catch (e) {
      fail(e);
    }
  };

  return (
    <div className="space-y-4">
      {/* Encabezado */}
      <PageHeader
        title="Usuarios"
        description="Administración de cuentas y permisos de acceso."
      >
        <Button onClick={openNew}>
          Nuevo Usuario
        </Button>
      </PageHeader>

      {/* Barra de búsqueda u otras utilidades */}
      <Toolbar>
        <Input
          placeholder="Buscar por nombre o usuario..."
          value={L.params?.q || ""}
          onChange={(e) => L.setParams({ ...L.params, q: e.target.value })}
          className="max-w-xs"
        />
      </Toolbar>

      {/* Tabla de Datos */}
      <TableWrap>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr>
              <Th>Nombre</Th>
              <Th>Usuario</Th>
              <Th>Rol</Th>
              <Th>Estado</Th>
              <Th className="text-right">Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {L.loading ? (
              <TableSkeleton cols={5} rows={5} />
            ) : L.items?.length === 0 ? (
              <EmptyRow cols={5} />
            ) : (
              L.items?.map((u) => (
                <tr key={u.id_usuario} className="border-b last:border-0 hover:bg-muted/50">
                  <Td className="font-medium">{u.nombre}</Td>
                  <Td>{u.usuario}</Td>
                  <Td>{roleLabels[u.rol] || u.rol}</Td>
                  <Td>
                    <Switch
                      checked={u.id_estado === 1}
                      onCheckedChange={() => toggleEstado(u)}
                      disabled={u.usuario === "admin"}
                    />
                  </Td>
                  <Td className="text-right space-x-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Ver usuario"
                      onClick={() => openView(u)}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>

                    <Button
                      variant="ghost"
                      size="icon"
                      title="Editar usuario"
                      onClick={() => openEdit(u)}
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>

                    {u.usuario !== "admin" && (
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Desactivar usuario"
                        onClick={() => del(u)}
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
      </TableWrap>

      {/* Paginación */}
      <Pagination L={L} />

      {/* Modal: Crear / Editar Usuario */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editing ? "Editar Usuario" : "Nuevo Usuario"}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="nombre">Nombre Completo</Label>
              <Input
                id="nombre"
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                placeholder="Juan Pérez"
              />
            </div>

            <div>
              <Label htmlFor="usuario">Nombre de Usuario</Label>
              <Input
                id="usuario"
                value={form.usuario}
                onChange={(e) => setForm({ ...form, usuario: e.target.value })}
                placeholder="jperez"
              />
            </div>

            <div>
              <Label htmlFor="rol">Rol</Label>
              <Select
                value={form.rol}
                onValueChange={(val) => setForm({ ...form, rol: val })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione un rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="TECNICO">Técnico</SelectItem>
                  <SelectItem value="ADMINISTRADOR">Administrador</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="contrasena">
                Contraseña {editing && "(Dejar en blanco para mantener actual)"}
              </Label>
              <Input
                id="contrasena"
                type="password"
                value={form.contrasena}
                onChange={(e) => setForm({ ...form, contrasena: e.target.value })}
                placeholder="••••••••"
              />
            </div>

            <div>
              <Label htmlFor="confirmarContrasena">Confirmar Contraseña</Label>
              <Input
                id="confirmarContrasena"
                type="password"
                value={form.confirmarContrasena}
                onChange={(e) => setForm({ ...form, confirmarContrasena: e.target.value })}
                placeholder="••••••••"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)} disabled={saving}>
              Cancelar
            </Button>
            <Button onClick={save} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                "Guardar"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal: Ver Información del Usuario */}
      <Dialog open={viewOpen} onOpenChange={setViewOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Información del Usuario</DialogTitle>
          </DialogHeader>

          {viewUser && (
            <div className="space-y-4 py-2">
              <div>
                <Label>Nombre</Label>
                <Input value={viewUser.nombre} readOnly disabled />
              </div>

              <div>
                <Label>Usuario</Label>
                <Input value={viewUser.usuario} readOnly disabled />
              </div>

              <div>
                <Label>Rol</Label>
                <Input value={roleLabels[viewUser.rol] || viewUser.rol} readOnly disabled />
              </div>

              <div>
                <Label>Estado</Label>
                <Input value={viewUser.estado || (viewUser.id_estado === 1 ? "Activo" : "Inactivo")} readOnly disabled />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setViewOpen(false)}>
              Cerrar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}