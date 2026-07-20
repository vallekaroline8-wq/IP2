import { useState } from "react";
import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  Network,
  Router,
  Monitor,
  Link2,
  Users,
  ScrollText,
  Menu,
  Moon,
  Sun,
  LogOut,
} from "lucide-react";

import { useTheme } from "@/context/ThemeContext";
import { useAuth } from "@/context/AuthContext";

import { Button } from "@/components/ui/button";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const NAV = [
  {
    to: "/",
    label: "Dashboard",
    icon: LayoutDashboard,
    end: true,
  },
  {
    to: "/departamentos",
    label: "Departamentos",
    icon: Building2,
    roles: ["administrador", "tecnico"],
  },
  {
    to: "/segmentos",
    label: "Segmentos",
    icon: Network,
  },
  {
    to: "/ips",
    label: "Direcciones IP",
    icon: Router,
  },
  {
    to: "/equipos",
    label: "Equipos",
    icon: Monitor,
  },
  {
    to: "/asignaciones",
    label: "Asignaciones",
    icon: Link2,
  },
  {
    to: "/usuarios",
    label: "Usuarios",
    icon: Users,
    roles: ["administrador"],
  },
  {
    to: "/bitacora",
    label: "Bitácora",
    icon: ScrollText,
    roles: ["administrador", "tecnico"],
  },
];

const roleLabel = {
  administrador: "Administrador",
  tecnico: "Técnico",
  consulta: "Consulta",
};

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const { theme, toggle } = useTheme();
  const { user, logout, can } = useAuth();

  const location = useLocation();
  const navigate = useNavigate();

  const items = NAV.filter(
    (item) => !item.roles || can(...item.roles)
  );

  const current = NAV.find((item) =>
    item.end
      ? location.pathname === "/"
      : location.pathname.startsWith(item.to) && item.to !== "/"
  );

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const Sidebar = ({ mobile }) => (
    <aside
      className={`${
        mobile ? "flex" : "hidden lg:flex"
      } flex-col bg-card border-r border-border transition-[width] duration-300 ${
        collapsed && !mobile ? "w-[76px]" : "w-64"
      } h-full`}
    >
      <div className="flex items-center gap-2.5 h-16 px-4 border-b border-border">
        <div className="w-9 h-9 rounded-lg bg-primary overflow-hidden grid place-items-center">
          <img
            src="/favicon.png"
            alt="Logo Hospital Militar"
            className="w-full h-full object-contain p-1"
          />
        </div>

        {(!collapsed || mobile) && (
          <div>
            <p className="font-heading font-extrabold">SIGIP</p>
            <p className="text-[10px] text-muted-foreground uppercase">
              Hospital Militar
            </p>
          </div>
        )}
      </div>

      <nav className="flex-1 py-3 px-2 space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent"
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            {(!collapsed || mobile) && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );

  return (
    <div className="h-screen flex">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <header className="h-16 flex justify-between items-center border-b px-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCollapsed(!collapsed)}
            >
              <Menu className="w-5 h-5" />
            </Button>

            <span>{current?.label}</span>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggle}>
              {theme === "dark" ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-primary text-white grid place-items-center">
                    {user?.nombre?.charAt(0) || "U"}
                  </div>

                  <div className="hidden sm:block text-left">
                    <p>{user?.nombre}</p>
                    <p className="text-xs text-muted-foreground">
                      {roleLabel[user?.rol]}
                    </p>
                  </div>
                </button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  {user?.usuario}
                </DropdownMenuLabel>

                <DropdownMenuSeparator />

                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Cerrar sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}