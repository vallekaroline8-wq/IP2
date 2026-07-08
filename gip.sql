-- ============================================================================
--  SIGIP - Sistema de Gestión de Direcciones IP  (Hospital Militar)
--  Script de Base de Datos MySQL  |  Motor: InnoDB  |  Charset: utf8mb4
-- ----------------------------------------------------------------------------
--  Este script crea la base de datos "gip", todas las tablas del modelo
--  entidad-relación con sus llaves primarias y foráneas, un procedimiento
--  almacenado para generar automáticamente las 254 IP de un segmento (RN-04),
--  triggers para reglas de negocio (RN-02, RN-05) y datos de ejemplo.
--
--  Uso:
--    mysql -u root -p < gip.sql
--  o desde MySQL Workbench: File > Open SQL Script > Ejecutar.
--
--  Nota de contraseñas: los hashes son bcrypt reales.
--    admin    -> admin123
--    tecnico  -> tecnico123
--    consulta -> consulta123
-- ============================================================================

DROP DATABASE IF EXISTS gip;
CREATE DATABASE gip
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE gip;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
--  TABLA: tbl_departamento
-- ============================================================================
CREATE TABLE tbl_departamento (
  id_departamento  INT AUTO_INCREMENT PRIMARY KEY,
  nombre           VARCHAR(100) NOT NULL,
  descripcion      VARCHAR(255) DEFAULT NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,   -- eliminación lógica
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_departamento_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_seccion   (una sección pertenece a un departamento)
-- ============================================================================
CREATE TABLE tbl_seccion (
  id_seccion       INT AUTO_INCREMENT PRIMARY KEY,
  nombre           VARCHAR(100) NOT NULL,
  id_departamento  INT NOT NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_seccion_departamento
    FOREIGN KEY (id_departamento) REFERENCES tbl_departamento (id_departamento)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_segmento  (subred /24) - RN-06: toda IP pertenece a un segmento
-- ============================================================================
CREATE TABLE tbl_segmento (
  id_segmento      INT AUTO_INCREMENT PRIMARY KEY,
  nombre           VARCHAR(100) NOT NULL,
  direccion_red    VARCHAR(15)  NOT NULL,           -- ej. 192.168.10.0
  mascara          VARCHAR(15)  NOT NULL DEFAULT '255.255.255.0',
  gateway          VARCHAR(15)  DEFAULT NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_segmento_red (direccion_red)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_departamento_segmento  (RN-01: segmentos autorizados por depto)
--  Relación N:M entre departamento y segmento.
-- ============================================================================
CREATE TABLE tbl_departamento_segmento (
  id_departamento_segmento INT AUTO_INCREMENT PRIMARY KEY,
  id_departamento  INT NOT NULL,
  id_segmento      INT NOT NULL,
  CONSTRAINT fk_ds_departamento
    FOREIGN KEY (id_departamento) REFERENCES tbl_departamento (id_departamento)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ds_segmento
    FOREIGN KEY (id_segmento) REFERENCES tbl_segmento (id_segmento)
    ON UPDATE CASCADE ON DELETE CASCADE,
  UNIQUE KEY uq_departamento_segmento (id_departamento, id_segmento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_tipo_dispositivo  (RN-07: los teléfonos IP son un tipo más)
-- ============================================================================
CREATE TABLE tbl_tipo_dispositivo (
  id_tipo_dispositivo INT AUTO_INCREMENT PRIMARY KEY,
  nombre           VARCHAR(80) NOT NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_tipo_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_equipo
-- ============================================================================
CREATE TABLE tbl_equipo (
  id_equipo        INT AUTO_INCREMENT PRIMARY KEY,
  nombre           VARCHAR(100) NOT NULL,
  marca            VARCHAR(80)  DEFAULT NULL,
  modelo           VARCHAR(80)  DEFAULT NULL,
  id_tipo_dispositivo INT NOT NULL,
  id_departamento  INT NOT NULL,
  id_seccion       INT DEFAULT NULL,
  es_telefono_ip   TINYINT(1) NOT NULL DEFAULT 0,
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_equipo_tipo
    FOREIGN KEY (id_tipo_dispositivo) REFERENCES tbl_tipo_dispositivo (id_tipo_dispositivo)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_equipo_departamento
    FOREIGN KEY (id_departamento) REFERENCES tbl_departamento (id_departamento)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_equipo_seccion
    FOREIGN KEY (id_seccion) REFERENCES tbl_seccion (id_seccion)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_ip
--  RN-03: no puede haber IP duplicadas  -> UNIQUE(direccion)
--  RN-06: toda IP pertenece a un segmento -> id_segmento NOT NULL
--  RN-02: una IP a un solo equipo -> id_equipo (se controla por trigger/estado)
-- ============================================================================
CREATE TABLE tbl_ip (
  id_ip            INT AUTO_INCREMENT PRIMARY KEY,
  direccion        VARCHAR(15) NOT NULL,
  id_segmento      INT NOT NULL,
  estado           ENUM('disponible','ocupada','reservada') NOT NULL DEFAULT 'disponible',
  id_equipo        INT DEFAULT NULL,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ip_segmento
    FOREIGN KEY (id_segmento) REFERENCES tbl_segmento (id_segmento)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ip_equipo
    FOREIGN KEY (id_equipo) REFERENCES tbl_equipo (id_equipo)
    ON UPDATE CASCADE ON DELETE SET NULL,
  UNIQUE KEY uq_ip_direccion (direccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_usuario  (roles: administrador / tecnico / consulta)
-- ============================================================================
CREATE TABLE tbl_usuario (
  id_usuario       INT AUTO_INCREMENT PRIMARY KEY,
  nombre           VARCHAR(120) NOT NULL,
  username         VARCHAR(50)  NOT NULL,
  password_hash    VARCHAR(255) NOT NULL,           -- bcrypt
  rol              ENUM('administrador','tecnico','consulta') NOT NULL DEFAULT 'consulta',
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_usuario_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_asignacion_ip  (historial de asignaciones)
-- ============================================================================
CREATE TABLE tbl_asignacion_ip (
  id_asignacion    INT AUTO_INCREMENT PRIMARY KEY,
  id_ip            INT NOT NULL,
  id_equipo        INT NOT NULL,
  fecha_asignacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_liberacion DATETIME DEFAULT NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,   -- 1 = asignación vigente
  id_usuario       INT DEFAULT NULL,                -- quién realizó la acción
  CONSTRAINT fk_asig_ip
    FOREIGN KEY (id_ip) REFERENCES tbl_ip (id_ip)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_asig_equipo
    FOREIGN KEY (id_equipo) REFERENCES tbl_equipo (id_equipo)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_asig_usuario
    FOREIGN KEY (id_usuario) REFERENCES tbl_usuario (id_usuario)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
--  TABLA: tbl_bitacora  (auditoría automática)
-- ============================================================================
CREATE TABLE tbl_bitacora (
  id_bitacora      INT AUTO_INCREMENT PRIMARY KEY,
  usuario          VARCHAR(50)  NOT NULL,
  accion           VARCHAR(60)  NOT NULL,           -- Inicio de sesión, Alta, Baja, Modificación, Asignación IP, Liberación IP
  modulo           VARCHAR(60)  NOT NULL,
  detalle          VARCHAR(255) DEFAULT NULL,
  fecha            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
--  TRIGGERS - Reglas de negocio a nivel de base de datos
--  RN-05: un equipo solo puede tener UNA IP activa (estado = 'ocupada').
-- ============================================================================
DELIMITER $$

DROP TRIGGER IF EXISTS trg_ip_una_activa_ins $$
CREATE TRIGGER trg_ip_una_activa_ins
BEFORE INSERT ON tbl_ip
FOR EACH ROW
BEGIN
  IF NEW.estado = 'ocupada' AND NEW.id_equipo IS NOT NULL THEN
    IF (SELECT COUNT(*) FROM tbl_ip
        WHERE id_equipo = NEW.id_equipo AND estado = 'ocupada') > 0 THEN
      SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'RN-05: el equipo ya tiene una IP activa';
    END IF;
  END IF;
END $$

DROP TRIGGER IF EXISTS trg_ip_una_activa_upd $$
CREATE TRIGGER trg_ip_una_activa_upd
BEFORE UPDATE ON tbl_ip
FOR EACH ROW
BEGIN
  IF NEW.estado = 'ocupada' AND NEW.id_equipo IS NOT NULL THEN
    IF (SELECT COUNT(*) FROM tbl_ip
        WHERE id_equipo = NEW.id_equipo AND estado = 'ocupada'
          AND id_ip <> NEW.id_ip) > 0 THEN
      SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'RN-05: el equipo ya tiene una IP activa';
    END IF;
  END IF;
END $$

-- ----------------------------------------------------------------------------
--  PROCEDIMIENTO: sp_generar_ips
--  RN-04: genera automáticamente las 254 direcciones (.1 a .254) de un segmento
--  Parámetros: p_id_segmento (INT), p_base (VARCHAR ej. '192.168.10')
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_generar_ips $$
CREATE PROCEDURE sp_generar_ips(IN p_id_segmento INT, IN p_base VARCHAR(11))
BEGIN
  DECLARE i INT DEFAULT 1;
  IF (SELECT COUNT(*) FROM tbl_ip WHERE id_segmento = p_id_segmento) > 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'El segmento ya tiene direcciones IP generadas';
  END IF;
  WHILE i <= 254 DO   -- RN-04: máximo 254 direcciones
    INSERT INTO tbl_ip (direccion, id_segmento, estado)
      VALUES (CONCAT(p_base, '.', i), p_id_segmento, 'disponible');
    SET i = i + 1;
  END WHILE;
END $$

DELIMITER ;

-- ============================================================================
--  DATOS DE EJEMPLO  (Hospital Militar)
-- ============================================================================

-- ---- Usuarios (contraseñas bcrypt) ----
INSERT INTO tbl_usuario (nombre, username, password_hash, rol) VALUES
 ('Administrador del Sistema', 'admin',    '$2b$12$Sj6QBU2vhVh9Lsmb./ASo..bL7oFEpRxPcxDC5Uu0Z5ivKC2gc4/i', 'administrador'),
 ('Técnico de Informática',    'tecnico',  '$2b$12$l6TlV5eFuMinP1DfFJBvDetjwDCv44AASDfobXCCsc0oxtlp/mMqC', 'tecnico'),
 ('Usuario de Consulta',       'consulta', '$2b$12$XTO0AY5jCtiXF.nInlwuwuBfxq2PUxXiFL9vh4QEN1lbKPUW1P5GK', 'consulta');

-- ---- Tipos de dispositivo ----
INSERT INTO tbl_tipo_dispositivo (nombre) VALUES
 ('Computadora de Escritorio'), ('Laptop'), ('Impresora'), ('Servidor'),
 ('Teléfono IP'), ('Access Point'), ('Cámara IP'), ('Switch Administrable');

-- ---- Departamentos ----
INSERT INTO tbl_departamento (nombre, descripcion) VALUES
 ('Dirección General',   'Dirección administrativa del hospital'),
 ('Informática',         'Departamento de Desarrollo Institucional / Informática'),
 ('Cardiología',         'Servicio de cardiología y hemodinamia'),
 ('Pediatría',           'Atención pediátrica y neonatología'),
 ('Emergencias',         'Servicio de urgencias médicas'),
 ('Laboratorio Clínico', 'Análisis clínicos y patología'),
 ('Farmacia',            'Farmacia hospitalaria');

-- ---- Secciones ----
INSERT INTO tbl_seccion (nombre, id_departamento) VALUES
 ('Soporte Técnico',    (SELECT id_departamento FROM tbl_departamento WHERE nombre='Informática')),
 ('Redes y Servidores', (SELECT id_departamento FROM tbl_departamento WHERE nombre='Informática')),
 ('Consulta Externa',   (SELECT id_departamento FROM tbl_departamento WHERE nombre='Cardiología')),
 ('Hospitalización',    (SELECT id_departamento FROM tbl_departamento WHERE nombre='Pediatría')),
 ('Triaje',             (SELECT id_departamento FROM tbl_departamento WHERE nombre='Emergencias')),
 ('Toma de Muestras',   (SELECT id_departamento FROM tbl_departamento WHERE nombre='Laboratorio Clínico')),
 ('Recepción',          (SELECT id_departamento FROM tbl_departamento WHERE nombre='Dirección General'));

-- ---- Segmentos ----
INSERT INTO tbl_segmento (nombre, direccion_red, mascara, gateway) VALUES
 ('Segmento Administrativo', '192.168.10.0', '255.255.255.0', '192.168.10.254'),
 ('Segmento Informática',    '192.168.20.0', '255.255.255.0', '192.168.20.254'),
 ('Segmento Cardiología',    '192.168.30.0', '255.255.255.0', '192.168.30.254'),
 ('Segmento Teléfonos IP',   '192.168.40.0', '255.255.255.0', '192.168.40.254');

-- ---- Generar las 254 IP de cada segmento (RN-04) ----
CALL sp_generar_ips((SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.10.0'), '192.168.10');
CALL sp_generar_ips((SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.20.0'), '192.168.20');
CALL sp_generar_ips((SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.30.0'), '192.168.30');
CALL sp_generar_ips((SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.40.0'), '192.168.40');

-- ---- Autorización de segmentos por departamento (RN-01) ----
INSERT INTO tbl_departamento_segmento (id_departamento, id_segmento) VALUES
 ((SELECT id_departamento FROM tbl_departamento WHERE nombre='Dirección General'), (SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.10.0')),
 ((SELECT id_departamento FROM tbl_departamento WHERE nombre='Informática'),       (SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.20.0')),
 ((SELECT id_departamento FROM tbl_departamento WHERE nombre='Informática'),       (SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.10.0')),
 ((SELECT id_departamento FROM tbl_departamento WHERE nombre='Cardiología'),       (SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.30.0')),
 ((SELECT id_departamento FROM tbl_departamento WHERE nombre='Emergencias'),       (SELECT id_segmento FROM tbl_segmento WHERE direccion_red='192.168.40.0'));

-- ---- Equipos ----
INSERT INTO tbl_equipo (nombre, marca, modelo, id_tipo_dispositivo, id_departamento, es_telefono_ip) VALUES
 ('PC-DIR-01',    'Dell',   'OptiPlex 7090',   (SELECT id_tipo_dispositivo FROM tbl_tipo_dispositivo WHERE nombre='Computadora de Escritorio'), (SELECT id_departamento FROM tbl_departamento WHERE nombre='Dirección General'), 0),
 ('PC-INF-01',    'HP',     'EliteDesk 800',   (SELECT id_tipo_dispositivo FROM tbl_tipo_dispositivo WHERE nombre='Computadora de Escritorio'), (SELECT id_departamento FROM tbl_departamento WHERE nombre='Informática'), 0),
 ('SRV-DATOS-01', 'Dell',   'PowerEdge R740',  (SELECT id_tipo_dispositivo FROM tbl_tipo_dispositivo WHERE nombre='Servidor'),                   (SELECT id_departamento FROM tbl_departamento WHERE nombre='Informática'), 0),
 ('TEL-EMER-01',  'Cisco',  'IP Phone 8845',   (SELECT id_tipo_dispositivo FROM tbl_tipo_dispositivo WHERE nombre='Teléfono IP'),                (SELECT id_departamento FROM tbl_departamento WHERE nombre='Emergencias'), 1),
 ('TEL-EMER-02',  'Cisco',  'IP Phone 8845',   (SELECT id_tipo_dispositivo FROM tbl_tipo_dispositivo WHERE nombre='Teléfono IP'),                (SELECT id_departamento FROM tbl_departamento WHERE nombre='Emergencias'), 1),
 ('PC-CARD-01',   'Lenovo', 'ThinkCentre M70', (SELECT id_tipo_dispositivo FROM tbl_tipo_dispositivo WHERE nombre='Computadora de Escritorio'), (SELECT id_departamento FROM tbl_departamento WHERE nombre='Cardiología'), 0);

-- ---- Asignaciones de ejemplo (marca IP como ocupada y registra historial) ----
-- PC-DIR-01 -> 192.168.10.10
UPDATE tbl_ip SET estado='ocupada', id_equipo=(SELECT id_equipo FROM tbl_equipo WHERE nombre='PC-DIR-01')
  WHERE direccion='192.168.10.10';
INSERT INTO tbl_asignacion_ip (id_ip, id_equipo, id_usuario)
  VALUES ((SELECT id_ip FROM tbl_ip WHERE direccion='192.168.10.10'),
          (SELECT id_equipo FROM tbl_equipo WHERE nombre='PC-DIR-01'),
          (SELECT id_usuario FROM tbl_usuario WHERE username='admin'));

-- PC-INF-01 -> 192.168.20.15
UPDATE tbl_ip SET estado='ocupada', id_equipo=(SELECT id_equipo FROM tbl_equipo WHERE nombre='PC-INF-01')
  WHERE direccion='192.168.20.15';
INSERT INTO tbl_asignacion_ip (id_ip, id_equipo, id_usuario)
  VALUES ((SELECT id_ip FROM tbl_ip WHERE direccion='192.168.20.15'),
          (SELECT id_equipo FROM tbl_equipo WHERE nombre='PC-INF-01'),
          (SELECT id_usuario FROM tbl_usuario WHERE username='admin'));

-- SRV-DATOS-01 -> 192.168.20.5
UPDATE tbl_ip SET estado='ocupada', id_equipo=(SELECT id_equipo FROM tbl_equipo WHERE nombre='SRV-DATOS-01')
  WHERE direccion='192.168.20.5';
INSERT INTO tbl_asignacion_ip (id_ip, id_equipo, id_usuario)
  VALUES ((SELECT id_ip FROM tbl_ip WHERE direccion='192.168.20.5'),
          (SELECT id_equipo FROM tbl_equipo WHERE nombre='SRV-DATOS-01'),
          (SELECT id_usuario FROM tbl_usuario WHERE username='admin'));

-- TEL-EMER-01 -> 192.168.40.20
UPDATE tbl_ip SET estado='ocupada', id_equipo=(SELECT id_equipo FROM tbl_equipo WHERE nombre='TEL-EMER-01')
  WHERE direccion='192.168.40.20';
INSERT INTO tbl_asignacion_ip (id_ip, id_equipo, id_usuario)
  VALUES ((SELECT id_ip FROM tbl_ip WHERE direccion='192.168.40.20'),
          (SELECT id_equipo FROM tbl_equipo WHERE nombre='TEL-EMER-01'),
          (SELECT id_usuario FROM tbl_usuario WHERE username='admin'));

-- ---- Bitácora inicial ----
INSERT INTO tbl_bitacora (usuario, accion, modulo, detalle) VALUES
 ('sistema', 'Inicialización', 'Sistema', 'Datos de ejemplo cargados');

-- ============================================================================
--  VISTAS ÚTILES (RN-08 / RN-09) - IP disponibles y estadísticas por segmento
-- ============================================================================
CREATE OR REPLACE VIEW vw_ip_disponibles AS
  SELECT i.id_ip, i.direccion, s.nombre AS segmento
  FROM tbl_ip i
  JOIN tbl_segmento s ON s.id_segmento = i.id_segmento
  WHERE i.estado = 'disponible';

CREATE OR REPLACE VIEW vw_estadistica_segmento AS
  SELECT
    s.id_segmento,
    s.nombre,
    COUNT(i.id_ip) AS total_ips,
    SUM(i.estado = 'ocupada')    AS ocupadas,
    SUM(i.estado = 'disponible') AS disponibles,
    SUM(i.estado = 'reservada')  AS reservadas,
    ROUND(SUM(i.estado='ocupada') / NULLIF(COUNT(i.id_ip),0) * 100, 1) AS porcentaje_ocupacion
  FROM tbl_segmento s
  LEFT JOIN tbl_ip i ON i.id_segmento = s.id_segmento
  WHERE s.activo = 1
  GROUP BY s.id_segmento, s.nombre;

-- ============================================================================
--  FIN DEL SCRIPT
-- ============================================================================
