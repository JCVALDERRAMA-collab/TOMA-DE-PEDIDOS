import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
from st_copy_to_clipboard import st_copy_to_clipboard

# --- Configuration for the consecutive number ---
CONSECUTIVE_FILE = 'ultimo_consecutivo.txt'
INITIAL_CONSECUTIVE = 1000

def get_next_consecutive():
    """Reads the last consecutive number from a file, increments it, and saves it back."""
    current_consecutive = INITIAL_CONSECUTIVE
    if os.path.exists(CONSECUTIVE_FILE):
        try:
            with open(CONSECUTIVE_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    current_consecutive = int(content)
                else:
                    st.warning(f"Advertencia: El archivo '{CONSECUTIVE_FILE}' está vacío. Reiniciando consecutivo a {INITIAL_CONSECUTIVE}.")
                    current_consecutive = INITIAL_CONSECUTIVE
        except ValueError:
            st.warning(f"Advertencia: El archivo '{CONSECUTIVE_FILE}' contiene un valor inválido. Reiniciando consecutivo a {INITIAL_CONSECUTIVE}.")
            current_consecutive = INITIAL_CONSECUTIVE
    
    next_consecutive = current_consecutive + 1
    with open(CONSECUTIVE_FILE, 'w') as f:
        f.write(str(next_consecutive))
    
    return next_consecutive

# Initialize the file if it doesn't exist on first run
if not os.path.exists(CONSECUTIVE_FILE):
    with open(CONSECUTIVE_FILE, 'w') as f:
        f.write(str(INITIAL_CONSECUTIVE))

# --- 1. Datos de los productos ---
productos_data = [
    {"COD_PRODUCTO": "DDPHCO0010", "DESCRIPCION": "DERMADIVA CON COLAGENO X 10 UNIDAD / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "DDPHPE0001", "DESCRIPCION": "DERMADIVA CON PEPINO X 10UNIDAD / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "DDPHSR0010", "DESCRIPCION": "DERMADIVA CON ROSAS Y ALOE VERA X 10 UNIDAD / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "DDPHBA0010", "DESCRIPCION": "TOALLA DESMAQUILLANTE DERMADIVA X 10-48 SURTIDA", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN COLAGENO X 30 / CAJA X 24", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN MIXTA X 30 / CAJA X 24 UN", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN PEPINO X 30 / CAJA X 24 U", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "AMARRE TO. DESMAQUILLANTES FACE CLEAN ROSAS Y ALOE VERA X 30 /", "UNIDAD_X_PAQUETE": 30, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "SWPHSA0050", "DESCRIPCION": "TOALLAS HUMEDAS SENIORS WIPES X 50 / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 50, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "FKPHSA0010", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 10 / CAJA X 48", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "FKPHSA0025", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 25 / CAJA X 48 UND", "UNIDAD_X_PAQUETE": 25, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "FTPHSA0040", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 40 / CAJA X 36 UND", "UNIDAD_X_PAQUETE": 40, "UNIDAD_X_CAJA": 36},
    {"COD_PRODUCTO": "FTPHSA0102", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 102 / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 102, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "FTPHSA0105", "DESCRIPCION": "PAÑITOS HÚMEDOS FRESKITOS X 105 / CAJA X 24 UND", "UNIDAD_X_PAQUETE": 105, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "FGPHSA001", "DESCRIPCION": "PAÑITOS HÚMEDOS ED ESPECIAL NEGRO X1", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 480},
    {"COD_PRODUCTO": "FGPHSA0010", "DESCRIPCION": "PAÑITOS HÚMEDOS ED ESPECIAL NEGRO X10", "UNIDAD_X_PAQUETE": 10, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "FGPHSA0015", "DESCRIPCION": "PAÑITOS HÚMEDOS ED ESPECIAL NEGRO X15", "UNIDAD_X_PAQUETE": 15, "UNIDAD_X_CAJA": 30},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 5 KG / BULTO X 4", "UNIDAD_X_PAQUETE": 5, "UNIDAD_X_CAJA": 4},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 2 KG / BULTO X 10", "UNIDAD_X_PAQUETE": 2, "UNIDAD_X_CAJA": 10},
    {"COD_PRODUCTO": "MWHTAO1000", "DESCRIPCION": "DETERGENTE MAXI WASH PLUS X 1 KG / BULTO X 20 UND", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 20},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "DETERGENTE MAXI WASH MULTIUSOS X 1 KG / BULTO X 20 UND", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 20},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "DETERGENTE MAXI WASH MULTIUSOS X 2 KG / BULTO X 10 UND", "UNIDAD_X_PAQUETE": 2, "UNIDAD_X_CAJA": 10},
    {"COD_PRODUCTO": "ANEBMF0300", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT MENTA FRESCA X 300ML / CAJA X 15 UN", "UNIDAD_X_PAQUETE": 300, "UNIDAD_X_CAJA": 15},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT MENTA FRESCA X 500ML / CAJA X 15 UN", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 15},
    {"COD_PRODUCTO": "ANEBYB0300", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT YERBABUENA 300ML / CAJA X 15 UND", "UNIDAD_X_PAQUETE": 300, "UNIDAD_X_CAJA": 15},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "ENJUAGUE BUCAL ACTIVMINT YERBABUENA 500ML / CAJA X 15 UND", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 15},
    {"COD_PRODUCTO": "FKCRLB0012", "DESCRIPCION": "CREMA HUMECTANTE FRESKITOS MANOS Y CUERPO X 800ML / CAJA X 12", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "JABON LIQUIDO AVENA X 1000 ML / CAJA X 16", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},
    {"COD_PRODUCTO": "FKJLFR1000", "DESCRIPCION": "JABON LIQUIDO FRESKITOS FRUTOS ROJOS X 1L / CAJA X 16 UND", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},
    {"COD_PRODUCTO": "FKJLMV1000", "DESCRIPCION": "JABON LIQUIDO FRESKITOS MANZANA VERDE X 1L / CAJA X 16 UND", "UNIDAD_X_PAQUETE": 1000, "UNIDAD_X_CAJA": 16},
    {"COD_PRODUCTO": "FPPNMC050", "DESCRIPCION": "PAÑITOS HUMEDOS FRESKISPETS X 50 / CAJA X 48 UND", "UNIDAD_X_PAQUETE": 50, "UNIDAD_X_CAJA": 48},
    {"COD_PRODUCTO": "FKSHAL0800", "DESCRIPCION": "SHAMPOO FRESKITOS ALOE Y MANZANILLA X 500 ML / CAJA X 24 UND", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "FKSHMA0800", "DESCRIPCION": "SHAMPOO FRESKITOS MANZANILLA X 800 ML / CAJA X 24 UND", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "FKSHMA0800", "DESCRIPCION": "SHAMPOO FRESKITOS MANZANILLA X 800 ML / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "FKSHRM0500", "DESCRIPCION": "SHAMPOO FRESKITOS ROMERO Y FRUTOS DEL BOSQUE X 500 ML / CAJ", "UNIDAD_X_PAQUETE": 500, "UNIDAD_X_CAJA": 24},
    {"COD_PRODUCTO": "FKSHRM0800", "DESCRIPCION": "SHAMPOO FRESKITOS ROMERO Y FRUTOS DEL BOSQUE X 800 ML / CAJ", "UNIDAD_X_PAQUETE": 800, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "JABON FACE CLEAN CARBÓN ACTIVADO 75 GR", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 18},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "JABON BAÑO BARRA CAJA SURTIDA X 75 GR / CAJA X 75 -", "UNIDAD_X_PAQUETE": 75, "UNIDAD_X_CAJA": 75},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "PAÑALES 0 X 18 X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "PAÑALES 1 X 18 X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "PAÑALES ET 2 X 18 X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "PAÑALES ET 3 X 18 X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "PAÑALES ET 4 X 18 X 12", "UNIDAD_X_PAQUETE": 18, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "TOALLAS DE COCINA 80 UNID X 15", "UNIDAD_X_PAQUETE": 80, "UNIDAD_X_CAJA": 15},
    {"COD_PRODUCTO": "HCTHFL0020", "DESCRIPCION": "TOALLAS MULTIUSOS BBQ HYPER CLEAN X 20 / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 20, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "POBOLD7W12", "DESCRIPCION": "BOMBILLO LED POLAR X 7W / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 1, "UNIDAD_X_CAJA": 12},
    {"COD_PRODUCTO": "#N/D", "DESCRIPCION": "BOMBILLO LED POLAR X 9W / CAJA X 12 UND", "UNIDAD_X_PAQUETE": 9, "UNIDAD_X_CAJA": 12},
]

