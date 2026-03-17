-- Creación de rol de grupo de usuarios base
CREATE ROLE base_users NOINHERIT;

-- Revocación de todos los permisos en public a todo rol público
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM base_users;

-------------------------------------------------------------------------------------

-- Schema para las tablas de auditoría
CREATE SCHEMA IF NOT EXISTS auditing;

-- Revocación de todos los permisos a todo rol público
REVOKE ALL ON SCHEMA auditing FROM PUBLIC;
REVOKE ALL ON SCHEMA auditing FROM base_users;

-- Revocación de permisos por defecto a tablas futuras para todo rol público
ALTER DEFAULT PRIVILEGES IN SCHEMA auditing 
    REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA auditing 
    REVOKE ALL ON TABLES FROM base_users;

-------------------------------------------------------------------------------------

-- Schema para las funciones SECURITY DEFINER para auditoría
CREATE SCHEMA IF NOT EXISTS auditing_functions;

-- Revocación de todos los permisos a todo rol público
REVOKE ALL ON SCHEMA auditing_functions FROM PUBLIC;
REVOKE ALL ON SCHEMA auditing_functions FROM base_users;

-- Dar permiso de uso a los usuarios base para poder ejecutar funciones
GRANT USAGE ON SCHEMA auditing_functions TO base_users;

-- Revocación de permisos por defecto a funciones futuras para todo rol público
ALTER DEFAULT PRIVILEGES IN SCHEMA auditing_functions 
    REVOKE ALL ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA auditing_functions 
    REVOKE ALL ON FUNCTIONS FROM base_users;

-------------------------------------------------------------------------------------

-- Schema para las funciones SECURITY DEFINER auxiliares
CREATE SCHEMA IF NOT EXISTS aux_functions;

-- Revocación de todos los permisos a todo rol público
REVOKE ALL ON SCHEMA aux_functions FROM PUBLIC;
REVOKE ALL ON SCHEMA aux_functions FROM base_users;

-- Dar permiso de uso a los usuarios base para poder ejecutar funciones
GRANT USAGE ON SCHEMA aux_functions TO base_users;

-- Revocación de permisos por defecto a funciones futuras para todo rol público
ALTER DEFAULT PRIVILEGES IN SCHEMA aux_functions 
    REVOKE ALL ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA aux_functions 
    REVOKE ALL ON FUNCTIONS FROM base_users;