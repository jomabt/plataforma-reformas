import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PRO-REFORMAS | Software de Cálculo Técnico y Presupuestos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS CON PALETA DE COLORES EXPLICITA
# Principal: #0F2C59 (Azul Profundo)
# Subtítulos/Acentos: #007BFF (Azul Eléctrico)
# Botones/Bordes destacados: #FFC107 (Amarillo Energía)
# Textos: #212529 (Gris Oscuro)
# Fondo General: #F8F9FA (Blanco Fondo)
# Inputs/Cuadros: #FFFFFF (Blanco Puro)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo General de la App */
    .stApp {
        background-color: #F8F9FA !important;
        color: #212529 !important;
    }
    
    /* Encabezado Principal */
    .header-saas {
        background: linear-gradient(135deg, #0F2C59 0%, #007BFF 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 1.8rem;
        border-left: 10px solid #FFC107;
        box-shadow: 0 4px 12px rgba(15, 44, 89, 0.15);
    }
    .header-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #E2E8F0 !important;
        font-size: 1.15rem !important;
        margin-top: 0.4rem;
    }
    .header-badge {
        background-color: #FFC107;
        color: #0F2C59 !important;
        padding: 0.4rem 1.0rem;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 0.8rem;
    }

    /* Aumento de tamaño de fuente en títulos principales (+4pt) */
    h1, h2, h3, .stHeader {
        color: #0F2C59 !important;
        font-weight: 800 !important;
    }
    h1 { font-size: 2.4rem !important; }
    h2 { font-size: 2.0rem !important; }
    h3 { font-size: 1.6rem !important; }
    h4 { font-size: 1.3rem !important; color: #007BFF !important; }

    /* Barra Lateral (Sidebar) en Azul Profundo */
    section[data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Cuadros de Entrada (Inputs) del Menú Izquierdo: Fondo Blanco #FFFFFF */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 2px solid #FFC107 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        background-color: #FFFFFF !important;
        color: #212529 !important;
    }

    /* Tarjetas de Módulos y Pestañas */
    .module-card {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-top: 5px solid #007BFF !important;
        border-radius: 10px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.04);
    }

    /* Botones de Acción CTA (Amarillo Energía) */
    .stButton>button {
        background-color: #FFC107 !important;
        color: #0F2C59 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border: None !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.2rem !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #E0A800 !important;
        color: #0F2C59 !important;
        transform: translateY(-1px);
    }

    /* Botones de Incrementar y Decrementar (+ / -) */
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background-color: #FFC107 !important;
        color: #0F2C59 !important;
        border: 1px solid #D39E00 !important;
        border-radius: 6px !important;
        font-weight: 900 !important;
    }

    /* Formulario General e Inputs del Cuerpo */
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 700 !important;
    }

    /* Tablas y Métricas */
    div[data-testid="stMetricValue"] {
        color: #0F2C59 !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA DE DATOS Y PASO ACTUAL)
# -----------------------------------------------------------------------------
if 'paso_actual' not in st.session_state: st.session_state.paso_actual = "📋 1. Alcance y Estancias"
if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 80.0

# Cantidad de Estancias (8 Zonas Completas)
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 3
if 'n_salones' not in st.session_state: st.session_state.n_salones = 1
if 'n_banos' not in st.session_state: st.session_state.n_banos = 2
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 1
if 'n_galerias' not in st.session_state: st.session_state.n_galerias = 1
if 'n_terrazas' not in st.session_state: st.session_state.n_terrazas = 1
if 'n_trasteros' not in st.session_state: st.session_state.n_trasteros = 1

# Toggles de Capítulos Incluidos
if 'inc_elec' not in st.session_state: st.session_state.inc_elec = True
if 'inc_font' not in st.session_state: st.session_state.inc_font = True
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = True
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = True
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = True

# Precios Unitarios (En €0.00 por defecto)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-saas">
    <div class="header-title">⚡ PRO-REFORMAS | Software Técnico y Presupuestos</div>
    <div class="header-subtitle">Plataforma SaaS para dimensionado técnico (REBT, CTE DB-HS, RITE, ICT2) y cuadro de mediciones comercial.</div>
    <div class="header-badge">VERSIÓN COMERCIAL SAAS 2026</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU IZQUIERDO)
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 👤 Datos del Cliente y Obra")

