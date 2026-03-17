
-- CREAR USUARIO
CREATE OR REPLACE FUNCTION auditing_functions.create_user(
    p_full_name VARCHAR,
    p_username VARCHAR,
    p_email VARCHAR
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
DECLARE
    v_user_id BIGINT;
BEGIN
    INSERT INTO auditing.users(full_name, username, email)
    VALUES (p_full_name, p_username, p_email)
    RETURNING id INTO v_user_id;

    RETURN v_user_id;
END;
$$;

-- BUSCAR ID DE USUARIO
CREATE OR REPLACE FUNCTION auditing_functions.get_user_id_by_username(
    p_username VARCHAR
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
DECLARE
    v_user_id BIGINT;
BEGIN
    SELECT id
    INTO v_user_id
    FROM auditing.users
    WHERE username = p_username;

    RETURN v_user_id;
END;
$$;

-- COMPROBAR SI USUARIO NECESITA CAMBIAR DE CONTRASEÑA
CREATE OR REPLACE FUNCTION auditing_functions.needs_password_change(
    p_username VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
DECLARE
    v_needs_password_change BOOLEAN;
BEGIN
    SELECT needs_password_change
    INTO v_needs_password_change
    FROM auditing.users
    WHERE username = p_username;

    RETURN v_needs_password_change;
END;
$$;

-- INICIAR SESIÓN
CREATE OR REPLACE FUNCTION auditing_functions.start_session(
    p_user_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
DECLARE
    v_session_id BIGINT;
BEGIN
    INSERT INTO auditing.sessions(user_id)
    VALUES (p_user_id)
    RETURNING id INTO v_session_id;

    RETURN v_session_id;
END;
$$;

-- FINALIZAR SESIÓN
CREATE OR REPLACE FUNCTION auditing_functions.end_session(
    p_session_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
BEGIN
    UPDATE auditing.sessions
    SET ended_at = NOW()
    WHERE id = p_session_id;

    IF NOT FOUND THEN
        RETURN -1;
    END IF;

    RETURN 0;
END;
$$;

-- INICIAR OPERACIÓN
CREATE OR REPLACE FUNCTION auditing_functions.start_statement(
    p_session_id BIGINT,
    p_statement_type VARCHAR,
    p_sql_text TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
DECLARE
    v_op_id BIGINT;
BEGIN
    PERFORM 1 FROM auditing.sessions WHERE id = p_session_id;

    IF NOT FOUND THEN
        RETURN -1;
    END IF;

    INSERT INTO auditing.statements(session_id, statement_type, sql_text)
    VALUES (p_session_id, p_statement_type, p_sql_text)
    RETURNING id INTO v_op_id;

    RETURN v_op_id;
END;
$$;

-- FINALIZAR OPERACIÓN CON ÉXITO
CREATE OR REPLACE FUNCTION auditing_functions.end_statement_ok(
    p_statement_id BIGINT,
    p_row_count INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
BEGIN
    UPDATE auditing.statements
    SET ended_at = NOW(),
        row_count = p_row_count,
        statement_result = 'OK'
    WHERE id = p_statement_id;

    IF NOT FOUND THEN
        RETURN -1;
    END IF;

    RETURN 0;
END;
$$;

-- FINALIZAR OPERACIÓN CON ERROR
CREATE OR REPLACE FUNCTION auditing_functions.end_statement_error(
    p_statement_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
BEGIN

    UPDATE auditing.statements
    SET ended_at = NOW(),
        statement_result = 'ERROR'
    WHERE id = p_statement_id;

    IF NOT FOUND THEN
        RETURN -1;
    END IF;

    RETURN 0;
END;
$$;

-- CREAR ERROR
CREATE OR REPLACE FUNCTION auditing_functions.create_error(
    p_statement_id BIGINT,
    p_error_code VARCHAR,
    p_error_type VARCHAR,
    p_error_message TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_temp
AS $$
DECLARE
    v_error_id BIGINT;
BEGIN
    PERFORM 1 FROM auditing.statements WHERE id = p_statement_id;

    IF NOT FOUND THEN
        RETURN -1;
    END IF;

    INSERT INTO auditing.errors(statement_id, error_code, error_type, 
        error_message)
    VALUES (p_statement_id, p_error_code, p_error_type, p_error_message)
    RETURNING id INTO v_error_id;

    RETURN v_error_id;
END;
$$;


-- Permisos para ejecutar las funciones
GRANT EXECUTE ON FUNCTION 
    auditing_functions.create_user(VARCHAR, VARCHAR, VARCHAR) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.get_user_id_by_username(VARCHAR) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.needs_password_change(VARCHAR) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.start_session(BIGINT) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.end_session(BIGINT) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.start_statement(BIGINT, VARCHAR, TEXT) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.end_statement_ok(BIGINT, INTEGER) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.end_statement_error(BIGINT) TO base_users;
GRANT EXECUTE ON FUNCTION 
    auditing_functions.create_error(BIGINT, VARCHAR, VARCHAR, TEXT) 
    TO base_users;