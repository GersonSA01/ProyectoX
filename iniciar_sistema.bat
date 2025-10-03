@echo off
echo ========================================
echo    SISTEMA DE PREGUNTAS AUTOMATICAS
echo ========================================
echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Creando migraciones...
python manage.py makemigrations

echo.
echo Aplicando migraciones...
python manage.py migrate

echo.
echo Creando datos de ejemplo...
python manage.py crear_datos_ejemplo --asignaturas 5 --programas-por-asignatura 3 --unidades-por-programa 4

echo.
echo Iniciando servidor...
echo.
echo ========================================
echo   SERVIDOR INICIADO EXITOSAMENTE
echo ========================================
echo.
echo Accede a: http://127.0.0.1:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
python manage.py runserver
