# Trendify
Proyecto Trendify - Backend

Este repositorio contiene el código fuente del backend para el proyecto Trendify, construido con Python, Flask y Celery.

Arquitectura

API: Flask (app.py) - Maneja las peticiones HTTP de los usuarios.

Modelos de Aplicación: SQLAlchemy (models.py) - Define la estructura de la base de datos de PostgreSQL (usuarios, foro, etc.).

Tareas de Fondo: Celery (tasks.py) - Maneja el web-scraping y el análisis de datos pesados.

Bases de Datos:

PostgreSQL: Para datos de usuarios, autenticación y foro.

MongoDB: Para almacenar los resultados del análisis de tendencias (Big Data).

Broker de Tareas: Redis - Usado por Celery para gestionar la cola de tareas.

Configuración Inicial (Servidor Ubuntu)

Sigue estos pasos para poner en marcha el servidor de prueba.

1. Requisitos del Sistema

Asegúrate de tener instalados los servicios esenciales en Ubuntu:

# Actualizar repositorios
sudo apt update

# Instalar Python y venv (entorno virtual)
sudo apt install python3-pip python3-venv

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Instalar Redis
sudo apt install redis-server

# Instalar MongoDB
# (Sigue la guía oficial de MongoDB para instalar 'mongodb-org' en Ubuntu)
# [https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)


2. Configurar PostgreSQL

Debes crear un usuario y una base de datos para Trendify:

# Iniciar sesión como el superusuario 'postgres'
sudo -u postgres psql

# Dentro de psql:
CREATE DATABASE trendify_app;
CREATE USER trendify_user WITH PASSWORD 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE trendify_app TO trendify_user;
\q


3. Configurar el Proyecto (Este Repositorio)

# Clonar tu repositorio (o copiar los archivos)
# git clone ...
# cd trendify-backend

# 1. Crear un entorno virtual de Python
python3 -m venv venv

# 2. Activar el entorno virtual
source venv/bin/activate
# (Tu terminal debería ahora mostrar '(venv)' al inicio)

# 3. Instalar las dependencias de Python
pip install -r requirements.txt

# 4. Crear tu archivo de configuración
# Copia el ejemplo y luego edítalo
cp .env.example .env

# 5. Edita el archivo .env con tus contraseñas y configuraciones
# (¡IMPORTANTE! Especialmente la DATABASE_URL)
nano .env

# 6. Inicializar y aplicar la migración de la base de datos
# (Esto crea las tablas 'users' en PostgreSQL)
flask db init
flask db migrate -m "Initial user model"
flask db upgrade


4. Ejecutar los Servicios

Necesitarás 3 terminales separadas (o sesiones tmux/screen) para ejecutar todo el sistema:

Terminal 1: Ejecutar la API de Flask

# (Asegúrate de que 'venv' esté activado)
flask run --host=0.0.0.0
# Tu API ahora está corriendo en http://[IP_DE_TU_SERVER]:5000


Terminal 2: Ejecutar el Worker de Celery

# (Asegúrate de que 'venv' esté activado)
celery -A tasks.celery_app worker --loglevel=info
# Este worker está esperando tareas (ej. enviar emails)


Terminal 3: Ejecutar Celery Beat (El programador de las 3 AM)

# (Asegúrate de que 'venv' esté activado)
celery -A tasks.celery_app beat --loglevel=info
# Este servicio se encarga de disparar la tarea 'run_main_trend_analysis'
# a la hora programada.
