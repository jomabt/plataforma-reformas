import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA - SOFTWARE TÉCNICO Y PRESUPUESTADOR SAAS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PRO-REFORMAS | Gestor Técnico & Presupuestador",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (PALETA OFICIAL Y TOTAL VISIBILIDAD DE CONTROLES)
# - Azul Profundo: #0F2C59 (Fondo Sidebar / Cabeceras)
# - Azul Eléctrico: #007BFF (Subtítulos / Enlaces / Bordes)
# - Amarillo Energía: #FFC107 (Botones CTA / Botones + y - / Bordes Highlight)
# - Gris Oscuro: #212529 (Textos y Etiquetas)
# - Blanco Fondo: #F8F9FA (Fondo General de Aplicación)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. FONDO GENERAL Y TIPOGRAFÍA DE LA APLICACIÓN */
    .stApp {
        background-color: #F8F9FA !important;
        color: #212529 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* 2. ENCABEZADO PRINCIPAL (AZUL PROFUNDO Y AMARILLO ENERGÍA) */
    .header-main {
        background: linear-gradient(135deg, #0F2C59 0%, #1A3E75 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 1.8rem;
        border-left: 10px solid #FFC107;
        box-shadow: 0 6px 15px rgba(15, 44, 89, 0.15);
    }
    .header-title {
        font-size: 2.3rem !important; /* Aumentado 2 puntos */
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #007BFF !important;
        font-size: 1.15rem !important; /* Aumentado 2 puntos */
        font-weight: 600 !important;
        margin-top: 0.4rem;
    }
    .header-badge {
        background-color: #FFC107;
        color: #212529 !important;
        padding: 0.4rem 1.0rem;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.95rem !important;
        display: inline-block;
        margin-top: 0.8rem;
    }

    /* 3. TÍTULOS Y SUBTÍTULOS DE SECCIÓN (+2 PUNTOS) */
    h1, .stMarkdown h1 {
        font-size: 2.3rem !important;
        color: #0F2C59 !important;
        font-weight: 800 !important;
    }
    h2, .stMarkdown h2 {
        font-size: 1.8rem !important;
        color: #0F2C59 !important;
        font-weight: 800 !important;
    }
    h3, .stMarkdown h3 {
        font-size: 1.5rem !important;
        color: #007BFF !important;
        font-weight: 700 !important;
    }
    h4, .stMarkdown h4 {
        font-size: 1.3rem !important;
        color: #0F2C59 !important;
        font-weight: 700 !important;
    }

    /* 4. BARRA LATERAL / MENÚ IZQUIERDO (AZUL PROFUNDO) */
    section[data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
        border-right: 2px solid #007BFF !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #FFC107 !important;
        font-weight: 800 !important;
    }

    /* 5. FIX RIGUROSO: BORDES Y CUADROS BLANCOS PARA CLIENTE, DIRECCIÓN Y TIPO DE IVA EN MENÚ IZQUIERDO */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[role="combobox"] {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 2px solid #FFC107 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
    }
    section[data-testid="stSidebar"] input::placeholder {
        color: #6C757D !important;
    }
    /* Iconos SVG dentro de los selectboxes de la barra lateral */
    section[data-testid="stSidebar"] svg {
        fill: #212529 !important;
        color: #212529 !important;
    }
    /* Etiquetas del Menú Izquierdo */
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }

    /* 6. FIX GLOBAL: TODOS LOS INPUTS Y SELECTBOXES DE LAS SECCIONES PRINCIPALES (SECCIÓN 2, 3, 4, ETC.) */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[role="combobox"],
    input[type="text"],
    input[type="number"],
    .stNumberInput input,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 2px solid #007BFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.0rem !important;
    }

    /* Opciones desplegables de Selectbox (Popovers/Listbox) */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        font-weight: 600 !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #FFC107 !important;
        color: #212529 !important;
    }

    /* 7. BOTONES DE MÁS Y MENOS (+ / -) EN AMARILLO ENERGÍA CON TEXTO NEGRO */
    div[data-testid="stNumberInputContainer"] button,
    button[aria-label="Increase count"],
    button[aria-label="Decrease count"],
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"] {
        background-color: #FFC107 !important;
        color: #212529 !important;
        border: 1px solid #0F2C59 !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        border-radius: 6px !important;
    }
    div[data-testid="stNumberInputContainer"] button:hover {
        background-color: #E0A800 !important;
        color: #212529 !important;
    }

    /* 8. BOTONES CTA PRINCIPALES (AMARILLO ENERGÍA CON HOVER AZUL PROFUNDO) */
    .stButton>button {
        background-color: #FFC107 !important;
        color: #212529 !important;
        font-weight: 800 !important;
        border: 2px solid #0F2C59 !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.2rem !important;
        width: 100% !important;
        font-size: 1.05rem !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #0F2C59 !important;
        color: #FFFFFF !important;
        border-color: #FFC107 !important;
    }

    /* 9. TARJETAS Y CONTENEDORES DE SECCIÓN Y PRODUCTOS */
    .card-product {
        background-color: #FFFFFF !important;
        border: 2px solid #007BFF !important;
        border-top: 6px solid #0F2C59 !important;
        border-radius: 10px !important;
        padding: 1.3rem !important;
        margin-bottom: 1.0rem !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important;
    }
    .card-title {
        color: #0F2C59 !important;
        font-size: 1.25rem !important; /* +2pt */
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    .card-desc {
        color: #212529 !important;
        font-size: 0.95rem !important;
        line-height: 1.45 !important;
        margin-bottom: 0.8rem !important;
        min-height: 48px;
    }

    /* 10. TARJETAS DE MÉTRICAS Y TABLAS DE PRESUPUESTO (SECCIÓN 4) */
    div[data-testid="metric-container"],
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricLabel"] {
        background-color: #FFFFFF !important;
        border: 2px solid #007BFF !important;
        border-radius: 10px !important;
        padding: 0.8rem !important;
        color: #0F2C59 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important; /* +2pt */
        font-weight: 800 !important;
        color: #0F2C59 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.05rem !important; /* +2pt */
        font-weight: 700 !important;
        color: #007BFF !important;
    }

    /* Dataframes y Tablas en blanco y legibles */
    .stDataFrame, div[data-testid="stTable"] {
        background-color: #FFFFFF !important;
        border: 2px solid #007BFF !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INICIALIZACIÓN DE ESTADO DE SESIÓN (PERSISTENCIA DE DATOS)
# -----------------------------------------------------------------------------
if 'cesta' not in st.session_state: st.session_state.cesta = {}
if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 0.0

# Cantidad de estancias (Paso 1)
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 0
if 'n_salones' not in st.session_state: st.session_state.n_salones = 0
if 'n_banos' not in st.session_state: st.session_state.n_banos = 0
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 0
if 'n_galerias' not in st.session_state: st.session_state.n_galerias = 0
if 'n_terrazas' not in st.session_state: st.session_state.n_terrazas = 0
if 'n_trasteros' not in st.session_state: st.session_state.n_trasteros = 0

# Estado de Navegación por Pasos (1 al 5)
if 'paso_actual' not in st.session_state: st.session_state.paso_actual = 1

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL DE LA PLATAFORMA
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-main">
    <div class="header-title">⚡ PRO-REFORMAS | Software de Cálculo & Presupuestos</div>
    <div class="header-subtitle">Plataforma SaaS para Dimensionado Normativo (REBT, CTE DB-HS, RITE, ICT2) y Gestión de Obras</div>
    <div class="header-badge">EDICIÓN TÉCNICA PROFESIONAL 2026</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA SUPERIOR DE NAVEGACIÓN PASO A PASO
# -----------------------------------------------------------------------------
col_n1, col_n2, col_n3, col_n4, col_n5 = st.columns(5)

with col_n1:
    if st.button("📋 1. Estancias", key="btn_p1"):
        st.session_state.paso_actual = 1
        st.rerun()

with col_n2:
    if st.button("🛠️ 2. Cálculos", key="btn_p2"):
        st.session_state.paso_actual = 2
        st.rerun()

with col_n3:
    if st.button("💶 3. Tarifas (€0)", key="btn_p3"):
        st.session_state.paso_actual = 3
        st.rerun()

with col_n4:
    if st.button("📊 4. Presupuesto", key="btn_p4"):
        st.session_state.paso_actual = 4
        st.rerun()

with col_n5:
    if st.button("📚 5. Biblioteca", key="btn_p5"):
        st.session_state.paso_actual = 5
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENÚ IZQUIERDO) - DATOS DEL CLIENTE Y RESUMEN FINANCIERO
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 👤 Datos del Cliente y Obra")

