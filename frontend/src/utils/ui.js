import Swal from "sweetalert2";
import { toast } from "sonner";
import api, { apiError } from "@/services/api";

export const swalTheme = () => document.documentElement.classList.contains("dark");

export async function confirmDelete(text = "Esta acción no se puede deshacer") {
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

export async function confirmAction(title, text, confirmText = "Confirmar") {
  const dark = swalTheme();
  const res = await Swal.fire({
    title, text, icon: "question", showCancelButton: true,
    confirmButtonColor: "#0A4B8F", cancelButtonColor: "#64748B",
    confirmButtonText: confirmText, cancelButtonText: "Cancelar",
    background: dark ? "#0F172A" : "#FFFFFF", color: dark ? "#F8FAFC" : "#0F172A",
  });
  return res.isConfirmed;
}

export function ok(msg) { toast.success(msg); }
export function fail(e) { toast.error(apiError(e?.response?.data?.detail) || e?.message || "Error"); }

export async function downloadReport(recurso, formato) {
  try {
    const res = await api.get(`/export/${recurso}/${formato}`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = `SIGIP_${recurso}.${formato === "excel" ? "xlsx" : "pdf"}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    ok(`Reporte ${formato.toUpperCase()} descargado`);
  } catch (e) { fail(e); }
}
