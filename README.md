# SQLTrainingLab

**SQLTrainingLab** es una aplicación de escritorio desarrollada en Python que funciona como entorno de desarrollo SQL en el ámbito académico. Ofrece un entorno simplificado y seguro para el aprendizaje de SQL, con autenticación, aislamiento de entornos y sistema de auditoría integrado para la monitorización de la actividad de los alumnos.

Utiliza una base de datos estándar de **PostgreSQL**, ya sea local o en la nube. Posee dos modos de interfaz: terminal y gráfica. Se recomienda utilizar la segunda.

Para su uso por parte de estudiantes, es necesario que el docente inicie sesión en la app mediante un superusuario "administrador", ejecute la opción de setup de la base de datos y cree usuarios para los alumnos a partir de Excel mediante la opción que se proporciona. Una vez realizados estos procesos, los estudiantes pueden acceder a la aplicación con sus credenciales y realizar sus prácticas de SQL bajo el registro de su actividad. Para la consulta de este, el administrador posee una opción para exportar los datos registrados, que se exportan automáticamente a Excel.

## Requisitos previos

- Python 3.11 o superior: https://www.python.org/downloads/
  - Durante la instalación se recomienda marcar la opción **Add Python to PATH**.

- Una vez instalado Python, instala las dependencias del proyecto desde el directorio raíz:

    ```bash
    pip install -r requirements.txt
    ```

## Configuración

SQLTrainingLab requiere un archivo `.env` en el directorio raíz del proyecto con los datos de conexión a la base de datos, el nombre del usuario administrador y el modo de interfaz. Se incluye el archivo `.env.example` como plantilla de referencia. Para configurar la aplicación, completa cada campo y renómbralo como `.env`.

> La base de datos PostgreSQL debe crearse previamente por el administrador antes de poner en marcha la aplicación.

## Archivos especiales

- `imports/users_import.xlsx` — ejemplo de fichero Excel para la creación automática de usuarios. Deben respetarse el nombre del archivo, de la hoja y de las dos columnas, incluyendo en estas los datos de los usuarios a crear.
- `exports/auditing_data.xlsx` — generado mediante la opción de exportación del administrador, no incluido inicialmente. Contiene cuatro hojas con los datos de registro de actividad exportados.
- `logs/` — carpeta con archivos `.log` de errores. Se genera un archivo por día de uso, no incluida inicialmente.

## Ejecución

**Opción 1 — Intérprete de Python:**
En el directorio de código ejecutar:
```bash
python .\main.py
```

**Opción 2 — Archivo `.bat`:**
Doble clic sobre `run_sqltraininglab.bat`.
