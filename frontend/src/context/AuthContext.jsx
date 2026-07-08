import { createContext, useContext, useEffect, useState } from "react";
import api, { setToken } from "@/services/api";

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/auth/me").then((r) => setUser(r.data)).catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const { data } = await api.post("/auth/login", { username, password });
    setToken(data.token);
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    try { await api.post("/auth/logout"); } catch (e) {}
    setToken(null);
    setUser(null);
  };

  const can = (...roles) => user && roles.includes(user.role);

  return <AuthContext.Provider value={{ user, loading, login, logout, can }}>{children}</AuthContext.Provider>;
};
