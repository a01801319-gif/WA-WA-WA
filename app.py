import sys
import json
from datetime import datetime

# Parchear requests para entornos Pyodide (Navegador)
if "pyodide" in sys.modules:
    try:
        import pyodide_http
        pyodide_http.patch_all()
    except Exception as e:
        pass

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas y Promociones",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para mejorar el diseño (Glassmorphism, fuentes modernas)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .kpi-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .kpi-container:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .kpi-title {
            font-size: 14px;
            font-weight: 300;
            color: #b0b0b0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 5px;
        }
        
        .kpi-sub {
            font-size: 12px;
            font-weight: 400;
            color: #4caf50; /* Verde para porcentaje o subtexto positivo */
        }
    </style>
""", unsafe_allow_html=True)

# Título y encabezado
st.title("📊 Dashboard Analítico de Ventas y Promociones")
st.markdown("Carga tus archivos de **Ventas** y **Promociones** (CSV o Excel) para visualizar el impacto comercial y obtener insights generados por IA.")

# Variables de estado para los archivos
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = None
if 'promos_data' not in st.session_state:
    st.session_state.promos_data = None

# Sección de Carga de Archivos
col_upload1, col_upload2 = st.columns(2)

with col_upload1:
    st.subheader("1. Base de Datos de Ventas")
    sales_file = st.file_uploader("Sube el archivo de Ventas (Excel/CSV)", type=["csv", "xlsx", "xls"], key="sales")
    
with col_upload2:
    st.subheader("2. Base de Datos de Promociones")
    promos_file = st.file_uploader("Sube el archivo de Promociones (Excel/CSV)", type=["csv", "xlsx", "xls"], key="promos")

# Función para cargar datos de forma robusta
def load_file(file):
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                # Intentar leer con UTF-8, si falla con latin-1
                try:
                    df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file, encoding='latin-1')
            else:
                df = pd.read_excel(file)
            return df
        except Exception as e:
            st.error(f"Error al leer el archivo {file.name}: {e}")
            return None
    return None

# Funciones de auto-detección de columnas
def detect_columns(columns, expected_terms):
    for col in columns:
        col_lower = str(col).lower().strip()
        for term in expected_terms:
            if term in col_lower:
                return col
    return columns[0] if len(columns) > 0 else None

# Cargar archivos en el estado de sesión si se suben
if sales_file:
    st.session_state.sales_data = load_file(sales_file)
if promos_file:
    st.session_state.promos_data = load_file(promos_file)

# Si los datos están cargados, configurar mapeo
if st.session_state.sales_data is not None:
    st.success("✅ Base de datos de Ventas cargada correctamente.")
    
    # Expandible para mapeo de columnas de ventas
    with st.expander("🛠️ Mapeo de Columnas: Ventas", expanded=False):
        cols = list(st.session_state.sales_data.columns)
        
        # Detección automática inteligente
        default_date = detect_columns(cols, ["fecha", "date", "day", "dia"])
        default_sku = detect_columns(cols, ["sku", "cod", "id", "producto", "item"])
        default_dept = detect_columns(cols, ["depto", "departamento", "dept", "category", "categoria"])
        default_subdept = detect_columns(cols, ["subdepto", "subdepartamento", "subdept", "subcategory", "subcategoria"])
        default_rev = detect_columns(cols, ["venta", "ingreso", "revenue", "monto", "total", "sales"])
        default_units = detect_columns(cols, ["unidad", "cantidad", "unit", "quantity", "cant", "unidades"])
        default_profit = detect_columns(cols, ["ganancia", "utilidad", "profit", "margen", "utility"])
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            map_date = st.selectbox("Fecha", cols, index=cols.index(default_date) if default_date in cols else 0)
            map_sku = st.selectbox("SKU / Producto", cols, index=cols.index(default_sku) if default_sku in cols else 0)
        with col_m2:
            map_dept = st.selectbox("Departamento", cols, index=cols.index(default_dept) if default_dept in cols else 0)
            map_subdept = st.selectbox("Subdepartamento", cols, index=cols.index(default_subdept) if default_subdept in cols else 0)
        with col_m3:
            map_rev = st.selectbox("Ingresos / Ventas ($)", cols, index=cols.index(default_rev) if default_rev in cols else 0)
            map_units = st.selectbox("Ventas por Unidades (Cant)", cols, index=cols.index(default_units) if default_units in cols else 0)
            map_profit = st.selectbox("Ganancia ($)", cols, index=cols.index(default_profit) if default_profit in cols else 0)

if st.session_state.promos_data is not None:
    st.success("✅ Base de datos de Promociones cargada correctamente.")
    
    # Expandible para mapeo de columnas de promociones
    with st.expander("🛠️ Mapeo de Columnas: Promociones", expanded=False):
        cols_p = list(st.session_state.promos_data.columns)
        
        # Detección automática inteligente
        default_p_sku = detect_columns(cols_p, ["sku", "cod", "id", "producto", "item"])
        default_p_camp = detect_columns(cols_p, ["campaña", "promocion", "promo", "campaign", "nombre"])
        default_p_start = detect_columns(cols_p, ["inicio", "start", "desde"])
        default_p_end = detect_columns(cols_p, ["fin", "end", "hasta"])
        
        col_mp1, col_mp2 = st.columns(2)
        with col_mp1:
            map_p_sku = st.selectbox("SKU de Promoción", cols_p, index=cols_p.index(default_p_sku) if default_p_sku in cols_p else 0)
            map_p_camp = st.selectbox("Nombre de Campaña/Promo", cols_p, index=cols_p.index(default_p_camp) if default_p_camp in cols_p else 0)
        with col_mp2:
            has_dates = st.checkbox("¿Tiene rango de fechas de validez?", value=True)
            map_p_start = st.selectbox("Fecha Inicio", cols_p, index=cols_p.index(default_p_start) if default_p_start in cols_p else 0, disabled=not has_dates)
            map_p_end = st.selectbox("Fecha Fin", cols_p, index=cols_p.index(default_p_end) if default_p_end in cols_p else 0, disabled=not has_dates)

# Validar y procesar datos solo si la base de ventas está cargada
if st.session_state.sales_data is not None:
    # 1. Copiar y preprocesar base de ventas
    df_sales = st.session_state.sales_data.copy()
    
    try:
        # Limpieza de columnas numéricas (remover $, comas, etc.)
        for col_name in [map_rev, map_units, map_profit]:
            if df_sales[col_name].dtype == 'object':
                df_sales[col_name] = df_sales[col_name].astype(str).str.replace('$', '', regex=False)
                df_sales[col_name] = df_sales[col_name].str.replace(',', '', regex=False)
                df_sales[col_name] = df_sales[col_name].str.strip()
                df_sales[col_name] = pd.to_numeric(df_sales[col_name], errors='coerce')
            else:
                df_sales[col_name] = pd.to_numeric(df_sales[col_name], errors='coerce')
        
        # Convertir fecha a datetime
        df_sales[map_date] = pd.to_datetime(df_sales[map_date], errors='coerce')
        df_sales = df_sales.dropna(subset=[map_date, map_sku])
        
    except Exception as e:
        st.error(f"Error al preprocesar las columnas de ventas: {e}")
        st.stop()

    # 2. Copiar y preprocesar base de promociones si existe
    df_promos = None
    if st.session_state.promos_data is not None:
        df_promos = st.session_state.promos_data.copy()
        try:
            if has_dates:
                df_promos[map_p_start] = pd.to_datetime(df_promos[map_p_start], errors='coerce')
                df_promos[map_p_end] = pd.to_datetime(df_promos[map_p_end], errors='coerce')
                df_promos = df_promos.dropna(subset=[map_p_sku, map_p_start, map_p_end])
            else:
                df_promos = df_promos.dropna(subset=[map_p_sku])
        except Exception as e:
            st.error(f"Error al preprocesar las columnas de promociones: {e}")
            df_promos = None

    # 3. Unir ventas y promociones de manera lógica
    df_merged = df_sales.copy()
    
    if df_promos is not None:
        if has_dates:
            # Unión por SKU y rango de fechas
            # Hacemos una unión por SKU primero
            df_temp = pd.merge(df_sales, df_promos[[map_p_sku, map_p_camp, map_p_start, map_p_end]], 
                               left_on=map_sku, right_on=map_p_sku, how='left')
            
            # Filtrar filas donde la fecha de venta está dentro del rango de la promoción
            in_promo = (df_temp[map_date] >= df_temp[map_p_start]) & (df_temp[map_date] <= df_temp[map_p_end])
            
            # Asignar campaña
            df_temp['Campaña_Final'] = "Sin Promoción"
            df_temp.loc[in_promo, 'Campaña_Final'] = df_temp.loc[in_promo, map_p_camp]
            
            # Para evitar duplicados en caso de solapamientos, nos quedamos con el registro que tiene promoción si existe
            df_temp = df_temp.sort_values(by=['Campaña_Final'], ascending=False)
            df_merged = df_temp.drop_duplicates(subset=[map_date, map_sku, map_dept, map_subdept, map_rev, map_units, map_profit])
            df_merged = df_merged.drop(columns=[map_p_sku, map_p_start, map_p_end, map_p_camp], errors='ignore')
            df_merged = df_merged.rename(columns={'Campaña_Final': 'Campaña'})
        else:
            # Unión simple por SKU
            df_merged = pd.merge(df_sales, df_promos[[map_p_sku, map_p_camp]], 
                                 left_on=map_sku, right_on=map_p_sku, how='left')
            df_merged = df_merged.rename(columns={map_p_camp: 'Campaña'})
            df_merged['Campaña'] = df_merged['Campaña'].fillna("Sin Promoción")
            df_merged = df_merged.drop(columns=[map_p_sku], errors='ignore')
    else:
        df_merged['Campaña'] = "Sin Promoción"

    # --- BARRA LATERAL: CONFIGURACIÓN DE FILTROS ---
    st.sidebar.header("🎯 Filtros del Dashboard")
    
    # 1. Filtro de Departamento
    dept_options = sorted(df_merged[map_dept].dropna().unique())
    selected_depts = st.sidebar.multiselect(
        "Departamento",
        options=dept_options,
        default=[]
    )
    
    # Si no se selecciona ninguno, interpretar como "Todos"
    if not selected_depts:
        df_filtered = df_merged.copy()
        subdept_options = sorted(df_merged[map_subdept].dropna().unique())
    else:
        df_filtered = df_merged[df_merged[map_dept].isin(selected_depts)]
        subdept_options = sorted(df_filtered[map_subdept].dropna().unique())
        
    # 2. Filtro de Subdepartamento (dinámico según el depto seleccionado)
    selected_subdepts = st.sidebar.multiselect(
        "Subdepartamento",
        options=subdept_options,
        default=[]
    )
    
    if selected_subdepts:
        df_filtered = df_filtered[df_filtered[map_subdept].isin(selected_subdepts)]
        
    # 3. Filtro de SKU
    sku_options = sorted(df_filtered[map_sku].dropna().unique())
    selected_skus = st.sidebar.multiselect(
        "SKU",
        options=sku_options,
        default=[]
    )
    
    if selected_skus:
        df_filtered = df_filtered[df_filtered[map_sku].isin(selected_skus)]

    # 4. Rango de Fechas
    min_date = df_filtered[map_date].min()
    max_date = df_filtered[map_date].max()
    
    if pd.notnull(min_date) and pd.notnull(max_date):
        selected_dates = st.sidebar.date_input(
            "Rango de Fechas",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
            df_filtered = df_filtered[(df_filtered[map_date].dt.date >= start_date) & 
                                      (df_filtered[map_date].dt.date <= end_date)]

    # --- BARRA LATERAL: CONFIGURACIÓN DE LLM (Qwen2) ---
    st.sidebar.markdown("---")
    st.sidebar.header("🤖 Configuración Qwen2 LLM")
    
    llm_provider = st.sidebar.selectbox(
        "Proveedor LLM",
        options=["Ollama (Local)", "OpenRouter (Nube)", "Hugging Face (Nube)", "API OpenAI Compatible"],
        index=0
    )
    
    llm_url = "http://localhost:11434"
    llm_key = ""
    llm_model = "qwen2.5"
    
    if llm_provider == "Ollama (Local)":
        llm_url = st.sidebar.text_input("URL de Ollama", value="http://localhost:11434")
        llm_model = st.sidebar.text_input("Modelo Ollama", value="qwen2.5")
        st.sidebar.info("💡 Asegúrate de que Ollama está corriendo en tu máquina con el modelo cargado (`ollama run qwen2.5` o `qwen2`).")
    elif llm_provider == "OpenRouter (Nube)":
        llm_url = "https://openrouter.ai/api/v1"
        llm_key = st.sidebar.text_input("OpenRouter API Key", type="password")
        llm_model = st.sidebar.selectbox("Modelo", options=["qwen/qwen-2.5-72b-instruct", "qwen/qwen-2-7b-instruct:free", "qwen/qwen-2.5-coder-32b-instruct"], index=1)
    elif llm_provider == "Hugging Face (Nube)":
        llm_url = "https://api-inference.huggingface.co/models"
        llm_key = st.sidebar.text_input("Hugging Face API Key / Token", type="password")
        llm_model = st.sidebar.text_input("Modelo HF", value="Qwen/Qwen2.5-72B-Instruct")
    else:
        llm_url = st.sidebar.text_input("URL Base API", value="https://api.openai.com/v1")
        llm_key = st.sidebar.text_input("API Key", type="password")
        llm_model = st.sidebar.text_input("Modelo", value="qwen2")

    # Mostrar advertencia de Mixed Content en GitHub Pages
    is_https = False
    # Detectamos si estamos en https analizando la URL del navegador si es posible, de lo contrario advertimos de forma general
    st.sidebar.markdown(
        """
        > **⚠️ Nota de Despliegue:**
        > Si esta página se ejecuta desde **GitHub Pages (HTTPS)**, el navegador bloqueará solicitudes locales HTTP directas a **Ollama** (`http://localhost:11434`) debido a políticas de seguridad (*Mixed Content*). 
        > **Solución**: Corre la app localmente con `streamlit run app.py` o utiliza un proveedor con HTTPS como **OpenRouter** o **Hugging Face**.
        """
    )

    # --- PANTALLA PRINCIPAL: METRICAS CLAVE (KPIs) ---
    st.subheader("📈 Resumen de Desempeño Comercial")
    
    total_revenue = df_filtered[map_rev].sum()
    total_profit = df_filtered[map_profit].sum()
    total_units = df_filtered[map_units].sum()
    
    # Evitar divisiones por cero
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    avg_ticket = (total_revenue / total_units) if total_units > 0 else 0.0
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
    
    with col_kpi1:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Ingresos Totales</div>
                <div class="kpi-value">${total_revenue:,.2f}</div>
                <div class="kpi-sub" style="color: #4caf50;">Venta Acumulada</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_kpi2:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Ganancia Neta</div>
                <div class="kpi-value">${total_profit:,.2f}</div>
                <div class="kpi-sub" style="color: #4caf50;">Margen Operativo</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_kpi3:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Margen Promedio</div>
                <div class="kpi-value">{profit_margin:.2f}%</div>
                <div class="kpi-sub" style="color: #2196f3;">Ganancias / Ingresos</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_kpi4:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Unidades Vendidas</div>
                <div class="kpi-value">{int(total_units):,}</div>
                <div class="kpi-sub" style="color: #ff9800;">Volumen de Ventas</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_kpi5:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Ticket Promedio</div>
                <div class="kpi-value">${avg_ticket:,.2f}</div>
                <div class="kpi-sub" style="color: #e91e63;">Por Unidad Vendida</div>
            </div>
        """, unsafe_allow_html=True)

    # --- PANTALLA PRINCIPAL: GRÁFICA SOLICITADA (INGRESOS, GANANCIAS Y UNIDADES) ---
    st.markdown("---")
    st.subheader("📊 Comportamiento de Ingresos, Ganancias y Ventas por Unidades")
    st.markdown("Evolución temporal consolidada de los tres indicadores clave. Usa los controles en la gráfica para hacer zoom e interactuar.")
    
    # Agrupar por fecha
    df_temporal = df_filtered.groupby(map_date).agg({
        map_rev: 'sum',
        map_profit: 'sum',
        map_units: 'sum'
    }).sort_index()
    
    if not df_temporal.empty:
        # Crear gráfica Plotly con eje Y secundario
        fig_combined = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Ingresos (Eje Y principal - Barra/Línea)
        fig_combined.add_trace(
            go.Bar(
                x=df_temporal.index,
                y=df_temporal[map_rev],
                name="Ingresos ($)",
                marker_color='#1f77b4',
                opacity=0.7,
                hovertemplate="Fecha: %{x}<br>Ingresos: $%{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        # Ganancias (Eje Y principal - Línea gruesa)
        fig_combined.add_trace(
            go.Scatter(
                x=df_temporal.index,
                y=df_temporal[map_profit],
                name="Ganancias ($)",
                line=dict(color='#2ca02c', width=3),
                mode='lines+markers',
                hovertemplate="Fecha: %{x}<br>Ganancias: $%{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        # Ventas por Unidades (Eje Y secundario - Línea punteada naranja)
        fig_combined.add_trace(
            go.Scatter(
                x=df_temporal.index,
                y=df_temporal[map_units],
                name="Unidades Vendidas",
                line=dict(color='#ff7f0e', width=2, dash='dot'),
                mode='lines+markers',
                hovertemplate="Fecha: %{x}<br>Unidades: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True
        )
        
        # Títulos y formato estético
        fig_combined.update_layout(
            title_text="Desempeño Diario Consolidado",
            title_x=0.5,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title="Fecha"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title="Moneda ($)",
                tickprefix="$"
            ),
            yaxis2=dict(
                title="Unidades",
                showgrid=False,
                overlaying="y",
                side="right"
            )
        )
        
        st.plotly_chart(fig_combined, use_container_width=True)
    else:
        st.warning("No hay datos en el rango de fechas seleccionado para mostrar la gráfica temporal.")

    # --- PANTALLA PRINCIPAL: OTRAS VISUALIZACIONES (TREEMAP E IMPACTO DE PROMOS) ---
    st.markdown("---")
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.subheader("🌲 Estructura de Ventas por Departamento y Subdepartamento")
        st.markdown("Jerarquía de ingresos y ganancias. Haz clic en las categorías para expandir.")
        
        # Treemap
        if not df_filtered.empty:
            fig_tree = px.treemap(
                df_filtered,
                path=[map_dept, map_subdept],
                values=map_rev,
                color=map_profit,
                color_continuous_scale='RdYlGn',
                hover_data=[map_units],
                color_continuous_midpoint=df_filtered[map_profit].mean()
            )
            fig_tree.update_layout(
                margin=dict(t=30, l=10, r=10, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar el Treemap.")
            
    with col_viz2:
        st.subheader("🏷️ Impacto y Desempeño por Campaña Promocional")
        st.markdown("Comparación de ventas promedio diarias por campaña promocional.")
        
        # Calcular ventas e ingresos promedio por día de cada promoción
        if not df_filtered.empty:
            # Agrupar por fecha y campaña para obtener ventas diarias por campaña
            daily_promo = df_filtered.groupby([map_date, 'Campaña']).agg({
                map_rev: 'sum',
                map_profit: 'sum',
                map_units: 'sum'
            }).reset_index()
            
            # Obtener el promedio de venta diario por campaña
            promo_comparison = daily_promo.groupby('Campaña').agg({
                map_rev: 'mean',
                map_profit: 'mean',
                map_units: 'mean'
            }).reset_index()
            
            # Graficar
            fig_promo = go.Figure()
            
            fig_promo.add_trace(go.Bar(
                x=promo_comparison['Campaña'],
                y=promo_comparison[map_rev],
                name="Promedio Ingresos ($)",
                marker_color='#1f77b4',
                hovertemplate="Campaña: %{x}<br>Promedio Diario: $%{y:,.2f}<extra></extra>"
            ))
            
            fig_promo.add_trace(go.Bar(
                x=promo_comparison['Campaña'],
                y=promo_comparison[map_profit],
                name="Promedio Ganancias ($)",
                marker_color='#2ca02c',
                hovertemplate="Campaña: %{x}<br>Promedio Diario: $%{y:,.2f}<extra></extra>"
            ))
            
            fig_promo.update_layout(
                barmode='group',
                margin=dict(t=30, l=10, r=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    title="Campaña"
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    title="Promedio Diario ($)",
                    tickprefix="$"
                )
            )
            
            st.plotly_chart(fig_promo, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar la gráfica de promociones.")

    # --- PANTALLA PRINCIPAL: LLM QWEN2 INSIGHTS GENERATOR ---
    st.markdown("---")
    st.subheader("🧠 Generación de Insights Estratégicos con Qwen2")
    st.markdown("Envía un resumen ejecutivo estructurado de tus datos a Qwen2 para detectar áreas de oportunidad de manera automática.")
    
    # Botón para activar el análisis
    if st.button("🚀 Generar Insights con Qwen2", key="llm_btn"):
        with st.spinner("Qwen2 está analizando tus datos... Por favor espera."):
            
            # Preparar los datos resumen para el prompt
            # Top 3 departamentos
            top_depts = df_filtered.groupby(map_dept).agg({
                map_rev: 'sum',
                map_profit: 'sum'
            }).sort_values(by=map_rev, ascending=False).head(3)
            
            depts_text = ""
            for idx, row in top_depts.iterrows():
                margin = (row[map_profit] / row[map_rev] * 100) if row[map_rev] > 0 else 0
                depts_text += f"- {idx}: Ventas ${row[map_rev]:,.2f}, Ganancia ${row[map_profit]:,.2f} (Margen: {margin:.1f}%)\n"
                
            # Top 3 SKUs
            top_skus = df_filtered.groupby(map_sku).agg({
                map_rev: 'sum',
                map_profit: 'sum',
                map_units: 'sum'
            }).sort_values(by=map_rev, ascending=False).head(3)
            
            skus_text = ""
            for idx, row in top_skus.iterrows():
                skus_text += f"- SKU {idx}: Ventas ${row[map_rev]:,.2f}, Unidades {int(row[map_units]):,}, Ganancia ${row[map_profit]:,.2f}\n"
                
            # Rendimiento de promociones
            promo_res = df_filtered.groupby('Campaña').agg({
                map_rev: ['count', 'sum', 'mean'],
                map_profit: 'sum'
            })
            
            promos_text = ""
            for idx, row in promo_res.iterrows():
                count = row[(map_rev, 'count')]
                rev_sum = row[(map_rev, 'sum')]
                rev_mean = row[(map_rev, 'mean')]
                prof_sum = row[(map_profit, 'sum')]
                margin = (prof_sum / rev_sum * 100) if rev_sum > 0 else 0
                promos_text += f"- Campaña '{idx}': {count} ventas, Ventas Totales ${rev_sum:,.2f}, Venta Diaria Promedio ${rev_mean:,.2f}, Margen Promedio {margin:.1f}%\n"

            # Prompt estructurado
            prompt = f"""Eres Qwen2, un asistente experto en analítica de negocios y retail. Analiza los siguientes datos comerciales e identifica patrones clave, problemas y recomendaciones de mejora.

RESUMEN GENERAL:
- Ingresos Totales: ${total_revenue:,.2f}
- Ganancia Neta: ${total_profit:,.2f}
- Margen de Ganancia Promedio: {profit_margin:.2f}%
- Unidades Vendidas Totales: {int(total_units):,}
- Ticket Promedio: ${avg_ticket:,.2f}

RENDIMIENTO DE TOP DEPARTAMENTOS:
{depts_text}

RENDIMIENTO DE TOP SKUs:
{skus_text}

RENDIMIENTO POR CAMPAÑA PROMOCIONAL:
{promos_text}

Por favor, genera un análisis ejecutivo de estos datos estructurado de la siguiente forma:
1. **Análisis de Rendimiento General**: Breve diagnóstico de la rentabilidad y volumen de ventas actuales.
2. **Impacto Real de las Promociones**: Evalúa si las promociones aumentaron de forma efectiva las ganancias o si afectaron negativamente al margen (canibalización). Identifica cuál fue la mejor campaña.
3. **Análisis de Categorías y SKUs**: Comportamiento de los departamentos y SKUs líderes y cuáles tienen mejor margen.
4. **Recomendaciones Accionables**: 3 consejos estratégicos para optimizar el inventario, los precios o las futuras promociones para maximizar el margen de ganancias.

Escribe el informe en español de manera formal, analítica, concisa y profesional."""

            # Llamada al LLM dependiendo del proveedor seleccionado
            success = False
            response_text = ""
            
            try:
                headers = {"Content-Type": "application/json"}
                
                if llm_provider == "Ollama (Local)":
                    url = f"{llm_url}/api/generate"
                    payload = {
                        "model": llm_model,
                        "prompt": prompt,
                        "stream": False
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    if response.status_code == 200:
                        response_text = response.json().get("response", "")
                        success = True
                    else:
                        response_text = f"Error en Ollama (Código {response.status_code}): {response.text}"
                        
                elif llm_provider == "OpenRouter (Nube)":
                    url = f"{llm_url}/chat/completions"
                    headers["Authorization"] = f"Bearer {llm_key}"
                    headers["HTTP-Referer"] = "https://github.com/stlite"
                    payload = {
                        "model": llm_model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=40)
                    if response.status_code == 200:
                        response_text = response.json()["choices"][0]["message"]["content"]
                        success = True
                    else:
                        response_text = f"Error en OpenRouter (Código {response.status_code}): {response.text}"
                        
                elif llm_provider == "Hugging Face (Nube)":
                    url = f"{llm_url}/{llm_model}"
                    headers["Authorization"] = f"Bearer {llm_key}"
                    payload = {
                        "inputs": prompt,
                        "parameters": {"max_new_tokens": 1000}
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=40)
                    if response.status_code == 200:
                        res_json = response.json()
                        if isinstance(res_json, list) and len(res_json) > 0:
                            response_text = res_json[0].get("generated_text", "")
                            # A veces HF devuelve el prompt original más la respuesta, tratamos de limpiar
                            if response_text.startswith(prompt):
                                response_text = response_text[len(prompt):].strip()
                        else:
                            response_text = str(res_json)
                        success = True
                    else:
                        response_text = f"Error en Hugging Face (Código {response.status_code}): {response.text}"
                        
                else: # OpenAI Compatible
                    url = f"{llm_url}/chat/completions"
                    if llm_key:
                        headers["Authorization"] = f"Bearer {llm_key}"
                    payload = {
                        "model": llm_model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=40)
                    if response.status_code == 200:
                        response_text = response.json()["choices"][0]["message"]["content"]
                        success = True
                    else:
                        response_text = f"Error en API (Código {response.status_code}): {response.text}"
                        
            except Exception as e:
                response_text = f"Ocurrió un error al contactar al LLM: {str(e)}\n\n"
                response_text += "Si estás usando la versión web (HTTPS) y Ollama local (HTTP), recuerda que el navegador bloquea la petición por Mixed Content. Ejecuta la app localmente con `streamlit run app.py` para solucionarlo."
            
            # Mostrar resultados
            st.markdown("---")
            if success:
                st.subheader("💡 Insights y Recomendaciones del Modelo Qwen2")
                st.markdown(response_text)
            else:
                st.error("No se pudo generar insights con el LLM:")
                st.markdown(response_text)

else:
    # Mensaje inicial si no se han cargado datos
    st.info("👋 Por favor, sube al menos el archivo de ventas en la parte superior para comenzar el análisis.")
    
    # Vista previa informativa de la plantilla de datos
    st.markdown("---")
    st.subheader("📋 Estructura Recomendada de Datos")
    
    col_temp1, col_temp2 = st.columns(2)
    with col_temp1:
        st.markdown("""
        **Archivo de Ventas (CSV o Excel):**
        Debe contener información detallada de transacciones. Ejemplo:
        | Fecha | SKU | Departamento | Subdepartamento | Venta | Unidades | Ganancia |
        |---|---|---|---|---|---|---|
        | 2026-03-01 | SKU-LAP-001 | Electrónica | Cómputo | 12000.00 | 1 | 3500.00 |
        | 2026-03-01 | SKU-TEN-010 | Deportes | Calzado | 3600.00 | 2 | 1600.00 |
        """)
    with col_temp2:
        st.markdown("""
        **Archivo de Promociones (CSV o Excel - Opcional):**
        Permite mapear qué productos estaban en campaña. Ejemplo:
        | SKU | Campaña | Fecha Inicio | Fecha Fin | Descuento |
        |---|---|---|---|---|
        | SKU-LAP-001 | Hot Sale | 2026-03-05 | 2026-03-15 | 0.15 |
        | SKU-TEN-010 | Buen Fin | 2026-04-10 | 2026-04-20 | 0.20 |
        """)
