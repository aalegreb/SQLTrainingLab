--- TABLA USUARIOS ---
CREATE TABLE auditing.users (
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(200) NOT NULL UNIQUE,
    needs_password_change BOOLEAN NOT NULL DEFAULT TRUE
);

--- TABLA SESIONES ---
CREATE TABLE auditing.sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES auditing.users(id),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP
);

--- TABLA SENTENCIAS ---
CREATE TABLE auditing.statements (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES auditing.sessions(id),
    statement_type VARCHAR(50) NOT NULL,
    sql_text TEXT NOT NULL,
    row_count INTEGER,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    statement_result VARCHAR(5) CHECK (statement_result IN ('OK', 'ERROR'))
);

--- TABLA ERRORES ---
CREATE TABLE auditing.errors (
    id BIGSERIAL PRIMARY KEY,
    statement_id BIGINT NOT NULL UNIQUE REFERENCES auditing.statements(id),
    error_code VARCHAR(5),
    error_type VARCHAR(60),
    error_message TEXT NOT NULL
);

------------------------------------------------------------------------

-- Solo el admin puede acceder a las tablas
REVOKE ALL ON ALL TABLES IN SCHEMA auditing FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA auditing FROM base_users;