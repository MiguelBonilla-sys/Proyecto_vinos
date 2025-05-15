import streamlit as st
import pandas as pd
import pickle
from PIL import Image
import os
import psycopg2
from dotenv import load_dotenv

# Configuración de la página
st.set_page_config(
    page_title="Predicción de Vinos",
    page_icon="🍷",
    layout="wide"
)

# Función para conectar a base de datos
def init_connection():
    try:
        # Intentar usar los secretos de Streamlit primero
        return psycopg2.connect(st.secrets["postgres"]["url"])
    except KeyError:
        # Si no hay secretos en Streamlit, intentar usar variables de entorno
        try:
            load_dotenv()
            postgres_url = os.getenv('POSTGRES_URL')
            if postgres_url:
                # Eliminar comillas simples o dobles si existen en la URL
                postgres_url = postgres_url.strip("'\"")
                return psycopg2.connect(postgres_url)
            else:
                st.error("No se encontró URL de base de datos en las variables de entorno")
                return None
        except Exception as e:
            st.error(f"Error al cargar desde variables de entorno: {e}")
            return None
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

def run_query(query):
    conn = init_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            st.error(f"Error al ejecutar consulta: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

# Título y descripción
st.title("Predicción de Calidad de Vinos")
st.write("Esta aplicación carga automáticamente datos de muestra desde la base de datos y predice su calidad. También puedes subir tu propio archivo CSV con características de vinos para obtener predicciones personalizadas.")

# Configuración de la barra lateral
try:
    # Intentar diferentes rutas para adaptarse tanto al entorno local como al de Streamlit Cloud
    possible_paths = [
        os.path.join("Images", "vino.png"),
        os.path.join(os.path.dirname(__file__), "Images", "vino.png"),
        "Images/vino.png"
    ]
    
    logo = None
    for path in possible_paths:
        try:
            logo = Image.open(path)
            break
        except Exception:
            continue
    
    if logo:
        st.sidebar.image(logo, width=180)
    else:
        st.sidebar.warning("No se pudo cargar el logo")
except Exception:
    st.sidebar.warning("No se pudo cargar el logo")

st.sidebar.header("Opciones:")
st.sidebar.write("Seleciona una de las siguientes opciones para predecir la calidad de los vinos:")
st.sidebar.markdown("---")  

# Selector de modelo
model_option = st.sidebar.selectbox(
    "Seleccione el modelo de predicción",
    ("Árbol de Decisión", "XGBoost")
)
st.sidebar.markdown("---")  
st.sidebar.info("Desarrollado por CMSJ")

# Define las columnas requeridas (ajusta según tu base de datos, menos 'quality')
required_columns = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar", 
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide", "density", 
    "ph", "sulphates", "alcohol"
]

# Mapeo inverso para mostrar la etiqueta original
quality_map = {
    5: "Excepcional",
    4: "Excelente",
    3: "Muy Bueno",
    2: "Bueno",
    1: "Regular",
    0: "Vino defectuoso"
}

# Función para cargar y procesar datos desde la base de datos
@st.cache_data(ttl=600)  # Caché por 10 minutos
def cargar_datos_bd(limit=1600):
    with st.spinner("Cargando datos de muestra desde la base de datos..."):
        # Cargar datos de ejemplo desde la base de datos
        df = run_query(f"SELECT * FROM vinos LIMIT {limit}")
        if df.empty:
            st.warning("No se pudieron cargar datos de muestra desde la base de datos.")
            return None
        
        # Crear una copia para no modificar el original
        df_procesado = df.copy()
        
        # Guardar columnas especiales antes de procesar
        datos_originales = {}
        if 'id' in df_procesado.columns:
            datos_originales['id'] = df_procesado['id'].copy()
            df_procesado = df_procesado.drop(columns=['id'])
        
        if 'quality' in df_procesado.columns:
            datos_originales['quality'] = df_procesado['quality'].copy()
            df_procesado = df_procesado.drop(columns=['quality'])
            
        return df_procesado, datos_originales

