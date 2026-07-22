import Swal from "sweetalert2";
import { toast } from "sonner";
import api, { apiError } from "@/services/api";

export const swalTheme = () =>
  document.documentElement.classList.contains("dark");

export async function confirmDelete(
  text = "Esta acción no se puede deshacer"
) {
  const dark = swalTheme();

  const res = await Swal.fire({
    title: "¿Está seguro?",
    text,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#EF4444",
    cancelButtonColor: "#64748B",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
    background: dark ? "#0F172A" : "#FFFFFF",
    color: dark ? "#F8FAFC" : "#0F172A",
  });

  return res.isConfirmed;
}

export async function confirmAction(
  title,
  text,
  confirmText = "Confirmar"
) {
  const dark = swalTheme();

  const res = await Swal.fire({
    title,
    text,
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: "#0A4B8F",
    cancelButtonColor: "#64748B",
    confirmButtonText: confirmText,
    cancelButtonText: "Cancelar",
    background: dark ? "#0F172A" : "#FFFFFF",
    color: dark ? "#F8FAFC" : "#0F172A",
  });

  return res.isConfirmed;
}

export function ok(msg) {
  toast.success(msg);
}

export function fail(e) {
  toast.error(
    apiError(e?.response?.data?.detail) ||
      e?.message ||
      "Ocurrió un error."
  );
}

export async function downloadReport(recurso, formato) {
  try {
    const response = await api.get(
      `/${recurso}/export/${formato}`,
      {
        responseType: "blob",
      }
    );

    const blob = new Blob([response.data]);

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    link.download =
      formato === "excel"
        ? `SIGIP_${recurso}.xlsx`
        : `SIGIP_${recurso}.pdf`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);

    ok(`Reporte ${formato.toUpperCase()} descargado correctamente.`);
  } catch (e) {
    fail(e);
  }
}