st.session_state.cliente_nombre = st.sidebar.text_input(
    "📌 Nombre del Cliente / Empresa:",
    value=st.session_state.cliente_nombre,
    placeholder="Ej. D. Juan Pérez / Reforma C/ Mayor"
)

st.session_state.cliente_obra = st.sidebar.text_input(
    "📍 Dirección / Ubicación de la Obra:",
    value=st.session_state.cliente_obra,
    placeholder="Ej. Av. Constitución 45, Castelldefels"
)

st.session_state.superficie = st.sidebar.number_input(
    "📐 Superficie Útil Afectada (m²):",
    min_value=0.0,
    value=float(st.session_state.superficie),
    step=5.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Capítulos en Presupuesto")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Cap. 1: Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Cap. 2: Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Cap. 3: Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Cap. 4: Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Cap. 5: Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox(
    "Tipo de IVA Aplicable:",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})"
)

# -----------------------------------------------------------------------------
# NAVEGACIÓN PRINCIPAL SUPERIOR (RADIO BAR)
# -----------------------------------------------------------------------------
pasos_lista = [
    "📋 1. Alcance y Estancias", 
    "🛠️ 2. Dimensionado Técnico", 
    "💶 3. Cuadro de Precios (€0)", 
    "📊 4. Presupuesto Final y Excel", 
    "📚 5. Biblioteca Normativa"
]

paso_seleccionado = st.radio(
    "Selecciona la sección de trabajo:",
    pasos_lista,
    index=pasos_lista.index(st.session_state.paso_actual) if st.session_state.paso_actual in pasos_lista else 0,
    horizontal=True
)
st.session_state.paso_actual = paso_seleccionado

st.markdown("---")