df_productos = pd.DataFrame(productos_data)
descripciones_productos = df_productos['DESCRIPCION'].tolist()

# Use Streamlit's session state to store variables that need to persist across reruns
if 'pedido_actual' not in st.session_state:
    st.session_state.pedido_actual = []
if 'global_summary_core_text' not in st.session_state:
    st.session_state.global_summary_core_text = ""
if 'show_generated_summary' not in st.session_state:
    st.session_state.show_generated_summary = False


# --- Validation functions for email and phone ---
def is_valid_email(email):
    """Basic email validation."""
    if not email: # Allow empty email
        return True
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_valid_phone(phone):
    """Basic phone validation (allows for optional leading + and spaces/hyphens)."""
    if not phone: # Allow empty phone
        return True
    # Ensures at least 7 digits, allows + at start, and spaces/hyphens in between
    return re.match(r"^\+?[\d\s\-]{7,15}$", phone)

# --- Streamlit UI ---
st.set_page_config(layout="centered", page_title="Generador de Pedidos")

# --- Sección para el logo ---
try:
    st.image("LOGO 2.png", width=200) 
except FileNotFoundError:
    st.warning("⚠️ No se encontró el logo. Asegúrate de que 'LOGO 2.png' esté en la misma carpeta o la ruta sea correcta.")

