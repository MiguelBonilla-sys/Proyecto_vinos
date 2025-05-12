# Guía de Despliegue en Streamlit Cloud

Sigue estos pasos para desplegar la aplicación de Predicción de Calidad de Vinos en Streamlit Cloud:

## 1. Preparar el repositorio

1. Asegúrate de que todos los archivos estén correctamente configurados:
   - `app.py`: Aplicación principal de Streamlit
   - `requirements.txt`: Dependencias del proyecto
   - `.streamlit/config.toml`: Configuración de Streamlit
   - `.streamlit/secrets.toml`: Secretos para conexiones de base de datos (local)
   - `README.md`: Documentación del proyecto
   - `Procfile`: Instrucciones para despliegue
   - `runtime.txt`: Versión de Python
   - Modelos entrenados: `dt_Classifier_ptap.pkl` y `xgb_classfier_ptap.pkl`

2. Sube tu código a GitHub:
   ```bash
   git init
   git add .
   git commit -m "Configuración inicial para despliegue en Streamlit"
   git remote add origin <URL_DE_TU_REPOSITORIO>
   git push -u origin master
   ```

## 2. Despliegue en Streamlit Cloud

1. Ve a [Streamlit Cloud](https://streamlit.io/cloud) e inicia sesión con tu cuenta GitHub.
2. Haz clic en "New app".
3. Selecciona tu repositorio, la rama (master o main) y especifica que el archivo principal es `app.py`.
4. En la sección "Advanced settings", ingresa los secretos:
   - Haz clic en "Secrets"
   - Añade los mismos secretos que tienes en tu archivo local `.streamlit/secrets.toml`:
     ```toml
     [postgres]
     url = "postgresql://vinosdb_owner:npg_g2Xwd7buHUse@ep-plain-truth-a41r71te-pooler.us-east-1.aws.neon.tech/vinosdb?sslmode=require"
     ```
5. Haz clic en "Deploy".
6. Espera a que la aplicación se construya y despliegue (esto puede tomar unos minutos).

## 3. Verificación Post-Despliegue

1. Cuando la aplicación esté desplegada, verifica que:
   - La interfaz de usuario se cargue correctamente
   - Las imágenes se muestren correctamente
   - La conexión a la base de datos funcione (prueba el botón "Cargar datos de muestra desde BD")
   - La carga de archivos CSV y la predicción funcionen correctamente

## 4. Resolución de Problemas Comunes

- **Problema con las Imágenes**: Si las imágenes no se cargan, verifica que las rutas sean correctas.
- **Error de Base de Datos**: Asegúrate de que los secretos estén configurados correctamente en Streamlit Cloud.
- **Error con los Modelos**: Si hay problemas con los modelos pickled, puede ser necesario regenerarlos con una versión de scikit-learn compatible con la versión en Streamlit Cloud.

## 5. Mantenimiento

1. Para actualizar la aplicación después de cambios en tu repositorio:
   - Simplemente haz push a la misma rama en GitHub
   - Streamlit Cloud detectará los cambios y reconstruirá automáticamente la aplicación

2. Para monitorear el uso:
   - Utiliza la sección "Metrics" en el dashboard de Streamlit Cloud