# -----------------------------------------------------------------------------
# PASO 1: ALCANCE Y ESTANCIAS (8 ZONAS COMPLETAS)
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == "📋 1. Alcance y Estancias":
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría de la Obra")
    st.write("Indica la cantidad de estancias y espacios para calcular los mínimos normativos de puntos de luz, tomas de agua y datos.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state.n_dormitorios = st.number_input("🛌 Dormitorios", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_salones = st.number_input("🛋️ Salones / Comedores", min_value=0, value=st.session_state.n_salones, step=1)
    with col2:
        st.session_state.n_banos = st.number_input("🛁 Baños Completos", min_value=0, value=st.session_state.n_banos, step=1)
        st.session_state.n_aseos = st.number_input("🧻 Aseos (Sin Ducha)", min_value=0, value=st.session_state.n_aseos, step=1)
    with col3:
        st.session_state.n_cocinas = st.number_input("🍳 Cocinas", min_value=0, value=st.session_state.n_cocinas, step=1)
        st.session_state.n_galerias = st.number_input("🧺 Galerías / Lavaderos", min_value=0, value=st.session_state.n_galerias, step=1)
    with col4:
        st.session_state.n_terrazas = st.number_input("🌿 Terrazas / Balcones", min_value=0, value=st.session_state.n_terrazas, step=1)
        st.session_state.n_trasteros = st.number_input("📦 Trasteros / Garajes", min_value=0, value=st.session_state.n_trasteros, step=1)

    estancias_totales = (
        st.session_state.n_dormitorios + st.session_state.n_salones + 
        st.session_state.n_banos + st.session_state.n_aseos + 
        st.session_state.n_cocinas + st.session_state.n_galerias + 
        st.session_state.n_terrazas + st.session_state.n_trasteros
    )

    st.info(f"💡 **Resumen del Inmueble:** {estancias_totales} estancias/zonas registradas | **Superficie Afectada:** {st.session_state.superficie:.1f} m².")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b2:
        if st.button("Siguiente: 🛠️ 2. Dimensionado Técnico ➔", key="btn_p1_next"):
            st.session_state.paso_actual = "🛠️ 2. Dimensionado Técnico"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 2: DIMENSIONADO TÉCNICO NORMATIVO
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "🛠️ 2. Dimensionado Técnico":
    st.subheader("🛠️ Paso 2: Dimensionado Técnico de Instalaciones")
    st.write("Motores de cálculo según la normativa española (REBT, CTE DB-HS, RITE, ICT2).")

    # Electricidad REBT
    with st.expander("⚡ **Cálculo Electrotécnico (REBT - RD 842/2002)**", expanded=True):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            electrificacion = st.selectbox("Nivel de Electrificación", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
            potencia_kw = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
        with col_e2:
            longitud_m = st.number_input("Longitud Derivación Individual (m)", min_value=1.0, value=15.0, step=1.0)
            I_calc = (potencia_kw * 1000) / (230 * 0.9)
            cd_max = 230 * 0.015
            s_min = (2 * longitud_m * (potencia_kw * 1000)) / (56 * cd_max * 230)
            s_rec = max(6.0, s_min)
            st.success(f"✔️ **Intensidad Nominal:** {I_calc:.2f} A | **Sección Mínima DI Recomendada:** {s_rec:.2f} mm² (Cu)")

    # Fontanería CTE DB-HS
    with st.expander("🚰 **Cálculo Hidráulico y Saneamiento (CTE DB-HS4 / HS5)**", expanded=True):
        n_puntos = (st.session_state.n_banos * 3) + (st.session_state.n_aseos * 2) + (st.session_state.n_cocinas * 3) + (st.session_state.n_galerias * 2)
        if n_puntos > 0:
            caudal_instalado = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40) + (st.session_state.n_galerias * 0.20)
            coef_simult = 1 / math.sqrt(max(1, n_puntos))
            caudal_diseno = caudal_instalado * coef_simult
            
            c1, c2 = st.columns(2)
            c1.metric("Caudal Total Instalado", f"{caudal_instalado:.2f} L/s")
            c2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
        else:
            st.info("Configura los baños y cocinas en el Paso 1 para ejecutar el cálculo hidráulico.")

    # Climatización RITE
    with st.expander("❄️ **Cálculo Térmico y Climatización (RITE - RD 1027/2007)**", expanded=True):
        if st.session_state.superficie > 0:
            zona = st.selectbox("Calidad Térmica / Aislamiento", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = 100 if "Media" in zona else (80 if "Buena" in zona else 120)
            p_kw = (st.session_state.superficie * w_m2) / 1000
            frig = p_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Paso Anterior: 📋 1. Estancias", key="btn_p2_prev"):
            st.session_state.paso_actual = "📋 1. Alcance y Estancias"
            st.rerun()
    with col_b2:
        if st.button("Siguiente: 💶 3. Cuadro de Precios (€0) ➔", key="btn_p2_next"):
            st.session_state.paso_actual = "💶 3. Cuadro de Precios (€0)"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 3: CUADRO DE PRECIOS (€0 INICIAL)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "💶 3. Cuadro de Precios (€0)":
    st.subheader("💶 Paso 3: Tarifación y Cuadro de Precios Unitarios")
    st.write("⚠️ **Todos los precios inician en 0.00 €.** Define los precios acordados con el cliente para cada partida.")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### ⚡ Capítulo 1: Electricidad")
        st.session_state.pu_elec_m2 = st.number_input("Instalación Eléctrica General (€/m²)", min_value=0.0, value=float(st.session_state.pu_elec_m2), step=5.0)
        st.session_state.pu_elec_cgmp = st.number_input("Cuadro CGMP y Protecciones (€/ud)", min_value=0.0, value=float(st.session_state.pu_elec_cgmp), step=25.0)

        st.markdown("#### 🚰 Capítulo 2: Fontanería")
        st.session_state.pu_font_bano = st.number_input("Instalación Completa Baño (€/baño)", min_value=0.0, value=float(st.session_state.pu_font_bano), step=50.0)
        st.session_state.pu_font_cocina = st.number_input("Instalación Completa Cocina (€/cocina)", min_value=0.0, value=float(st.session_state.pu_font_cocina), step=50.0)

    with col_p2:
        st.markdown("#### ❄️ Capítulo 3: Climatización")
        st.session_state.pu_clima_kw = st.number_input("Instalación Climatización RITE (€/kW)", min_value=0.0, value=float(st.session_state.pu_clima_kw), step=25.0)

        st.markdown("#### 📡 Capítulo 4: Telecomunicaciones")
        st.session_state.pu_teleco_toma = st.number_input("Toma de Datos RJ45 Cat6 (€/toma)", min_value=0.0, value=float(st.session_state.pu_teleco_toma), step=5.0)

        st.markdown("#### 🏗️ Capítulo 5: Albañilería Auxiliar")
        st.session_state.pu_albanil_m2 = st.number_input("Rozas, Ayuda y Tapado (€/m²)", min_value=0.0, value=float(st.session_state.pu_albanil_m2), step=5.0)

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Paso Anterior: 🛠️ 2. Cálculos", key="btn_p3_prev"):
            st.session_state.paso_actual = "🛠️ 2. Dimensionado Técnico"
            st.rerun()
    with col_b2:
        if st.button("Siguiente: 📊 4. Presupuesto Final y Excel ➔", key="btn_p3_next"):
            st.session_state.paso_actual = "📊 4. Presupuesto Final y Excel"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO FINAL Y EXCEL
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "📊 4. Presupuesto Final y Excel":
    st.subheader("📊 Paso 4: Estado de Mediciones y Presupuesto General")

    sup = st.session_state.superficie
    n_banos = st.session_state.n_banos + st.session_state.n_aseos
    n_cocinas = st.session_state.n_cocinas + st.session_state.n_galerias
    tomas_teleco = (st.session_state.n_dormitorios + st.session_state.n_salones) * 2
    potencia_clima = (sup * 100) / 1000 if sup > 0 else 0.0

    filas = []

    if st.session_state.inc_elec:
        filas.append({"Capítulo": "⚡ Electricidad", "Partida": "Instalación Eléctrica General en Vivienda", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_elec_m2, "Importe (€)": sup * st.session_state.pu_elec_m2})
        filas.append({"Capítulo": "⚡ Electricidad", "Partida": "Cuadro General de Mando y Protecciones (CGMP)", "Unidad": "ud", "Cantidad": 1 if sup > 0 else 0, "Precio Unitario (€)": st.session_state.pu_elec_cgmp, "Importe (€)": (1 if sup > 0 else 0) * st.session_state.pu_elec_cgmp})

    if st.session_state.inc_font:
        filas.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Saneamiento en Baños", "Unidad": "ud", "Cantidad": n_banos, "Precio Unitario (€)": st.session_state.pu_font_bano, "Importe (€)": n_banos * st.session_state.pu_font_bano})
        filas.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Desagües en Cocina/Galería", "Unidad": "ud", "Cantidad": n_cocinas, "Precio Unitario (€)": st.session_state.pu_font_cocina, "Importe (€)": n_cocinas * st.session_state.pu_font_cocina})

    if st.session_state.inc_clima:
        filas.append({"Capítulo": "❄️ Climatización", "Partida": "Equipamiento Climatización RITE", "Unidad": "kW", "Cantidad": potencia_clima, "Precio Unitario (€)": st.session_state.pu_clima_kw, "Importe (€)": potencia_clima * st.session_state.pu_clima_kw})

    if st.session_state.inc_teleco:
        filas.append({"Capítulo": "📡 Telecomunicaciones", "Partida": "Red de Datos Cat6 e Instalación ICT2", "Unidad": "toma", "Cantidad": tomas_teleco, "Precio Unitario (€)": st.session_state.pu_teleco_toma, "Importe (€)": tomas_teleco * st.session_state.pu_teleco_toma})

    if st.session_state.inc_albanil:
        filas.append({"Capítulo": "🏗️ Albañilería", "Partida": "Rozas, Ayuda a Instalaciones y Remates", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_albanil_m2, "Importe (€)": sup * st.session_state.pu_albanil_m2})

    if filas:
        df_presupuesto = pd.DataFrame(filas)
        st.dataframe(
            df_presupuesto.style.format({
                "Cantidad": "{:.1f}",
                "Precio Unitario (€)": "{:.2f} €",
                "Importe (€)": "{:.2f} €"
            }),
            use_container_width=True
        )

        subtotal = df_presupuesto["Importe (€)"].sum()
        impuesto = subtotal * (tipo_iva / 100)
        total = subtotal + impuesto

        st.markdown("---")
        c_r1, c_r2, c_r3 = st.columns(3)
        c_r1.metric("Base Imponible (Subtotal)", f"{subtotal:,.2f} €")
        c_r2.metric(f"IVA ({tipo_iva}%)", f"{impuesto:,.2f} €")
        c_r3.metric("TOTAL PRESUPUESTO", f"{total:,.2f} €")

        st.markdown("---")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_presupuesto.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')

            df_resumen = pd.DataFrame([
                {"Concepto": "Cliente / Referencia", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
                {"Concepto": "Ubicación Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
                {"Concepto": "Superficie Útil", "Valor": f"{sup} m²"},
                {"Concepto": "Subtotal (Base Imponible)", "Valor": f"{subtotal:.2f} €"},
                {"Concepto": f"IVA ({tipo_iva}%)", "Valor": f"{impuesto:.2f} €"},
                {"Concepto": "Total Presupuesto", "Valor": f"{total:.2f} €"}
            ])
            df_resumen.to_excel(writer, index=False, sheet_name='Resumen_Ejecutivo')

        excel_bytes = output.getvalue()

        st.download_button(
            label="🟢 Descargar Presupuesto Profesional en Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"Presupuesto_{(st.session_state.cliente_nombre if st.session_state.cliente_nombre else 'Reforma').replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("👉 Selecciona al menos un capítulo en la barra lateral izquierda para generar el cuadro de presupuesto.")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Paso Anterior: 💶 3. Precios", key="btn_p4_prev"):
            st.session_state.paso_actual = "💶 3. Cuadro de Precios (€0)"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "📚 5. Biblioteca Normativa":
    st.subheader("📚 Biblioteca Técnica y Referencias Normativas")
    st.write("Compendio normativo oficial de consulta para instalaciones en España.")

    tab_n1, tab_n2, tab_n3, tab_n4 = st.tabs([
        "⚡ REBT (Electricidad)", 
        "🚰 CTE DB-HS (Fontanería)", 
        "❄️ RITE (Climatización)", 
        "📡 ICT2 (Telecomunicaciones)"
    ])

    with tab_n1:
        st.markdown("### ⚡ Reglamento Electrotécnico para Baja Tensión (REBT - RD 842/2002)")
        st.write("• **ITC-BT-25:** Define los circuitos C1 (iluminación), C2 (enchufes), C3 (cocina/horno), C4 (lavadora/lavavajillas/termo) y C5 (baños/auxiliares).")
        st.write("• **Límite de Caída de Tensión:** Máximo 1.5% en derivación individual y 3% en instalaciones interiores.")

    with tab_n2:
        st.markdown("### 🚰 Código Técnico de la Edificación (CTE DB-HS4/HS5)")
        st.write("• **Caudales Mínimos:** Lavabo: 0.10 L/s | Ducha: 0.20 L/s | Fregadero: 0.20 L/s.")
        st.write("• **Presión de Servicio:** Mínima 1 bar, máxima 5 bar.")

    with tab_n3:
        st.markdown("### ❄️ Reglamento de Instalaciones Térmicas (RITE - RD 1027/2007)")
        st.write("• **Eficiencia:** Obligatoriedad de regulación por termostato y contabilización individualizada.")

    with tab_n4:
        st.markdown("### 📡 Infraestructuras de Telecomunicaciones (ICT2 - RD 346/2011)")
        st.write("• **Redes:** Par trenzado Cat6, Fibra Óptica (FTTH) y Coaxial con PAU centralizado.")

    st.markdown("---")
    if st.button("🏠 Volver al Inicio: 📋 1. Estancias", key="btn_p5_home"):
        st.session_state.paso_actual = "📋 1. Alcance y Estancias"
        st.rerun()
