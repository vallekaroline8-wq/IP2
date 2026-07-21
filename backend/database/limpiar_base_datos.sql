-- =========================================================
-- SCRIPT DE LIMPIEZA DE DATOS Y REINICIO DE CONTADORES AUTO_INCREMENT
-- SIGIP System
-- =========================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Vaciar registros y reiniciar contador de IDs (AUTO_INCREMENT) a 1
TRUNCATE TABLE tbl_asignacion_ip;
ALTER TABLE tbl_asignacion_ip AUTO_INCREMENT = 1;

TRUNCATE TABLE tbl_ip;
ALTER TABLE tbl_ip AUTO_INCREMENT = 1;

TRUNCATE TABLE tbl_equipo;
ALTER TABLE tbl_equipo AUTO_INCREMENT = 1;

TRUNCATE TABLE tbl_departamento_segmento;
ALTER TABLE tbl_departamento_segmento AUTO_INCREMENT = 1;

TRUNCATE TABLE tbl_segmento;
ALTER TABLE tbl_segmento AUTO_INCREMENT = 1;

TRUNCATE TABLE tbl_departamento;
ALTER TABLE tbl_departamento AUTO_INCREMENT = 1;

-- 2. Reactivar la verificación de llaves foráneas
SET FOREIGN_KEY_CHECKS = 1;
