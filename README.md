# FastAPI Persona CRUD (MySQL por defecto)

Proyecto de demostración con FastAPI + SQLAlchemy y estructura MVC para un CRUD de `Persona`. Usa MySQL por defecto y permite apuntar a otra base SQL mediante la variable de entorno `DATABASE_URL` (configurable en `.env`).

## Requisitos

- Python 3.10+ (recomendado 3.11)

## Instalación y ejecución

1. Crear entorno virtual e instalar dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales de MySQL
   # Por defecto: DATABASE_URL=mysql+pymysql://user:password@localhost:3306/fastapi_demo
   ```

3. Ejecutar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Documentación interactiva:
   - Swagger UI: <http://localhost:8000/docs>
   - ReDoc: <http://localhost:8000/redoc>

## Conexión a otras bases de datos

Edita `DATABASE_URL` en `.env`.
- MySQL: `mysql+pymysql://user:password@localhost:3306/mydb`

> Nota: Instala el driver correspondiente (psycopg2, PyMySQL, pyodbc, etc.).

## Ejemplo de `.env` (MySQL local)

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/nombre_basedatos
```

## Endpoints principales

- `GET /health` → estado del servicio
- `POST /personas` → crear persona
- `GET /personas` → listar personas (`skip`, `limit`)
- `GET /personas/{id}` → obtener persona por ID
- `PUT /personas/{id}` → actualizar (parcial) persona
- `DELETE /personas/{id}` → eliminar persona

### Esquemas (JSON)

- Crear:
  ```json
  {
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan.perez@example.com",
    "phone": "+57 3000000000",
    "birth_date": "1990-05-20",
    "is_active": true,
    "notes": "Cliente frecuente"
  }
  ```

- Actualizar (parcial):
  ```json
  {
    "email": "juan.perez2@example.com",
    "notes": "Actualizado"
  }
  ```

## Colección de Postman

Importa `FastAPI-CRUD-Demo.postman_collection.json` en Postman. Variables:

- `base_url` (por defecto `http://localhost:8000`)
- `persona_id` (por defecto `1`)

## Notas

- Las tablas se crean automáticamente al iniciar (solo con fines de demo).
- Asegúrate de crear la base de datos en MySQL y de que el usuario tenga permisos (por ejemplo, `CREATE DATABASE fastapi_demo;`).

## Estructura MVC

- `app/models/` → modelos SQLAlchemy (por ejemplo, `persona.py`).
- `app/views/` → esquemas Pydantic (por ejemplo, `persona.py`).
- `app/controllers/` → routers/controladores FastAPI (por ejemplo, `persona_controller.py`).

## Pruebas rápidas (curl)

```bash
# Health
curl -s http://127.0.0.1:8000/health

# Crear persona
curl -s -X POST http://127.0.0.1:8000/personas \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name":"Juan",
    "last_name":"Perez",
    "email":"juan.perez@example.com",
    "phone":"+57 3000000000",
    "birth_date":"1990-05-20",
    "is_active":true,
    "notes":"Cliente frecuente"
  }'

# Listar
curl -s http://127.0.0.1:8000/personas

# Obtener por ID
curl -s http://127.0.0.1:8000/personas/1

# Actualizar parcial
curl -s -X PUT http://127.0.0.1:8000/personas/1 \
  -H 'Content-Type: application/json' \
  -d '{"email":"juan.perez2@example.com","notes":"Actualizado"}'

# Eliminar
curl -s -X DELETE http://127.0.0.1:8000/personas/1 -i

## Detener el servidor

- Si lo iniciaste en la misma terminal: usa `CTRL+C`.
- Si corre en background, puedes cerrar esa terminal o matar el proceso de uvicorn (`pkill -f uvicorn`).


## Endpoints desarrollados por Esteban

- `POST /personas/poblar` - Carga masiva con Faker (1 a 1000 registros, emails únicos con dominios reales).
- `DELETE /personas/reset` - Borra todos los registros y devuelve cuántos eliminó.
- `GET /personas/estadisticas/dominios` - Cantidad de personas por proveedor de correo.