import { useEffect, useState } from "react";
import {
  Network, Building2, Monitor, Router, CheckCircle2, XCircle, Phone, HardDrive,
} from "lucide-react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";
import api from "@/services/api";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { fail } from "@/utils/ui";

const cardDefs = [
  { key: "segmentos", label: "Segmentos", icon: Network, color: "text-blue-600 bg-blue-100 dark:bg-blue-500/15" },
  { key: "departamentos", label: "Departamentos", icon: Building2, color: "text-indigo-600 bg-indigo-100 dark:bg-indigo-500/15" },
  { key: "equipos", label: "Equipos", icon: Monitor, color: "text-cyan-600 bg-cyan-100 dark:bg-cyan-500/15" },
  { key: "ips", label: "Direcciones IP", icon: Router, color: "text-slate-600 bg-slate-100 dark:bg-slate-500/15" },
  { key: "disponibles", label: "IP Disponibles", icon: CheckCircle2, color: "text-emerald-600 bg-emerald-100 dark:bg-emerald-500/15" },
  { key: "ocupadas", label: "IP Ocupadas", icon: XCircle, color: "text-red-600 bg-red-100 dark:bg-red-500/15" },
  { key: "equipos", label: "Equipos Registrados", icon: HardDrive, color: "text-violet-600 bg-violet-100 dark:bg-violet-500/15", alt: true },
  { key: "telefonos", label: "Teléfonos IP", icon: Phone, color: "text-amber-600 bg-amber-100 dark:bg-amber-500/15" },
];

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/dashboard").then((r) => setData(r.data)).catch(fail);
  }, []);

  if (!data) return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 8 }).map((_, i) => <div key={i} className="h-28 rounded-lg bg-muted animate-pulse" />)}
    </div>
  );

  const { cards, pie, por_segmento, ultimas_asignaciones, actividad } = data;

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Resumen general del sistema de direcciones IP" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cardDefs.map((c, i) => (
          <div key={i} className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow animate-fade-in" data-testid={`stat-${c.label.toLowerCase().replace(/\s/g, "-")}`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">{c.label}</p>
                <p className="font-heading text-3xl font-extrabold mt-1 text-foreground">{cards[c.key]}</p>
              </div>
              <div className={`w-10 h-10 rounded-lg grid place-items-center ${c.color}`}>
                <c.icon className="w-5 h-5" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="font-heading font-bold mb-4">Distribución de IP</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pie} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {pie.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-lg p-5 lg:col-span-2">
          <h3 className="font-heading font-bold mb-4">Ocupación por Segmento</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={por_segmento}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="nombre" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} />
              <Tooltip cursor={{ fill: "hsl(var(--accent))" }} />
              <Legend />
              <Bar dataKey="ocupadas" name="Ocupadas" fill="#EF4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="disponibles" name="Disponibles" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="font-heading font-bold mb-4">Estadísticas por Segmento</h3>
          <div className="space-y-4">
            {por_segmento.map((s, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">{s.nombre}</span>
                  <span className="text-muted-foreground">{s.ocupadas}/{s.total} · {s.porcentaje}%</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${s.porcentaje}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-5">
          <h3 className="font-heading font-bold mb-4">Últimas Asignaciones</h3>
          <div className="space-y-3">
            {ultimas_asignaciones.length === 0 && <p className="text-sm text-muted-foreground">Sin asignaciones</p>}
            {ultimas_asignaciones.map((a, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-mono-ip font-medium">{a.ip_direccion}</span>
                  <span className="text-muted-foreground"> → {a.equipo_nombre}</span>
                </div>
                <StatusBadge status={a.activo ? "activa" : "liberada"} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg p-5">
        <h3 className="font-heading font-bold mb-4">Actividad Reciente</h3>
        <div className="space-y-2">
          {actividad.map((a, i) => (
            <div key={i} className="flex items-center gap-3 text-sm py-1.5 border-b border-border/50 last:border-0">
              <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
              <span className="font-medium">{a.usuario}</span>
              <span className="text-muted-foreground">{a.accion} · {a.modulo}</span>
              <span className="ml-auto text-xs text-muted-foreground">{a.fecha?.slice(0, 16).replace("T", " ")}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
