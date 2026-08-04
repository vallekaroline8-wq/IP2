-- =========================================================
-- CONSULTA SQL CORREGIDA PARA INSERTAR 10 EQUIPOS
-- Esquema real:
-- tbl_tipo_dispositivo: (id_tipo, nombre)
-- tbl_equipo: (nombre_equipo, marca, modelo, id_tipo, id_departamento, id_estado)
-- =========================================================

-- 1. Insertar tipos de dispositivos en tbl_tipo_dispositivo (id_tipo, nombre)
INSERT IGNORE INTO tbl_tipo_dispositivo (id_tipo, nombre) VALUES
(1, 'Laptop'),
(2, 'PC de Escritorio'),
(3, 'Teléfono IP'),
(4, 'Cámara de Seguridad');

-- 2. Insertar 10 Equipos en tbl_equipo con las columnas reales de la base de datos
INSERT INTO tbl_equipo 
(nombre_equipo, marca, modelo, id_tipo, id_departamento, id_estado) 
VALUES
('Laptop Lenovo ThinkPad T14', 'Lenovo', 'ThinkPad T14', 1, 1, 1),
('PC HP ProDesk 400 G6', 'HP', 'ProDesk 400 G6', 2, 2, 1),
('Teléfono Cisco IP Phone 8841', 'Cisco', '8841', 3, 3, 1),
('Cámara Dahua IP Bullet 4MP', 'Dahua', 'IPC-HFW2431T', 4, 4, 1),
('Laptop Dell Latitude 5420', 'Dell', 'Latitude 5420', 1, 5, 1),
('PC Dell OptiPlex 7080', 'Dell', 'OptiPlex 7080', 2, 6, 1),
('Teléfono Grandstream GXP2170', 'Grandstream', 'GXP2170', 3, 7, 1),
('Cámara Hikvision IP Dome 5MP', 'Hikvision', 'DS-2CD2155FWD', 4, 8, 1),
('Laptop ASUS ExpertBook B1', 'ASUS', 'B1400', 1, 9, 1),
('PC Lenovo ThinkCentre M720', 'Lenovo', 'M720 Tiny', 2, 10, 1);