st.title("📝 Generador de Pedidos")
st.markdown("Completa los detalles para generar un resumen de tu solicitud.")

st.write("---")

st.subheader("Datos del Cliente")
nit = st.text_input("NIT:", value='222222222', disabled=True)
nombre_cliente = st.text_input("Cliente:", value='CONSUMIDOR FINAL', disabled=True)

st.write("---")

st.subheader("Selección de Productos")

selected_description = st.selectbox(
    'Selecciona un producto:',
    options=[""] + descripciones_productos,
    index=0,
    help="Empieza a escribir o selecciona un producto de la lista."
)

producto_encontrado = None
if selected_description and selected_description != "":
    df_filtered = df_productos[df_productos['DESCRIPCION'] == selected_description]
    if not df_filtered.empty:
        producto_encontrado = df_filtered.iloc[0]
    else:
        st.error("Producto no válido o no encontrado. Por favor, selecciona de la lista.")

col1, col2 = st.columns(2)

with col1:
    cantidad_cajas = st.number_input(
        "Cantidad de Cajas:",
        min_value=0,
        value=0,
        step=1,
        disabled=(producto_encontrado is None)
    )

with col2:
    cantidad_unidades = st.number_input(
        "Cantidad de Unidades Individuales:",
        min_value=0,
        value=0,
        step=1,
        disabled=(producto_encontrado is None)
    )

if st.button('Añadir Producto al Pedido', type="primary", disabled=(producto_encontrado is None or (cantidad_cajas == 0 and cantidad_unidades == 0))):
    if not selected_description or (cantidad_cajas == 0 and cantidad_unidades == 0):
        st.error("❌ Error: Selecciona un producto e ingresa al menos una cantidad (caja o unidad).")
    else:
        st.session_state.pedido_actual.append({
            "COD_PRODUCTO": producto_encontrado['COD_PRODUCTO'],
            "DESCRIPCION": selected_description,
            "CANT_CAJAS": cantidad_cajas,
            "CANT_UNIDADES_IND": cantidad_unidades,
            "UNIDAD_X_CAJA": producto_encontrado['UNIDAD_X_CAJA'],
            "UNIDAD_X_PAQUETE": producto_encontrado['UNIDAD_X_PAQUETE']
        })
        st.success(f"Producto '{selected_description}' añadido al pedido.")
        # Clear the summary and hide it when a new product is added
        st.session_state.global_summary_core_text = ""
        st.session_state.show_generated_summary = False # Hide the summary


