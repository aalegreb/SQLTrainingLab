------------------------------- BLOQUE 4 -------------------------------

--- PRUEBAS DE VALIDACIÓN DE SQL Y SEGURIDAD

-- P16: Intento de acceso a metadatos
SELECT * FROM INFORMATION_SCHEMA.tables;

-- P17: Intento de modificación de permisos
GRANT USAGE ON SCHEMA schema_user2 TO user1;

-- P18: Intento de modificación de search_path
SET search_path TO public;

-- P19: Intento de acceso a esquema auditing
SELECT * FROM auditing.users;

-- P20: Intento de acceso a esquema de otro usuario
SELECT * FROM schema_user2.nombre_de_tabla;