import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const api = axios.create({ baseURL: API, withCredentials: true });

const stored = localStorage.getItem("sigip-token");
if (stored) api.defaults.headers.common["Authorization"] = `Bearer ${stored}`;

export function setToken(token) {
  if (token) {
    localStorage.setItem("sigip-token", token);
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    localStorage.removeItem("sigip-token");
    delete api.defaults.headers.common["Authorization"];
  }
}

export function apiError(detail) {
  if (detail == null) return "Ocurrió un error. Intente nuevamente.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((e) => e?.msg || JSON.stringify(e)).join(" ");
  if (detail?.msg) return detail.msg;
  return String(detail);
}

export { API };
export default api;
