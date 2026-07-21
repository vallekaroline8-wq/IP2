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

  const {
    cards,
    pie,
    ultimas_asignaciones,
    actividad,
  } = data;

  return (
    <div>

      <PageHeader
        title="Dashboard"
        subtitle="Resumen general del sistema"
      />

      {/* TARJETAS */}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">

        {cardDefs.map((c) => (

          <div
            key={c.key}
            className="bg-card border rounded-lg p-4 hover:shadow-md transition-shadow"
          >

            <div className="flex justify-between items-start">

              <div>

                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  {c.label}
                </p>

                <p className="text-3xl font-bold mt-2">
                  {cards[c.key] ?? 0}
                </p>

              </div>

              <div
                className={`w-10 h-10 rounded-lg grid place-items-center ${c.color}`}
              >
                <c.icon className="w-5 h-5" />
              </div>

            </div>

          </div>

        ))}

      </div>

      {/* GRAFICOS */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

        {/* PIE */}

        <div className="bg-card border rounded-lg p-5">

          <h3 className="font-bold mb-4">
            Estado de Direcciones IP
          </h3>

          <ResponsiveContainer width="100%" height={280}>

            <PieChart>

              <Pie
                data={pie}
                dataKey="cantidad"
                nameKey="nombre"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={2}
              >

                {pie.map((_, index) => (

                  <Cell
                    key={index}
                    fill={COLORS[index % COLORS.length]}
                  />

                ))}

              </Pie>

              <Tooltip />

              <Legend />

            </PieChart>

          </ResponsiveContainer>

        </div>

        {/* BARRAS (eliminado: Secciones) */}

      </div>

      {/* RESUMEN */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Lista de Secciones eliminada */}

        <div className="bg-card border rounded-lg p-5">

          <h3 className="font-bold mb-4">
            Últimas Asignaciones
          </h3>

          {ultimas_asignaciones.length === 0 ? (

            <p className="text-muted-foreground">
              No existen asignaciones registradas.
            </p>

          ) : (

            ultimas_asignaciones.map((a, i) => (

              <div key={i}>
                {a.ip_direccion}
              </div>

            ))

          )}

        </div>

      </div>

      {/* ACTIVIDAD */}

      <div className="bg-card border rounded-lg p-5 mt-6">

        <h3 className="font-bold mb-4">
          Actividad Reciente
        </h3>

        {actividad.length === 0 ? (

          <p className="text-muted-foreground">
            Sin actividad registrada.
          </p>

        ) : (

          actividad.map((a, i) => (

            <div
              key={i}
              className="flex justify-between border-b py-2"
            >

              <span>{a.usuario}</span>

              <span>{a.accion}</span>

              <span>{a.modulo}</span>

            </div>

          ))

        )}

      </div>

    </div>
  );
}