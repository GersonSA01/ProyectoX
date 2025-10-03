# Sistema DreamIAlert - Generador de Preguntas Universitarias

Sistema web desarrollado en Django para la generación automática de preguntas universitarias con integración a Supabase. Permite crear partidas, unidades, preguntas y opciones, además de generar documentos Word y prompts para IA.

## 🚀 Características Principales

- **Gestión de Partidas**: Crear y administrar partidas de preguntas
- **Unidades Temáticas**: Organizar contenido por unidades con filtros
- **Generación de Preguntas**: Crear preguntas automáticamente con opciones
- **Integración Supabase**: Base de datos en la nube
- **Generación de Documentos**: Exportar a Word con formato profesional
- **Prompts para IA**: Generar prompts estructurados para inteligencia artificial
- **Interfaz Moderna**: UI responsive con Bootstrap

## 📋 Requisitos del Sistema

### Software Requerido
- **Python 3.11+** (recomendado 3.13)
- **Git** para clonar el repositorio
- **Navegador web** (Chrome, Firefox, Edge)

### Cuentas Necesarias
- **Supabase**: Para base de datos en la nube
- **Cuenta de GitHub** (opcional): Para clonar el repositorio

## 🛠️ Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
# Opción 1: Si tienes el código en GitHub
git clone https://github.com/tu-usuario/sistema-dreamialert.git
cd sistema-dreamialert

# Opción 2: Si tienes el código en una carpeta
# Copia la carpeta del proyecto a tu computadora
```

### 2. Configurar Python

#### Windows:
```bash
# Verificar versión de Python
python --version

# Si no tienes Python, descárgalo desde: https://python.org
# Asegúrate de marcar "Add Python to PATH" durante la instalación
```

#### Linux/Mac:
```bash
# Verificar versión de Python
python3 --version

# Instalar Python si es necesario
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (con Homebrew):
brew install python3
```

### 3. Crear Entorno Virtual

```bash
# Navegar a la carpeta del proyecto
cd C:\Trabajo\Sistema  # En Windows
# o
cd /ruta/a/tu/proyecto  # En Linux/Mac

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
# Instalar paquetes requeridos
pip install -r requirements.txt
```

### 5. Configurar Supabase

#### 5.1 Crear Proyecto en Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Crea una cuenta o inicia sesión
3. Crea un nuevo proyecto
4. Anota la **URL** y **API Key** de tu proyecto

#### 5.2 Configurar Variables de Entorno
1. Crea un archivo `.env` en la raíz del proyecto:

```env
# Supabase Configuration
SUPABASE_URL=tu_url_de_supabase_aqui
SUPABASE_KEY=tu_api_key_de_supabase_aqui

