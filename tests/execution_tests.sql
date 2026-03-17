------------------------------- BLOQUE 5 -------------------------------

--- P21: PRUEBA DE EJECUCIÓN DE CREACIÓN Y MODIFICACIÓN DE OBJETOS

CREATE TABLE equipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    estadio VARCHAR(100)
);

CREATE TABLE jugadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    dorsal INTEGER CHECK (dorsal > 0),
    equipo_id INTEGER REFERENCES equipos(id)
);

CREATE TABLE partidos (
    id SERIAL PRIMARY KEY,
    local_id INTEGER REFERENCES equipos(id),
    visitante_id INTEGER REFERENCES equipos(id)
);

ALTER TABLE jugadores ADD COLUMN posicion VARCHAR(20);

CREATE VIEW delanteros AS
    SELECT nombre, dorsal, equipo_id
    FROM jugadores
    WHERE posicion = 'Delantero';

CREATE FUNCTION obtener_dorsal(p_nombre VARCHAR)
RETURNS INTEGER AS $$
    SELECT dorsal FROM jugadores WHERE nombre = p_nombre;
$$ LANGUAGE SQL;

------------------------------------------------------------------------
------------------------------------------------------------------------

--- P22: PRUEBAS DE INSERCIÓN Y MANIPULACIÓN DE DATOS

INSERT INTO equipos (nombre, estadio) VALUES
    ('Real Madrid', 'Santiago Bernabéu'),
    ('FC Barcelona', 'Camp Nou'),
    ('Atlético de Madrid', 'Metropolitano');

INSERT INTO jugadores (nombre, dorsal, equipo_id, posicion) VALUES
    ('Lamine Yamal', 10, 2, 'Delantero'),
    ('Julián Álvarez', 19, 3, 'Delantero'),
    ('Thibaut Courtois', 1, 1, 'Portero'),
    ('Federico Valverde', 15, 1, 'Centrocampista');

INSERT INTO partidos (local_id, visitante_id) VALUES
    (1, 2),
    (2, 3),
    (3, 1);

UPDATE jugadores SET dorsal = 8 WHERE nombre = 'Federico Valverde';

DELETE FROM partidos WHERE local_id = 2;

------------------------------------------------------------------------
------------------------------------------------------------------------

--- P23: PRUEBAS DE EJECUCIÓN DE CONSULTAS

SELECT * FROM jugadores;

SELECT nombre, dorsal
    FROM jugadores
    ORDER BY dorsal ASC;

SELECT j.nombre, e.nombre AS equipo, j.posicion
    FROM jugadores j
    JOIN equipos e ON j.equipo_id = e.id;

SELECT e.nombre, COUNT(j.id) AS plantilla_total
    FROM equipos e
    LEFT JOIN jugadores j ON e.id = j.equipo_id
    GROUP BY e.nombre
    HAVING COUNT(j.id) > 0;

SELECT * FROM delanteros;

SELECT obtener_dorsal('Federico Valverde');

------------------------------------------------------------------------
------------------------------------------------------------------------

--- P24: PRUEBAS DE COMANDOS TRUNCATE Y DROP

TRUNCATE TABLE partidos;

DROP FUNCTION obtener_dorsal;

DROP VIEW delanteros;

DROP TABLE partidos;

------------------------------------------------------------------------
------------------------------------------------------------------------

--- PRUEBA DE ERRORES SQL
-- P25: Error de sintaxis
SELEC * FROM jugadores;

-- P26: Columna inexistente
SELECT nacionalidad FROM jugadores;

-- P27: Violación de restricción NOT NULL
INSERT INTO equipos (nombre) VALUES (NULL);

-- P28: Tabla inexistente
SELECT * FROM entrenadores;