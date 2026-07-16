import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/context/ThemeContext";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import Login from "@/pages/Login";
import DashboardLayout from "@/layouts/DashboardLayout";
import Dashboard from "@/pages/Dashboard";
import Departamentos from "@/pages/Departamentos";
import Secciones from "@/pages/Secciones";
import Segmentos from "@/pages/Segmentos";
import DireccionesIP from "@/pages/DireccionesIP";
import Equipos from "@/pages/Equipos";
import Asignaciones from "@/pages/Asignaciones";
import Usuarios from "@/pages/Usuarios";
import Bitacora from "@/pages/Bitacora";

const Protected = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="h-screen grid place-items-center bg-background text-muted-foreground">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

const RequireRole = ({ children, roles = [] }) => {
  const { user, loading, can } = useAuth();

  if (loading) return <div className="h-screen grid place-items-center bg-background text-muted-foreground">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!can(...roles)) return <Navigate to="/" replace />;

  return children;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Toaster richColors position="top-right" />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Protected><DashboardLayout /></Protected>}>
              <Route index element={<Dashboard />} />
              <Route
                path="departamentos"
                element={
                  <RequireRole roles={["administrador", "tecnico"]}>
                    <Departamentos />
                  </RequireRole>
                }
              />
              <Route
                path="secciones"
                element={
                  <RequireRole roles={["administrador", "tecnico"]}>
                    <Secciones />
                  </RequireRole>
                }
              />
              <Route path="segmentos" element={<Segmentos />} />
              <Route path="ips" element={<DireccionesIP />} />
              <Route path="equipos" element={<Equipos />} />
              <Route path="asignaciones" element={<Asignaciones />} />
              <Route path="usuarios" element={<Usuarios />} />
              <Route path="bitacora" element={<Bitacora />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;