st.session_state.cliente_nombre = st.sidebar.text_input(
    "📌 Nombre del Cliente / Empresa:", 
    value=st.session_state.cliente_nombre, 
    placeholder="Ej. Juan Pérez / D. Antonio López"
)

st.session_state.cliente_obra = st.sidebar.text_input(
    "📍 Dirección / Ubicación de la Obra:", 
    value=st.session_state.cliente_obra, 
    placeholder="Ej. Av. Constitución 45, Castelldefels"
)

tipo_iva = st.sidebar.selectbox(
    "Tipo de IVA Aplicable:",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Partidas en Presupuesto")

if not st.session_state.cesta:
    st.sidebar.info("El presupuesto está vacío. Añade partidas o configura precios en las secciones del programa.")
else:
    subtotal_cesta = 0.0
    for item_id, datos in list(st.session_state.cesta.items()):
        cant = datos['cantidad']
        pu = datos['precio_unitario']
        imp = cant * pu
        subtotal_cesta += imp
        
        st.sidebar.markdown(f"**{datos['nombre']}**")
        st.sidebar.caption(f"Cant: **{cant:.1f} {datos['unidad']}** | PU: **{pu:.2f} €** | Importe: **{imp:.2f} €**")
        if st.sidebar.button(f"🗑️ Eliminar", key=f"del_{item_id}"):
            del st.session_state.cesta[item_id]
            st.rerun()
        st.sidebar.markdown("---")
    
    iva_calc = subtotal_cesta * (tipo_iva / 100)
    total_calc = subtotal_cesta + iva_calc
    
    st.sidebar.metric("Subtotal Base", f"{subtotal_cesta:,.2f} €")
    st.sidebar.metric(f"IVA ({tipo_iva}%)", f"{iva_calc:,.2f} €")
    st.sidebar.metric("TOTAL PRESUPUESTO", f"{total_calc:,.2f} €")
    
    if st.sidebar.button("🧹 Limpiar Presupuesto", key="btn_vaciar_side"):
        st.session_state.cesta = {}
        st.rerun()

# -----------------------------------------------------------------------------
# NAVEGACIÓN 1: ESTANCIAS Y ALCANCE DE LA REFORMA
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == 1:
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría del Inmueble")
    st.write("Indica la cantidad de estancias y la superficie para calcular automáticamente los puntos normativos recomendados.")

    st.session_state.superficie = st.number_input(
        "📐 Superficie Útil Afectada (m²):", 
        min_value=0.0, 
        value=st.session_state.superficie, 
        step=5.0
    )

    st.markdown("#### 🏠 Distribución de Zonas y Estancias:")
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)

    with col_e1:
        st.session_state.n_dormitorios = st.number_input("🛌 Dormitorios", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_salones = st.number_input("🛋️ Salones / Comedores", min_value=0, value=st.session_state.n_salones, step=1)

    with col_e2:
        st.session_state.n_banos = st.number_input("🛁 Baños Completos", min_value=0, value=st.session_state.n_banos, step=1)
        st.session_state.n_aseos = st.number_input("🧻 Aseos (Sin Ducha)", min_value=0, value=st.session_state.n_aseos, step=1)

    with col_e3:
        st.session_state.n_cocinas = st.number_input("🍳 Cocinas", min_value=0, value=st.session_state.n_cocinas, step=1)
        st.session_state.n_galerias = st.number_input("🧺 Galerías / Lavaderos", min_value=0, value=st.session_state.n_galerias, step=1)

    with col_e4:
        st.session_state.n_terrazas = st.number_input("🌿 Terrazas / Balcones", min_value=0, value=st.session_state.n_terrazas, step=1)
        st.session_state.n_trasteros = st.number_input("📦 Trasteros / Garaje / Otros", min_value=0, value=st.session_state.n_trasteros, step=1)

    estancias_totales = (st.session_state.n_dormitorios + st.session_state.n_salones + 
                         st.session_state.n_banos + st.session_state.n_aseos + 
                         st.session_state.n_cocinas + st.session_state.n_galerias + 
                         st.session_state.n_terrazas + st.session_state.n_trasteros)

    st.info(f"💡 **Resumen Inmueble:** {estancias_totales} estancias/zonas configuradas | **Superficie:** {st.session_state.superficie:.1f} m².")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([3, 1])
    with col_nav_b2:
        if st.button("Siguiente: 🛠️ Cálculos Normativos ➔", key="btn_sig_1"):
            st.session_state.paso_actual = 2
            st.rerun()

# -----------------------------------------------------------------------------
# NAVEGACIÓN 2: CÁLCULOS NORMATIVOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 2:
    st.subheader("🛠️ Paso 2: Dimensionado Técnico de Instalaciones")
    st.write("Motores de cálculo según reglamentos oficiales en España (REBT, CTE DB-HS, RITE, ICT2).")

    with st.expander("⚡ **1. Cálculo Electrotécnico (REBT - RD 842/2002)**", expanded=True):
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            electrificacion = st.selectbox("Nivel de Electrificación", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
            potencia_kw = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
        with col_calc2:
            longitud_m = st.number_input("Longitud Derivación Individual (m)", min_value=1.0, value=15.0, step=1.0)
            I_calc = (potencia_kw * 1000) / (230 * 0.9)
            cd_max = 230 * 0.015
            s_min = (2 * longitud_m * (potencia_kw * 1000)) / (56 * cd_max * 230)
            s_rec = max(6.0, s_min)
            st.success(f"✔️ **Intensidad de Cálculo:** {I_calc:.2f} A | **Sección Mínima DI:** {s_rec:.2f} mm² (Cobre)")

    with st.expander("🚰 **2. Suministro de Agua y Desagües (CTE DB-HS4 / DB-HS5)**", expanded=True):
        n_puntos = (st.session_state.n_banos * 3) + (st.session_state.n_aseos * 2) + (st.session_state.n_cocinas * 3) + (st.session_state.n_galerias * 2)
        if n_puntos > 0:
            caudal_instalado = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40) + (st.session_state.n_galerias * 0.20)
            coef_simult = 1 / math.sqrt(max(1, n_puntos))
            caudal_diseno = caudal_instalado * coef_simult
            c1, c2 = st.columns(2)
            c1.metric("Caudal Total Instalado", f"{caudal_instalado:.2f} L/s")
            c2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
        else:
            st.info("Configura baños o cocinas en el Paso 1 para calcular caudales de agua.")

    with st.expander("❄️ **3. Carga Térmica y Climatización (RITE - RD 1027/2007)**", expanded=True):
        if st.session_state.superficie > 0:
            zona = st.selectbox("Calidad Térmica / Aislamiento Inmueble", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_kw = (st.session_state.superficie * w_m2) / 1000
            frig = p_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie en el Paso 1 para estimar la potencia térmica.")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([1, 1])
    with col_nav_b1:
        if st.button("⬅️ Atrás: 📋 Estancias", key="btn_ant_2"):
            st.session_state.paso_actual = 1
            st.rerun()
    with col_nav_b2:
        if st.button("Siguiente: 💶 Cuadro de Tarifas (€0) ➔", key="btn_sig_2"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# NAVEGACIÓN 3: CUADRO DE PRECIOS Y TARIFACIÓN (€0 DE INICIO)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 3:
    st.subheader("💶 Paso 3: Configuración del Cuadro de Precios Unitarios")
    st.write("⚠️ **Todas las partidas inician en 0.00 €.** Introduce tus precios pactados o ajusta cantidades antes de añadir al presupuesto.")

    # Base de datos de catálogo
    if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
    if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
    if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
    if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("#### ⚡ 1. Electricidad y Telecomunicaciones")
        pu_elec = st.number_input("Instalación Eléctrica General (€/m²)", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0)
        cant_elec = st.number_input("Superficie Eléctrica (m²)", min_value=0.0, value=st.session_state.superficie, step=5.0)
        if st.button("🛒 Añadir Electricidad al Presupuesto", key="btn_add_elec"):
            st.session_state.cesta['elec_gen'] = {"nombre": "⚡ Instalación Eléctrica General (REBT)", "unidad": "m²", "cantidad": cant_elec, "precio_unitario": pu_elec}
            st.success("Añadido al presupuesto activo.")
            st.rerun()

        st.markdown("#### 🚰 2. Fontanería y Saneamiento")
        pu_font = st.number_input("Instalación Fontanería Baño (€/baño)", min_value=0.0, value=st.session_state.pu_font_bano, step=25.0)
        cant_font = st.number_input("Cantidad de Baños (ud)", min_value=0.0, value=float(st.session_state.n_banos + st.session_state.n_aseos), step=1.0)
        if st.button("🛒 Añadir Fontanería al Presupuesto", key="btn_add_font"):
            st.session_state.cesta['font_bano'] = {"nombre": "🚰 Instalación Fontanería en Baños (CTE)", "unidad": "baño", "cantidad": cant_font, "precio_unitario": pu_font}
            st.success("Añadido al presupuesto activo.")
            st.rerun()

    with col_t2:
        st.markdown("#### ❄️ 3. Climatización RITE")
        pu_clima = st.number_input("Climatización e Instalación (€/kW)", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0)
        cant_clima = st.number_input("Potencia a Instalar (kW)", min_value=0.0, value=round((st.session_state.superficie * 100)/1000, 1) if st.session_state.superficie > 0 else 0.0, step=0.5)
        if st.button("🛒 Añadir Climatización al Presupuesto", key="btn_add_clima"):
            st.session_state.cesta['clima_kw'] = {"nombre": "❄️ Equipo y Red Climatización (RITE)", "unidad": "kW", "cantidad": cant_clima, "precio_unitario": pu_clima}
            st.success("Añadido al presupuesto activo.")
            st.rerun()

        st.markdown("#### 🏗️ 4. Albañilería Auxiliar")
        pu_albanil = st.number_input("Rozas, Ayuda y Remates (€/m²)", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0)
        cant_albanil = st.number_input("Superficie Albañilería (m²)", min_value=0.0, value=st.session_state.superficie, step=5.0)
        if st.button("🛒 Añadir Albañilería al Presupuesto", key="btn_add_alb"):
            st.session_state.cesta['alb_m2'] = {"nombre": "🏗️ Ayuda de Albañilería y Remates", "unidad": "m²", "cantidad": cant_albanil, "precio_unitario": pu_albanil}
            st.success("Añadido al presupuesto activo.")
            st.rerun()

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([1, 1])
    with col_nav_b1:
        if st.button("⬅️ Atrás: 🛠️ Cálculos Normativos", key="btn_ant_3"):
            st.session_state.paso_actual = 2
            st.rerun()
    with col_nav_b2:
        if st.button("Siguiente: 📊 Resumen Presupuesto ➔", key="btn_sig_3"):
            st.session_state.paso_actual = 4
            st.rerun()

# -----------------------------------------------------------------------------
# NAVEGACIÓN 4: PRESUPUESTO FINAL Y DESCARGA EXCEL
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 4:
    st.subheader("📊 Paso 4: Estado General de Mediciones y Presupuesto")

    if st.session_state.cesta:
        filas_pres = []
        for item_id, d in st.session_state.cesta.items():
            filas_pres.append({
                "Partida / Concepto": d['nombre'],
                "Unidad": d['unidad'],
                "Cantidad": d['cantidad'],
                "Precio Unitario (€)": d['precio_unitario'],
                "Importe (€)": d['cantidad'] * d['precio_unitario']
            })
        
        df_pres = pd.DataFrame(filas_pres)
        
        st.dataframe(
            df_pres.style.format({
                "Cantidad": "{:.1f}",
                "Precio Unitario (€)": "{:.2f} €",
                "Importe (€)": "{:.2f} €"
            }),
            use_container_width=True
        )
        
        sub = df_pres["Importe (€)"].sum()
        iva_val = sub * (tipo_iva / 100)
        tot_val = sub + iva_val
        
        st.markdown("---")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Base Imponible", f"{sub:,.2f} €")
        col_r2.metric(f"IVA ({tipo_iva}%)", f"{iva_val:,.2f} €")
        col_r3.metric("TOTAL PRESUPUESTO", f"{tot_val:,.2f} €")
        
        st.markdown("---")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_pres.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')
            
            df_res = pd.DataFrame([
                {"Concepto": "Cliente / Empresa", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
                {"Concepto": "Dirección de Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
                {"Concepto": "Base Imponible", "Valor": f"{sub:.2f} €"},
                {"Concepto": "IVA", "Valor": f"{iva_val:.2f} €"},
                {"Concepto": "Total Presupuesto", "Valor": f"{tot_val:.2f} €"}
            ])
            df_res.to_excel(writer, index=False, sheet_name='Datos_Cliente')
            
        excel_bytes = output.getvalue()
        
        st.download_button(
            label="🟢 Descargar Presupuesto Profesional en Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"Presupuesto_{(st.session_state.cliente_nombre if st.session_state.cliente_nombre else 'Reforma').replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("El presupuesto está vacío. Añade partidas en el Paso 3 (Tarifas).")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([1, 1])
    with col_nav_b1:
        if st.button("⬅️ Atrás: 💶 Tarifas (€0)", key="btn_ant_4"):
            st.session_state.paso_actual = 3
            st.rerun()
    with col_nav_b2:
        if st.button("Siguiente: 📚 Biblioteca Normativa ➔", key="btn_sig_4"):
            st.session_state.paso_actual = 5
            st.rerun()

# -----------------------------------------------------------------------------
# NAVEGACIÓN 5: BIBLIOTECA NORMATIVA DE CONSULTA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 5:
    st.subheader("📚 Paso 5: Biblioteca Técnica y Compendio Normativo")
    st.write("Guía rápida de consulta de reglamentación técnica para proyectos en España.")

    t_n1, t_n2, t_n3, t_n4 = st.tabs(["⚡ REBT (Electricidad)", "🚰 CTE DB-HS (Fontanería)", "❄️ RITE (Climatización)", "📡 ICT2 (Telecomunicaciones)"])

    with t_n1:
        st.markdown("### ⚡ REBT (RD 842/2002)")
        st.write("• **ITC-BT-25:** Circuitos obligatorios C1 (iluminación), C2 (tomas generales), C3 (cocina/horno), C4 (lavadora/lavavajillas/termo) y C5 (baños/auxiliares).")
        st.write("• **Caída de tensión máxima:** 1.5% en derivación individual.")

    with t_n2:
        st.markdown("### 🚰 CTE DB-HS4 / DB-HS5")
        st.write("• **Caudales:** Lavabo 0.10 L/s | Ducha 0.20 L/s | Fregadero 0.20 L/s.")
        st.write("• **Presiones:** Mínima 1 bar, máxima 5 bar.")

    with t_n3:
        st.markdown("### ❄️ RITE (RD 1027/2007)")
        st.write("• **Exigencias:** Regulación por termostato, mantenimiento preventivo y contabilización de energía.")

    with t_n4:
        st.markdown("### 📡 ICT2 (RD 346/2011)")
        st.write("• **Redes:** Fibra óptica (FTTH), par trenzado Cat6 y coaxial con registro PAU centralizado.")

    st.markdown("---")
    if st.button("⬅️ Volver al Inicio: 📋 Estancias", key="btn_ant_5"):
        st.session_state.paso_actual = 1
        st.rerun()
