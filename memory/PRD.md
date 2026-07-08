# PRD — SIGIP (Sistema de Gestión de Direcciones IP) · Hospital Militar

## Problema original
Sistema web IPAM para administrar direcciones IP del Hospital Militar de forma centralizada:
evitar duplicidad, mantener historial de asignaciones, consultar disponibilidad por segmento,
estadísticas y auditoría. (Enunciado pedía Node/MySQL; el usuario aprobó construirlo sobre el
stack soportado: React + FastAPI + MongoDB, con la misma lógica de negocio.)

## Arquitectura
- Frontend: React (CRA) + Tailwind + shadcn/ui + Recharts + SweetAlert2 + sonner. Context (Auth, Theme), services (axios), hooks (useList), layouts, pages.
- Backend: FastAPI por capas (database.py, auth.py, exports.py, seed.py, server.py). Rutas con prefijo /api.
- BD: MongoDB (DB_NAME=gip). Colecciones: usuarios, departamentos, secciones, segmentos, departamento_segmento, tipo_dispositivo, equipos, ips, asignaciones, bitacora.
- Auth: JWT (cookie httpOnly + Bearer en localStorage), bcrypt, roles (administrador, tecnico, consulta).

## Personas
- Administrador: control total (incl. usuarios y autorización de segmentos).
- Técnico: CRUD operativo, asignaciones, sin gestión de usuarios.
- Consulta: solo lectura.

## Reglas de negocio implementadas
RN-01 (segmento autorizado por depto), RN-02 (IP a un solo equipo), RN-03 (sin IP duplicadas),
RN-04 (254 IPs por segmento), RN-05 (un equipo = una IP activa), RN-06 (IP pertenece a segmento),
RN-07 (teléfonos IP como dispositivos), RN-08 (IP disponibles automáticas), RN-09 (dashboard usadas/disponibles por segmento).

## Implementado (2026-07-08)
- Login empresarial (usuario/contraseña, mostrar/ocultar, recordarme, recuperar).
- Dashboard: 8 tarjetas, gráfico pastel, gráfico barras, % ocupación por segmento, últimas asignaciones, actividad reciente.
- CRUD: Departamentos, Secciones, Segmentos (con generar 254 IPs + autorizar deptos), Equipos (incl. teléfonos IP), Usuarios (roles, cambio de contraseña, estado).
- Direcciones IP: filtros (segmento/estado), búsqueda, cambio de estado, historial.
- Asignaciones: asignar / liberar / reasignar con validación automática de RN.
- Bitácora automática (login, alta, baja, modificación, asignación, liberación, exportación).
- Exportar PDF y Excel (ips, equipos, asignaciones, bitacora).
- Modo claro/oscuro, sidebar colapsable, navbar, breadcrumb, skeletons, toasts, SweetAlert2.
- Datos de ejemplo del Hospital Militar precargados.
- Testing: 41 pruebas backend (100%), frontend e2e (100%).

## Backlog (P1/P2)
- P1: Imprimir vista, más filtros avanzados combinados, gráficos históricos por fecha.
- P1: Recuperación de contraseña real por email (hoy es aviso informativo).
- P2: Rate-limit/lockout de login (5 intentos), CORS explícito + cookies secure para producción.
- P2: Paginación/orden vía aggregation en IPs y segmentos para gran escala.
- P2: Importación masiva desde Advanced IP Scanner (CSV).

## Próximas tareas
Según feedback del usuario. Sugerencia inmediata: recuperación de contraseña por email (Resend) e importación CSV.