st.write("---")

st.subheader("Productos en el Pedido")
if st.session_state.pedido_actual:
    for i, item in enumerate(st.session_state.pedido_actual):
        total_unidades_item = (item['CANT_CAJAS'] * item['UNIDAD_X_CAJA']) + item['CANT_UNIDADES_IND']
        st.markdown(f"**{i+1}.** {item['DESCRIPCION']} - Cajas: {item['CANT_CAJAS']}, Unidades: {item['CANT_UNIDADES_IND']} (Total: {total_unidades_item} uds)")
else:
    st.info("No hay productos añadidos al pedido aún.")

st.write("---")

st.subheader("Información de Contacto Adicional")
cliente_email = st.text_input("Email Cliente:", value=st.session_state.get('cliente_email', ''), placeholder='ejemplo@dominio.com', key='email_input')
cliente_telefono = st.text_input("Teléfono Cliente:", value=st.session_state.get('cliente_telefono', ''), placeholder='Ej: 3001234567', key='phone_input')

# Store inputs in session state to persist them across reruns
st.session_state.cliente_email = cliente_email
st.session_state.cliente_telefono = cliente_telefono

st.write("---")

# Conditional button display and summary generation
if not st.session_state.show_generated_summary: # If summary is not currently being shown
    if st.button('Generar Resumen Final', type="secondary"):
        if not st.session_state.pedido_actual:
            st.warning("No hay productos en el pedido para generar un resumen.")
        else:
            email_valid = is_valid_email(cliente_email)
            phone_valid = is_valid_phone(cliente_telefono)

            if not email_valid:
                st.error("❌ Error: Formato de email inválido. Por favor, corrígelo antes de generar el resumen.")
            elif not phone_valid:
                st.error("❌ Error: Formato de teléfono inválido. Por favor, corrígelo antes de generar el resumen.")
            else:
                consecutivo = get_next_consecutive()
                
                summary_core = ""
                summary_core += "--- Resumen General de la Solicitud ---\n"
                summary_core += f"Número de Pedido: {consecutivo}\n"
                summary_core += f"Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                summary_core += f"NIT: {nit}\n"
                summary_core += f"Cliente: {nombre_cliente}\n"
                
                if cliente_email:
                    summary_core += f"Email Cliente: {cliente_email}\n"
                if cliente_telefono:
                    summary_core += f"Teléfono Cliente: {cliente_telefono}\n"

                summary_core += "\n--- Detalles de los Productos Pedidos ---\n"

                for i, item in enumerate(st.session_state.pedido_actual):
                    total_unidades_item = (item['CANT_CAJAS'] * item['UNIDAD_X_CAJA']) + item['CANT_UNIDADES_IND']
                    summary_core += f"\nProducto {i+1}:\n"
                    summary_core += f"  Código: {item['COD_PRODUCTO']}\n"
                    summary_core += f"  Descripción: {item['DESCRIPCION']}\n"
                    summary_core += f"  Cant. Cajas: {item['CANT_CAJAS']}\n"
                    summary_core += f"  Cant. Unidades Individuales: {item['CANT_UNIDADES_IND']}\n"
                    summary_core += f"  Unidades por Caja (del producto): {item['UNIDAD_X_CAJA']}\n"
                    summary_core += f"  Total Unidades Calculadas: {total_unidades_item}\n"
                
                summary_core += "\n-------------------------------------\n"
                summary_core += "Resumen de la solicitud finalizado."
                
                st.session_state.global_summary_core_text = summary_core
                st.session_state.show_generated_summary = True # Now set to True to display summary

    # Display the summary and "Copiar Información" button if show_generated_summary is True
    if st.session_state.show_generated_summary:
        st.write("---")
        st.subheader("Resumen Generado") 
        st.code(st.session_state.global_summary_core_text)

    st.write("---")
    if st.button("Copiar Información"):
        st_copy_to_clipboard(st.code)
        st.success("¡Mensaje copiado al portapapeles! Ya puedes pegarlo donde necesites.")
