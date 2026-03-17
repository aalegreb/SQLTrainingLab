
-- CAMBIAR CONTRASEÑA
CREATE OR REPLACE FUNCTION aux_functions.change_role_password(
    p_role_name text,
    p_new_password text
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
BEGIN
    EXECUTE format(
        'ALTER ROLE %I WITH LOGIN PASSWORD %L',
        p_role_name,
        p_new_password
    );

    UPDATE auditing.users
    SET needs_password_change = FALSE
    WHERE username = p_role_name;

    IF NOT FOUND THEN
        RETURN -1;
    END IF;

    RETURN 0;
END;
$$;

-- OBTENER TABLAS EXISTENTES EN UN SCHEMA Y SUS COLUMNAS
CREATE OR REPLACE FUNCTION aux_functions.get_schema_tables(
    p_schema TEXT
)
RETURNS TABLE (
    table_name   TEXT,
    column_name  TEXT,
    data_type    TEXT
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
    SELECT
        c.table_name,
        c.column_name,
        c.data_type
    FROM information_schema.columns c
    JOIN information_schema.tables t
        ON c.table_schema = t.table_schema
        AND c.table_name = t.table_name
    WHERE c.table_schema = p_schema
        AND t.table_type = 'BASE TABLE'
    ORDER BY c.table_name, c.ordinal_position;
$$;

-- OBTENER VISTAS EXISTENTES EN UN SCHEMA Y SUS COLUMNAS
CREATE OR REPLACE FUNCTION aux_functions.get_schema_views(
    p_schema TEXT
)
RETURNS TABLE (
    view_name    TEXT,
    column_name  TEXT,
    data_type    TEXT
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
    SELECT
        c.table_name AS view_name,
        c.column_name,
        c.data_type
    FROM information_schema.columns c
    JOIN information_schema.tables t
        ON c.table_schema = t.table_schema
        AND c.table_name = t.table_name
    WHERE c.table_schema = p_schema
        AND t.table_type = 'VIEW'
    ORDER BY c.table_name, c.ordinal_position;
$$;

-- OBTENER FUNCIONES EXISTENTES EN UN SCHEMA
CREATE OR REPLACE FUNCTION aux_functions.get_schema_functions(
    p_schema TEXT
)
RETURNS TABLE (
    function_name TEXT
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
    SELECT p.proname AS function_name
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = p_schema
    ORDER BY p.proname;
$$;


-- Permisos para ejecutar las funciones
GRANT EXECUTE ON FUNCTION 
    aux_functions.change_role_password(text, text) TO base_users;
GRANT EXECUTE ON FUNCTION 
    aux_functions.get_schema_tables(text) TO base_users;
GRANT EXECUTE ON FUNCTION 
    aux_functions.get_schema_views(text) TO base_users;
GRANT EXECUTE ON FUNCTION 
    aux_functions.get_schema_functions(text) TO base_users;