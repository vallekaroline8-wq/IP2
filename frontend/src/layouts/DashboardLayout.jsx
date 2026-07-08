import { useState } from "react";
import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Building2, Layers, Network, Router, Monitor, Link2,
  Users, ScrollText, Menu, Moon, Sun, LogOut, ChevronRight, Shield,
} from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/departamentos", label: "Departamentos", icon: Building2 },
  { to: "/secciones", label: "Secciones", icon: Layers },
  { to: "/segmentos", label: "Segmentos", icon: Network },
  { to: "/ips", label: "Direcciones IP", icon: Router },
  { to: "/equipos", label: "Equipos", icon: Monitor },
  { to: "/asignaciones", label: "Asignaciones", icon: Link2 },
  { to: "/usuarios", label: "Usuarios", icon: Users, roles: ["administrador"] },
  { to: "/bitacora", label: "Bitácora", icon: ScrollText, roles: ["administrador", "tecnico"] },
];

const roleLabel = { administrador: "Administrador", tecnico: "Técnico", consulta: "Consulta" };

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { theme, toggle } = useTheme();
  const { user, logout, can } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const items = NAV.filter((n) => !n.roles || n.roles.includes(user?.role));
  const current = NAV.find((n) => (n.end ? location.pathname === "/" : location.pathname.startsWith(n.to) && n.to !== "/"));

  const handleLogout = async () => { await logout(); navigate("/login"); };

  const Sidebar = ({ mobile }) => (
    <aside
      className={`${mobile ? "flex" : "hidden lg:flex"} flex-col bg-card border-r border-border transition-[width] duration-300 ${collapsed && !mobile ? "w-[76px]" : "w-64"} h-full`}
      data-testid="sidebar"
    >
      <div className="flex items-center gap-2.5 h-16 px-4 border-b border-border">
        <div className="w-9 h-9 rounded-lg bg-primary grid place-items-center shrink-0">
          <Shield className="w-5 h-5 text-primary-foreground" />
        </div>
        {(!collapsed || mobile) && (
          <div className="overflow-hidden">
            <p className="font-heading font-extrabold text-foreground leading-tight">SIGIP</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Hospital Militar</p>
          </div>
        )}
      </div>
      <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={() => setMobileOpen(false)}
            data-testid={`nav-${item.label.toLowerCase().replace(/\s/g, "-")}`}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors border-l-2 ${
                isActive
                  ? "bg-primary/10 text-primary border-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground border-transparent"
              }`
            }
          >
            <item.icon className="w-[18px] h-[18px] shrink-0" />
            {(!collapsed || mobile) && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );

  return (
    <div className="h-screen flex bg-background overflow-hidden">
      <Sidebar />
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
          <div className="absolute left-0 top-0 h-full"><Sidebar mobile /></div>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 shrink-0 border-b border-border bg-card/80 backdrop-blur-xl flex items-center justify-between px-4 gap-4 sticky top-0 z-30">
          <div className="flex items-center gap-3 min-w-0">
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setMobileOpen(true)} data-testid="mobile-menu-btn">
              <Menu className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" className="hidden lg:flex" onClick={() => setCollapsed((c) => !c)} data-testid="collapse-btn">
              <Menu className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-1.5 text-sm min-w-0">
              <span className="text-muted-foreground">SIGIP</span>
              <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
              <span className="font-medium text-foreground truncate" data-testid="breadcrumb">{current?.label || "Dashboard"}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggle} data-testid="theme-toggle">
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 rounded-md pl-1 pr-2 py-1 hover:bg-accent transition-colors" data-testid="user-menu">
                  <div className="w-8 h-8 rounded-full bg-primary grid place-items-center text-primary-foreground text-sm font-semibold">
                    {user?.nombre?.charAt(0) || "U"}
                  </div>
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-medium leading-tight text-foreground">{user?.nombre}</p>
                    <p className="text-[11px] text-muted-foreground">{roleLabel[user?.role]}</p>
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>{user?.username}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} data-testid="logout-btn" className="text-destructive focus:text-destructive">
                  <LogOut className="w-4 h-4 mr-2" /> Cerrar sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
