import streamlit as st
import pandas as pd
import os

# --- Configuración de página ---
st.set_page_config(page_title="Inventario CON pYTHON", layout="wide")
st.title(" Sistema de Inventario")

# --- Archivo CSV base ---
archivo = "inventario.csv"

# Crear archivo si no existe
if not os.path.exists(archivo):
    df = pd.DataFrame(columns=["ID", "Producto", "Cantidad", "Precio"])
    df.to_csv(archivo, index=False)
else:
    df = pd.read_csv(archivo)

# --- Estado inicial ---
if "fila_seleccionada" not in st.session_state:
    st.session_state.fila_seleccionada = None
if "fila_index" not in st.session_state:
    st.session_state.fila_index = None

# --- Mostrar tabla ---
st.subheader(" Inventario actual")
st.dataframe(df, use_container_width=True)

# --- Seleccionar fila ---
if len(df) > 0:
    fila_index = st.number_input(
        "Selecciona el número de fila a editar (por índice)",
        min_value=0,
        max_value=len(df) - 1,
        step=1,
        value=st.session_state.fila_index if st.session_state.fila_index is not None else 0,
    )

    if st.button(" Cargar datos en formulario"):
        fila = df.iloc[fila_index]
        st.session_state.fila_seleccionada = fila.to_dict()
        st.session_state.fila_index = fila_index
        st.success(f"Fila {fila_index} cargada para edición.")
else:
    st.info("📭No hay datos aún en el inventario.")

# --- Formulario ---
st.subheader("Formulario de producto")

with st.form("form_producto"):
    if st.session_state.fila_seleccionada:
        producto = st.text_input("Producto", st.session_state.fila_seleccionada["Producto"])
        cantidad = st.number_input("Cantidad", min_value=0, value=int(st.session_state.fila_seleccionada["Cantidad"]))
        precio = st.number_input("Precio", min_value=0.0, value=float(st.session_state.fila_seleccionada["Precio"]))
        id_actual = st.session_state.fila_seleccionada["ID"]
        st.text_input("ID (automático)", id_actual, disabled=True)
    else:
        producto = st.text_input("Producto")
        cantidad = st.number_input("Cantidad", min_value=0, step=1)
        precio = st.number_input("Precio", min_value=0.0, step=0.01)

    col1, col2 = st.columns(2)
    guardar = col1.form_submit_button(" Guardar / Actualizar")
    limpiar = col2.form_submit_button(" Limpiar formulario")

# --- Guardar cambios ---
if guardar:
    if producto:
        # Si hay productos previos, obtener el siguiente ID automáticamente
        if len(df) > 0:
            nuevo_id = int(df["ID"].max()) + 1
        else:
            nuevo_id = 1

        nuevo_dato = pd.DataFrame([{
            "ID": nuevo_id,
            "Producto": producto,
            "Cantidad": cantidad,
            "Precio": precio
        }])

        # Si se está editando, mantener el ID original y reemplazar fila
        if st.session_state.fila_seleccionada:
            df.loc[st.session_state.fila_index, ["Producto", "Cantidad", "Precio"]] = [
                producto, cantidad, precio
            ]
            st.success(f" Producto ID {id_actual} actualizado correctamente.")
            st.session_state.fila_seleccionada = None
            st.session_state.fila_index = None
        else:
            # Agregar nuevo registro con ID automático
            df = pd.concat([df, nuevo_dato], ignore_index=True)
            st.success(f" Producto agregado {nuevo_id}.")

        df.to_csv(archivo, index=False)
    else:
        st.warning(" completa el nombre del producto.")

# --- Limpiar formulario ---
if limpiar:
    st.session_state.fila_seleccionada = None
    st.session_state.fila_index = None
    st.info("Formulario limpiado.")
