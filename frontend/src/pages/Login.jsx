import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Eye, EyeOff, Loader2, User, Lock } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { apiError } from "@/services/api";
import { toast } from "sonner";
import BG from "@/assets/hospital.jpeg";
import Logo from "@/assets/logo.png";


export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username.trim(), password);
      toast.success("Bienvenido al sistema");
      navigate("/");
    } catch (err) {
      toast.error(apiError(err?.response?.data?.detail) || "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  const forgot = () => toast.info("Contacte al administrador de Informática para restablecer su contraseña.");

  return (
    <div className="min-h-screen flex">
      <div className="relative hidden lg:flex flex-1 items-end p-12 overflow-hidden">
        <img src={BG} alt="Hospital Militar" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-[#062a52]/80" />
        <div className="relative z-10 text-white max-w-lg">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/15 backdrop-blur grid place-items-center border border-white/20">
              <Shield className="w-6 h-6" />
            </div>
            <span className="font-heading text-xl font-bold">Hospital Militar</span>
          </div>
          <h1 className="font-heading text-4xl font-extrabold leading-tight mb-4">
            Sistema de Gestión de Direcciones IP
          </h1>
          <p className="text-white/80 text-lg">
            Administración centralizada de direcciones IP institucionales. Control de segmentos,
            equipos, asignaciones e historial en un solo lugar.
          </p>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 bg-background">
        <div className="w-full max-w-md animate-fade-in">
          <div className="rounded-[32px] bg-amber-50/95 border border-amber-200/80 shadow-2xl shadow-amber-900/10 p-8 md:p-10 text-center">
            <div className="mb-6 flex justify-center">
              <img src={Logo} alt="Logo Hospital Militar" className="h-28 w-auto rounded-3xl shadow-sm" />
            </div>

            <h2 className="font-heading text-3xl font-extrabold tracking-tight mb-2">Iniciar Sesión</h2>
            <p className="text-muted-foreground mb-8">Ingrese sus credenciales para acceder al sistema.</p>

            <form onSubmit={submit} className="space-y-5 text-left">
              <div>
                <Label htmlFor="username">Usuario</Label>
                <div className="relative mt-1.5">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input id="username" data-testid="login-username" value={username}
                    onChange={(e) => setUsername(e.target.value)} placeholder="admin" className="pl-9" required />
                </div>
              </div>

              <div>
                <Label htmlFor="password">Contraseña</Label>
                <div className="relative mt-1.5">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input id="password" data-testid="login-password" type={show ? "text" : "password"}
                    value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" className="pl-9 pr-10" required />
                  <button type="button" onClick={() => setShow((s) => !s)} data-testid="toggle-password"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
                  <Checkbox checked={remember} onCheckedChange={setRemember} data-testid="remember-me" /> Recordarme
                </label>
                <button type="button" onClick={forgot} className="text-sm text-primary hover:underline" data-testid="forgot-password">
                  ¿Olvidó su contraseña?
                </button>
              </div>

              <Button type="submit" className="w-full" disabled={loading} data-testid="login-submit">
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                {loading ? "Ingresando…" : "Ingresar"}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