# Django Configuration
SECRET_KEY=tu_clave_secreta_django_aqui
DEBUG=True
```

#### 5.3 Crear Tablas en Supabase
Ejecuta este SQL en el editor SQL de Supabase:

```sql
-- Tabla de carreras
CREATE TABLE carreras (
    carrera_id SERIAL PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de asignaturas
CREATE TABLE asignaturas (
    asignatura_id SERIAL PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL,
    carrera_id INTEGER REFERENCES carreras(carrera_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de programas analíticos
CREATE TABLE programas_analiticos (
    linea_educativa_id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    contexto TEXT,
    asignatura_id INTEGER REFERENCES asignaturas(asignatura_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de unidades
CREATE TABLE unidades (
    unidad_id SERIAL PRIMARY KEY,
    numero_unidad INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    num_preguntas INTEGER DEFAULT 0,
    programa_analitico_id INTEGER REFERENCES programas_analiticos(linea_educativa_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de partidas
CREATE TABLE partidas (
    partida_id SERIAL PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL,
    asignatura_id INTEGER REFERENCES asignaturas(asignatura_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de preguntas
CREATE TABLE preguntas (
    pregunta_id SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    enunciado TEXT NOT NULL,
    unidad_id INTEGER REFERENCES unidades(unidad_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de opciones
CREATE TABLE opciones (
    opcion_id SERIAL PRIMARY KEY,
    opcion TEXT NOT NULL,
    es_correcta BOOLEAN DEFAULT FALSE,
    pregunta_id INTEGER REFERENCES preguntas(pregunta_id),
    media_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Configurar Django

```bash
# Aplicar migraciones (si es necesario)
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic
```

### 7. Ejecutar el Servidor

```bash
# Iniciar servidor de desarrollo
python manage.py runserver

# El sistema estará disponible en:
# http://127.0.0.1:8000
```

## 📁 Estructura del Proyecto

```
Sistema/
├── app/                          # Aplicación principal
│   ├── templates/               # Plantillas HTML
│   │   ├── partidas/           # Templates de partidas
│   │   ├── unidades/           # Templates de unidades
│   │   └── preguntas/          # Templates de preguntas
│   ├── static/                 # Archivos estáticos
│   │   └── img/               # Imágenes (logo UNEMI)
│   ├── models.py              # Modelos de Django
│   ├── views.py               # Vistas y lógica de negocio
│   ├── urls.py                # URLs de la aplicación
│   ├── repositories.py        # Repositorios para Supabase
│   └── supabase_client.py     # Cliente de Supabase
├── project/                    # Configuración del proyecto
│   ├── settings.py            # Configuración de Django
│   └── urls.py                # URLs principales
├── requirements.txt            # Dependencias de Python
├── manage.py                   # Script de gestión de Django
└── README.md                   # Este archivo
```

## 🔧 Configuración Adicional

### Personalizar Logo
1. Coloca tu logo en `app/static/img/unemi.png`
2. El sistema lo usará automáticamente en los documentos generados

### Configurar Base de Datos Local (Opcional)
Si prefieres usar SQLite en lugar de Supabase:

```python
# En project/settings.py, cambia:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 🚀 Uso del Sistema

### 1. Acceder al Sistema
- Abre tu navegador
- Ve a `http://127.0.0.1:8000`

### 2. Crear una Partida
1. Haz clic en "Crear Partida"
2. Completa los datos requeridos
3. El sistema creará automáticamente unidades y preguntas

### 3. Gestionar Preguntas
1. Ve a la sección "Preguntas"
2. Filtra por partida, programa analítico o unidad
3. Edita preguntas y opciones inline

### 4. Generar Documentos
1. En la sección de preguntas
2. Haz clic en "Descargar Google Docs"
3. Se generará un documento Word con formato profesional

### 5. Generar Prompts
1. En la sección de preguntas
2. Haz clic en "Ver Prompt"
3. Copia el prompt generado para usar con IA

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```bash
# Asegúrate de que el entorno virtual esté activado
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error de Conexión a Supabase
1. Verifica que las variables de entorno estén correctas
2. Asegúrate de que la URL y API Key sean válidas
3. Revisa que las tablas existan en Supabase

### Error de Permisos en Windows
```bash
# Ejecuta PowerShell como administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Puerto 8000 en Uso
```bash
# Usa un puerto diferente
python manage.py runserver 8080
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** del servidor Django
2. **Verifica la configuración** de Supabase
3. **Asegúrate** de que todas las dependencias estén instaladas
4. **Consulta** la documentación de Django y Supabase

## 🔄 Actualizaciones

Para actualizar el sistema:

```bash
# Detener el servidor (Ctrl+C)
# Activar entorno virtual
venv\Scripts\activate

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar servidor
python manage.py runserver
```

## 📝 Notas Importantes

- **Desarrollo**: Este sistema está configurado para desarrollo local
- **Producción**: Para producción, configura variables de entorno seguras
- **Backup**: Realiza copias de seguridad regulares de tu base de datos Supabase
- **Seguridad**: No compartas tus claves de API de Supabase

## 🎯 Próximos Pasos

1. **Personaliza** el sistema según tus necesidades
2. **Agrega** más funcionalidades si es necesario
3. **Configura** un dominio personalizado para producción
4. **Implementa** autenticación de usuarios si es requerido

---

**¡Sistema listo para usar! 🎉**

Para más información, consulta la documentación de [Django](https://docs.djangoproject.com/) y [Supabase](https://supabase.com/docs).
