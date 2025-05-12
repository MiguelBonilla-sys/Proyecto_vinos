# Predicción de Calidad de Vinos

Aplicación de Streamlit para predecir la calidad de vinos basada en sus características físico-químicas.

## Características

- Predicción de calidad de vinos usando modelos de machine learning
- Soporte para cargar archivos CSV con datos de vinos
- Carga de datos de ejemplo directamente desde base de datos PostgreSQL
- Visualización de resultados con tablas interactivas

## Modelos de ML utilizados

- Árbol de Decisión
- XGBoost

## Requisitos

Ver el archivo `requirements.txt` para las dependencias exactas.

## Configuración

1. Clona este repositorio
2. Instala las dependencias con `pip install -r requirements.txt`
3. Para uso local, crea un archivo `.env` con la URL de conexión a tu base de datos PostgreSQL:
   ```
   POSTGRES_URL = 'postgresql://usuario:contraseña@host/basedatos?sslmode=require'
   ```
4. Para despliegue en Streamlit Cloud, configura el mismo secreto en la sección de secretos de Streamlit.

## Uso

1. Ejecuta la aplicación con `streamlit run app.py`
2. La aplicación carga automáticamente datos de muestra desde la base de datos
3. Puedes cambiar el modelo de machine learning a utilizar o cargar tu propio archivo CSV con datos
4. Visualiza los resultados de la predicción
5. Si deseas actualizar los datos de muestra, usa el botón "Actualizar datos de muestra"

## Estructura del archivo CSV

El archivo CSV debe contener las siguientes columnas:

- fixed_acidity
- volatile_acidity
- citric_acid
- residual_sugar
- chlorides
- free_sulfur_dioxide
- total_sulfur_dioxide
- density
- ph
- sulphates
- alcohol
