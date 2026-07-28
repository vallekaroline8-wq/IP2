import { useEffect, useState } from "react";
import {
  Network,
  Building2,
  Monitor,
  Router,
  CheckCircle2,
  XCircle,
  Trash2,
} from "lucide-react";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

import api from "@/services/api";
import { PageHeader } from "@/components/PageHeader";
import { fail } from "@/utils/ui";

const COLORS = [
  "#22C55E",
  "#3B82F6",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
];

const cardDefs = [
  {
    key: "departamentos",
    label: "Departamentos",
    icon: Building2,
    color: "text-indigo-600 bg-indigo-100 dark:bg-indigo-500/15",
  },
  {
    key: "segmentos",
    label: "Segmentos",
    icon: Network,
    color: "text-blue-600 bg-blue-100 dark:bg-blue-500/15",
  },
  {
    key: "equipos",
    label: "Equipos",
    icon: Monitor,
    color: "text-cyan-600 bg-cyan-100 dark:bg-cyan-500/15",
  },
  {
    key: "ips",
    label: "Direcciones IP",
    icon: Router,
    color: "text-slate-600 bg-slate-100 dark:bg-slate-500/15",
  },
  {
    key: "usuarios_activos",
    label: "Usuarios Activos",
    icon: CheckCircle2,
    color: "text-emerald-600 bg-emerald-100 dark:bg-emerald-500/15",
  },
  {
    key: "usuarios_inactivos",
    label: "Usuarios Inactivos",
    icon: XCircle,
    color: "text-amber-600 bg-amber-100 dark:bg-amber-500/15",
  },
  {
    key: "usuarios_eliminados",
    label: "Usuarios Eliminados",
    icon: Trash2,
    color: "text-red-600 bg-red-100 dark:bg-red-500/15",
  },
];

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api
      .get("/dashboard")
      .then((r) => setData(r.data))
      .catch(fail);
  }, []);

  if (!data) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="h-28 rounded-lg bg-muted animate-pulse"
          />
        ))}
      </div>
    );
  }

  const { cards = {}, pie = [] } = data;

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Resumen general del sistema"
      />

      {/* TARJETAS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cardDefs.map((c) => {
          const Icon = c.icon;
          return (
            <div
              key={c.key}
              className="bg-card border rounded-xl p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">
                    {c.label}
                  </p>

                  <p className="text-4xl font-bold mt-3 tracking-tight">
                    {cards[c.key] ?? 0}
                  </p>
                </div>

                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-sm ${c.color}`}
                >
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* GRÁFICOS */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        {/* PIE CHART */}
        <div className="bg-card border rounded-xl p-6 shadow-sm">
          <h3 className="font-bold mb-4">Estado de Direcciones IP</h3>

          <ResponsiveContainer width="100%" height={420}>
            <PieChart>
              <Pie
                data={pie}
                dataKey="cantidad"
                nameKey="nombre"
                innerRadius={95}
                outerRadius={145}
                paddingAngle={1}
                stroke="none"
                isAnimationActive
                animationDuration={1200}
                animationEasing="ease-out"
              >
                {(pie ?? []).map((_, index) => (
                  <Cell
                    key={index}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>

              <Tooltip
                contentStyle={{
                  borderRadius: "12px",
                  border: "none",
                  boxShadow: "0 8px 20px rgba(0,0,0,.15)",
                }}
              />

              <Legend
                verticalAlign="bottom"
                iconType="circle"
                wrapperStyle={{
                  paddingTop: 20,
                  fontSize: 14,
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}