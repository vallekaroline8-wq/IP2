import { createContext, useContext, useEffect, useState } from "react";
import api, { setToken } from "@/services/api";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/auth/me")
      .then((r) => {
        console.log("Usuario actual:", r.data);
        setUser(r.data);
      })
      .catch((err) => {
        console.error("Error obteniendo usuario:", err);
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const login = async (username, password) => {
    const { data } = await api.post("/auth/login", {
      username,
      password,
    });

    console.log("Respuesta Login:", data);

    setToken(data.token);
    setUser(data.user);

    return data.user;
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (e) {}

    setToken(null);
    setUser(null);
  };

  const can = (...roles) => {
    if (!user) return false;

    return roles.includes(user.rol);
  };

  // ====== DEBUG ======
  console.log("========== AUTH ==========");
  console.log("Usuario:", user);
  console.log("Rol:", user?.rol);
  console.log("Puede administrador:", can("administrador"));
  console.log("Puede tecnico:", can("tecnico"));
  console.log("Puede consulta:", can("consulta"));
  console.log("==========================");

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        can,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
