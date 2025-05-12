import streamlit as st
import pandas as pd
import pickle
from PIL import Image
import os

# Configuración de la página
st.set_page_config(
    page_title="Predicción de Vinos",
    page_icon="🍷",
    layout="wide"
)

# Título y descripción
st.title("Predicción de Calidad de Vinos")
st.write("Sube un archivo CSV con las características del vino para predecir su calidad.")

# Configuración de la barra lateral
try:
    logo = Image.open(os.path.join("Images", "logo_usb.png"))
    st.sidebar.image(logo)
except Exception:
    st.sidebar.warning("No se pudo cargar el logo")

st.sidebar.header("Cargue un archivo CSV con las variables")
st.sidebar.write("El archivo debe contener las columnas requeridas para el modelo.")

# Selector de modelo
model_option = st.sidebar.selectbox(
    "Seleccione el modelo de predicción",
    ("Árbol de Decisión", "XGBoost")
)

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

# Carga y procesamiento del archivo
uploaded_file = st.sidebar.file_uploader("Cargar archivo", type=["csv"])
if uploaded_file is not None:
    try:
        input_df = pd.read_csv(uploaded_file, sep=";")
        # Renombrar columnas para que coincidan con el modelo entrenado
        rename_dict = {
            "fixed acidity": "fixed_acidity",
            "volatile acidity": "volatile_acidity",
            "citric acid": "citric_acid",
            "residual sugar": "residual_sugar",
            "free sulfur dioxide": "free_sulfur_dioxide",
            "total sulfur dioxide": "total_sulfur_dioxide",
            "pH": "ph"
        }
        input_df = input_df.rename(columns=rename_dict)
        # Conversión de columnas numéricas a float (reemplaza ',' por '.')
        for col in required_columns:
            input_df[col] = (
                input_df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )
        # Crear un DataFrame solo con las columnas requeridas para el modelo, excluyendo explícitamente 'id'
        if 'id' in input_df.columns:
            id_column = input_df['id'].copy()  # Guardar id para mostrarlo después
            input_df = input_df.drop(columns=['id'])
        
        model_input_df = input_df[required_columns].copy()
        
        if all(col in model_input_df.columns for col in required_columns):
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
            
            # Restaurar columna id si existía
            if 'id' in locals():
                input_df.insert(0, 'id', id_column)

            st.subheader("Resultados de la Predicción")
            # Mostrar id si existe
            display_cols = (['id'] if 'id' in input_df.columns else []) + required_columns + ['Calidad_Predicha']
            st.dataframe(input_df[display_cols].style.highlight_max(axis=0))
            st.subheader("Distribución de la Calidad Predicha")
            st.write(input_df['Calidad_Predicha'].value_counts())
        else:
            st.error(f"El archivo CSV debe contener las columnas: {', '.join(required_columns)}")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.info("Desarrollado por USB")