# Cargar automáticamente datos de muestra al inicio
with st.spinner("Inicializando aplicación..."):
    db_data = cargar_datos_bd()
    
    if db_data:
        input_df, datos_originales = db_data
        
        # Seleccionar solo las columnas necesarias para el modelo
        model_input_df = input_df[required_columns].copy()
        
        # Selección del modelo según la opción elegida
        if model_option == "Árbol de Decisión":
            model_filename = 'dt_Classifier_ptap.pkl'
        else:
            model_filename = 'xgb_classfier_ptap.pkl'
        
        with open(model_filename, 'rb') as model_file:
            model = pickle.load(model_file)
        
        # Hacer predicción usando solo las columnas requeridas
        input_df['Calidad_Predicha_Num'] = model.predict(model_input_df)
        input_df['Calidad_Predicha'] = input_df['Calidad_Predicha_Num'].map(quality_map)
        
        # Restaurar columnas originales
        if 'id' in datos_originales:
            input_df.insert(0, 'id', datos_originales['id'])
        if 'quality' in datos_originales:
            input_df['Calidad_Real'] = datos_originales['quality']
        
        # Mostrar resultados
        st.subheader("Resultados de la Predicción (Datos de muestra)")
        display_cols = (['id'] if 'id' in input_df.columns else []) + required_columns + ['Calidad_Predicha']
        if 'Calidad_Real' in input_df.columns:
            display_cols.append('Calidad_Real')
            
        # Usar hide_index=True para ocultar la columna de índice sin nombre
        st.dataframe(input_df[display_cols].style.highlight_max(axis=0), hide_index=True)
        st.subheader("Distribución de la Calidad Predicha")
        st.write(input_df['Calidad_Predicha'].value_counts())

        # Mostrar métrica de accuracy debajo de la distribución
        if model_option == "Árbol de Decisión":
            try:
                with open('dt_metrics.pkl', 'rb') as f:
                    mse_dt = pickle.load(f)
                st.info(f"Precisión del Árbol de Decisión: {mse_dt:.4f}")
            except Exception:
                st.warning("No se pudo cargar la métrica del Árbol de Decisión.")
        else:
            try:
                with open('xgb_metrics.pkl', 'rb') as f:
                    mse_xgb = pickle.load(f)
                st.info(f"Precisión de XGBoost: {mse_xgb:.4f}")
            except Exception:
                st.warning("No se pudo cargar la métrica de XGBoost.")

        # Gráficas de acuerdo al modelo seleccionado y la calidad predicha
        st.subheader("Gráfica de Calidad Predicha vs pH")
        import altair as alt
        if model_option == "Árbol de Decisión":
            chart = alt.Chart(input_df).mark_bar().encode(
                x=alt.X('Calidad_Predicha:N', title='Calidad Predicha'),
                y=alt.Y('ph:Q', aggregate='mean', title='pH Promedio'),
                color=alt.Color('Calidad_Predicha:N', legend=None)
            ).properties(title='pH Promedio por Calidad Predicha (Árbol de Decisión)')
            st.altair_chart(chart, use_container_width=True)
        else:
            chart = alt.Chart(input_df).mark_bar().encode(
                x=alt.X('Calidad_Predicha:N', title='Calidad Predicha'),
                y=alt.Y('alcohol:Q', aggregate='mean', title='Alcohol Promedio'),
                color=alt.Color('Calidad_Predicha:N', legend=None)
            ).properties(title='Alcohol Promedio por Calidad Predicha (XGBoost)')
            st.altair_chart(chart, use_container_width=True)

        # Añadir botón para refrescar datos
        if st.button("Actualizar datos de muestra", help="Carga nuevos datos de muestra desde la base de datos"):
            st.cache_data.clear()
            st.rerun()

        # Graficas deacuerdo al modelo seleccionado y la calidad predicha

