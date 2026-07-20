import { useState } from "react";
import {
  Pencil,
  Trash2,
  Loader2,
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
  rol: "",
  id_estado: 1,
};

const validatePassword = (password) => {
  if (!password) {
    return "Ingrese una contraseña.";
  }

  if (password.length < 8) {
    return "La contraseña debe tener al menos 8 caracteres.";
  }

  if (!/[a-z]/.test(password)) {
    return "La contraseña debe incluir al menos una minúscula.";
  }

  if (!/[A-Z]/.test(password)) {
    return "La contraseña debe incluir al menos una mayúscula.";
  }

  if (!/[^A-Za-z0-9]/.test(password)) {
    return "La contraseña debe incluir al menos un carácter especial.";
  }

  return "";
};

export default function Usuarios() {
  const L = useList("usuarios");

  // Modal Crear / Editar
  const [open, setOpen] = useState(false);

  // Usuario en edición
  const [editing, setEditing] = useState(null);

  // Formulario
  const [form, setForm] = useState(empty);

  // Estado de guardado
  const [saving, setSaving] = useState(false);

  const getPasswordStrength = (password) => {
    if (!password) {
      return { score: 0, label: "Sin contraseña", color: "bg-muted" };
    }

    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    if (score <= 1) {
      return { score, label: "Débil", color: "bg-red-500" };
    }

    if (score === 2) {
      return { score, label: "Regular", color: "bg-yellow-500" };
    }

    if (score === 3) {
      return { score, label: "Buena", color: "bg-blue-500" };
    }

    return { score, label: "Fuerte", color: "bg-green-500" };
  };

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

  const passwordStrength = getPasswordStrength(form.contrasena);

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

    if (form.contrasena) {
      const passwordError = validatePassword(form.contrasena);
      if (passwordError) {
        return fail({
          response: {
            data: {
              detail: passwordError,
            },
          },
        });
      }
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

      {/* Barra de búsqueda reutilizable */}
      <Toolbar
        search={L.search}
        setSearch={L.setSearch}
      />

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
      <Pagination
        page={L.page}
        pages={L.pages}
        total={L.total}
        onChange={L.setPage}
      />

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
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                  <span>Seguridad de contraseña</span>
                  <span>{passwordStrength.label}</span>
                </div>
                <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    className={`h-full transition-all ${passwordStrength.color}`}
                    style={{ width: `${(passwordStrength.score / 4) * 100}%` }}
                  />
                </div>
              </div>
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

            <div>
              <Label htmlFor="rol">Rol</Label>
              <Select
                value={form.rol || undefined}
                onValueChange={(val) => setForm({ ...form, rol: val })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione un rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Seleccione un rol">Seleccione un rol...</SelectItem>
                  <SelectItem value="TECNICO">Técnico</SelectItem>
                  <SelectItem value="ADMINISTRADOR">Administrador</SelectItem>
                </SelectContent>
              </Select>
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

    </div>
  );
}