import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PRO-REFORMAS | Software Técnico y Presupuestos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (PALETA OFICIAL)
# -----------------------------------------------------------------------------
# Azul Profundo: #0F2C59 (Fondo de Menú Izquierdo / Cabecera)
# Azul Eléctrico: #007BFF (Subtítulos, Enlaces)
# Amarillo Energía: #FFC107 (Botones CTA, +, -, Novedades)
# Gris Oscuro: #212529 (Textos Principales)
# Blanco Fondo: #F8F9FA (Fondo General)

st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #F8F9FA !important;
        color: #212529 !important;
    }

    /* Fondo del Menú Izquierdo (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
    }

    /* Textos y Etiquetas dentro del Menú Izquierdo */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }

    /* Inputs de texto y selectboxes dentro del Sidebar */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border-radius: 6px !important;
    }

    /* Header principal */
    .header-main {
        background-color: #0F2C59;
        border-left: 8px solid #FFC107;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
    }
    .header-subtitle {
        color: #007BFF !important;
        font-size: 1rem;
        margin-top: 0.3rem;
        font-weight: 600;
    }

    /* Botones principales de acción y CTA */
    .stButton>button {
        background-color: #FFC107 !important;
        color: #212529 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #E0A800 !important;
        color: #212529 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    }

    /* Estilo específico para los botones de + y - en NumberInputs */
    button[title*="Increment"], button[title*="Decrement"], 
    [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {
        background-color: #FFC107 !important;
        color: #212529 !important;
        border-radius: 4px !important;
        border: 1px solid #D39E00 !important;
        font-weight: bold !important;
    }
    button[title*="Increment"]:hover, button[title*="Decrement"]:hover,
    [data-testid="stNumberInputStepUp"]:hover, [data-testid="stNumberInputStepDown"]:hover {
        background-color: #E0A800 !important;
        color: #212529 !important;
    }

    /* Tarjetas de Módulos / Estancias */
    .card-box {
        background-color: #FFFFFF !important;
        border: 1px solid #CED4DA !important;
        border-top: 4px solid #007BFF !important;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .card-title {
        color: #0F2C59 !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        margin-bottom: 0.4rem !important;
    }
    .card-desc {
        color: #212529 !important;
        font-size: 0.9rem !important;
    }

    /* Textos y Etiquetas principales */
    label, .stWidgetLabel, div[data-baseweb="label"] {
        color: #212529 !important;
        font-weight: 700 !important;
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        color: #0F2C59 !important;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F2C59 !important;
        color: #FFC107 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA DE DATOS)
# -----------------------------------------------------------------------------
if 'paso_actual' not in st.session_state: st.session_state.paso_actual = 1
if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 0.0

# Estancias de la vivienda
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 0
if 'n_salones' not in st.session_state: st.session_state.n_salones = 0
if 'n_banos' not in st.session_state: st.session_state.n_banos = 0
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 0
if 'n_galerias' not in st.session_state: st.session_state.n_galerias = 0
if 'n_terrazas' not in st.session_state: st.session_state.n_terrazas = 0
if 'n_trasteros' not in st.session_state: st.session_state.n_trasteros = 0

# Toggles de Capítulos Incluidos
if 'inc_elec' not in st.session_state: st.session_state.inc_elec = True
if 'inc_font' not in st.session_state: st.session_state.inc_font = True
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = False
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = False
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = False

# Precios Unitarios (Inician en €0.00 por defecto)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# CABECERA PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-main">
    <div class="header-title">⚡ PRO-REFORMAS | Software Técnico y Presupuestos</div>
    <div class="header-subtitle">Plataforma Profesional de Medición de Obras y Cálculos Normativos (REBT, CTE, RITE, ICT2)</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (AZUL PROFUNDO #0F2C59)
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 👤 DATOS DEL CLIENTE Y OBRA")

st.session_state.cliente_nombre = st.sidebar.text_input(
    "📌 Nombre del Cliente / Empresa:",
    value=st.session_state.cliente_nombre,
    placeholder="Ej. D. Antonio López / Empresa"
)

st.session_state.cliente_obra = st.sidebar.text_input(
    "📍 Dirección / Ubicación de la Obra:",
    value=st.session_state.cliente_obra,
    placeholder="Ej. Av. Constitución 45, Castelldefels"
)

st.session_state.superficie = st.sidebar.number_input(
    "📐 Superficie Útil Afectada (m²):",
    min_value=0.0,
    value=st.session_state.superficie,
    step=5.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 CAPÍTULOS INCLUIDOS")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Capítulo 1: Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Capítulo 2: Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Capítulo 3: Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Capítulo 4: Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Capítulo 5: Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox(
    "Tipo de IVA Aplicable",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido' if x==10 else 'Exento'})"
)

# -----------------------------------------------------------------------------
# BOTONES SUPERIORES DE NAVEGACIÓN PASO A PASO
# -----------------------------------------------------------------------------
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

with nav_col1:
    if st.button("📋 1. Estancias", key="btn_nav_p1"):
        st.session_state.paso_actual = 1
        st.rerun()

with nav_col2:
    if st.button("🛠️ 2. Cálculos", key="btn_nav_p2"):
        st.session_state.paso_actual = 2
        st.rerun()

with nav_col3:
    if st.button("💶 3. Precios", key="btn_nav_p3"):
        st.session_state.paso_actual = 3
        st.rerun()

with nav_col4:
    if st.button("📊 4. Presupuesto", key="btn_nav_p4"):
        st.session_state.paso_actual = 4
        st.rerun()

with nav_col5:
    if st.button("📚 5. Biblioteca", key="btn_nav_p5"):
        st.session_state.paso_actual = 5
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# PASO 1: ALCANCE Y ESTANCIAS
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == 1:
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría")
    st.write("Indica el número de estancias para definir las necesidades mínimas de la instalación:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.session_state.n_dormitorios = st.number_input("🛌 Dormitorios", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_cocinas = st.number_input("🍳 Cocinas", min_value=0, value=st.session_state.n_cocinas, step=1)

    with col2:
        st.session_state.n_salones = st.number_input("🛋️ Salones / Comedores", min_value=0, value=st.session_state.n_salones, step=1)
        st.session_state.n_galerias = st.number_input("🧺 Galerías / Lavaderos", min_value=0, value=st.session_state.n_galerias, step=1)

    with col3:
        st.session_state.n_banos = st.number_input("🛁 Baños Completos", min_value=0, value=st.session_state.n_banos, step=1)
        st.session_state.n_terrazas = st.number_input("🌿 Terrazas / Balcones", min_value=0, value=st.session_state.n_terrazas, step=1)

    with col4:
        st.session_state.n_aseos = st.number_input("🧻 Aseos (Sin Ducha)", min_value=0, value=st.session_state.n_aseos, step=1)
        st.session_state.n_trasteros = st.number_input("📦 Trasteros / Garaje / Otros", min_value=0, value=st.session_state.n_trasteros, step=1)

    estancias_totales = (
        st.session_state.n_dormitorios + st.session_state.n_salones + 
        st.session_state.n_banos + st.session_state.n_aseos + 
        st.session_state.n_cocinas + st.session_state.n_galerias + 
        st.session_state.n_terrazas + st.session_state.n_trasteros
    )

    st.info(f"💡 **Resumen Inmueble:** {estancias_totales} estancias configuradas | **Superficie:** {st.session_state.superficie:.1f} m².")

    st.markdown("---")
    c_bot1, c_bot2 = st.columns([4, 1])
    with c_bot2:
        if st.button("Siguiente Paso ➔", key="btn_next_p1"):
            st.session_state.paso_actual = 2
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 2: CÁLCULOS NORMATIVOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 2:
    st.subheader("🛠️ Paso 2: Dimensionado Técnico de Instalaciones")
    st.write("Cálculos ingenieriles automatizados según normativas técnicas vigentes:")

    with st.expander("⚡ **Cálculo Electrotécnico (REBT - RD 842/2002)**", expanded=True):
        if not st.session_state.inc_elec:
            st.caption("ℹ️ Capítulo de Electricidad marcado como NO INCLUIDO.")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            electrificacion = st.selectbox("Nivel de Electrificación", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
            potencia_kw = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
        with col_e2:
            longitud_m = st.number_input("Longitud Derivación Individual (m)", min_value=0.0, value=15.0, step=1.0)
            I_calc = (potencia_kw * 1000) / (230 * 0.9)
            cd_max = 230 * 0.015
            s_min = (2 * longitud_m * (potencia_kw * 1000)) / (56 * cd_max * 230)
            st.success(f"✔️ **Intensidad de Cálculo:** {I_calc:.2f} A | **Sección Mínima DI:** {max(6.0, s_min):.2f} mm² (Cu)")

    with st.expander("🚰 **Cálculo Hidráulico y Saneamiento (CTE DB-HS4 / HS5)**", expanded=True):
        if not st.session_state.inc_font:
            st.caption("ℹ️ Capítulo de Fontanería marcado como NO INCLUIDO.")
        n_puntos = (st.session_state.n_banos * 3) + (st.session_state.n_aseos * 2) + (st.session_state.n_cocinas * 3)
        if n_puntos > 0:
            caudal_instalado = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40)
            coef_simult = 1 / math.sqrt(max(1, n_puntos))
            caudal_diseno = caudal_instalado * coef_simult
            c1, c2 = st.columns(2)
            c1.metric("Caudal Total Instalado", f"{caudal_instalado:.2f} L/s")
            c2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
        else:
            st.info("Configura los baños y cocinas en el Paso 1 para ejecutar el cálculo de caudal.")

    with st.expander("❄️ **Cálculo Térmico y Climatización (RITE - RD 1027/2007)**", expanded=True):
        if not st.session_state.inc_clima:
            st.caption("ℹ️ Capítulo de Climatización marcado como NO INCLUIDO.")
        if st.session_state.superficie > 0:
            zona = st.selectbox("Aislamiento Térmico", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_kw = (st.session_state.superficie * w_m2) / 1000
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{p_kw * 860:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie útil en la barra lateral para calcular la potencia térmica.")

    st.markdown("---")
    c_bot1, c_bot2, c_bot3 = st.columns([1, 3, 1])
    with c_bot1:
        if st.button("⬅️ Paso Anterior", key="btn_prev_p2"):
            st.session_state.paso_actual = 1
            st.rerun()
    with c_bot3:
        if st.button("Siguiente Paso ➔", key="btn_next_p2"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 3: CUADRO DE PRECIOS UNITARIOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 3:
    st.subheader("💶 Paso 3: Tarifación y Cuadro de Precios Unitarios")
    st.write("⚠️ **Todos los precios inician en 0.00 €.** Introduce tus tarifas convenidas:")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### ⚡ Capítulo 1: Electricidad")
        st.session_state.pu_elec_m2 = st.number_input("Instalación Eléctrica General (€/m²)", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0)
        st.session_state.pu_elec_cgmp = st.number_input("Cuadro CGMP y Protecciones (€/ud)", min_value=0.0, value=st.session_state.pu_elec_cgmp, step=25.0)

        st.markdown("#### 🚰 Capítulo 2: Fontanería")
        st.session_state.pu_font_bano = st.number_input("Instalación Fontanería Baño (€/baño)", min_value=0.0, value=st.session_state.pu_font_bano, step=50.0)
        st.session_state.pu_font_cocina = st.number_input("Instalación Fontanería Cocina (€/cocina)", min_value=0.0, value=st.session_state.pu_font_cocina, step=50.0)

    with col_p2:
        st.markdown("#### ❄️ Capítulo 3: Climatización")
        st.session_state.pu_clima_kw = st.number_input("Instalación Climatización RITE (€/kW)", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0)

        st.markdown("#### 📡 Capítulo 4: Telecomunicaciones")
        st.session_state.pu_teleco_toma = st.number_input("Toma Datos RJ45 Cat6 (€/toma)", min_value=0.0, value=st.session_state.pu_teleco_toma, step=5.0)

        st.markdown("#### 🏗️ Capítulo 5: Albañilería Auxiliar")
        st.session_state.pu_albanil_m2 = st.number_input("Rozas, Ayuda y Tapado (€/m²)", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0)

    st.markdown("---")
    c_bot1, c_bot2, c_bot3 = st.columns([1, 3, 1])
    with c_bot1:
        if st.button("⬅️ Paso Anterior", key="btn_prev_p3"):
            st.session_state.paso_actual = 2
            st.rerun()
    with c_bot3:
        if st.button("📊 Ver Presupuesto ➔", key="btn_next_p3"):
            st.session_state.paso_actual = 4
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO GENERAL Y EXCEL
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 4:
    st.subheader("📊 Paso 4: Estado de Mediciones y Presupuesto General")

    sup = st.session_state.superficie
    n_banos = st.session_state.n_banos + st.session_state.n_aseos
    n_cocinas = st.session_state.n_cocinas
    tomas_teleco = (st.session_state.n_dormitorios + st.session_state.n_salones) * 2
    potencia_clima = (sup * 100) / 1000 if sup > 0 else 0.0

    filas = []

    if st.session_state.inc_elec:
        filas.append({"Capítulo": "⚡ Electricidad", "Partida": "Instalación Eléctrica General en Vivienda", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_elec_m2, "Importe (€)": sup * st.session_state.pu_elec_m2})
        filas.append({"Capítulo": "⚡ Electricidad", "Partida": "Cuadro General de Mando y Protecciones (CGMP)", "Unidad": "ud", "Cantidad": 1 if sup > 0 else 0, "Precio Unitario (€)": st.session_state.pu_elec_cgmp, "Importe (€)": (1 if sup > 0 else 0) * st.session_state.pu_elec_cgmp})

    if st.session_state.inc_font:
        filas.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Saneamiento en Baños", "Unidad": "ud", "Cantidad": n_banos, "Precio Unitario (€)": st.session_state.pu_font_bano, "Importe (€)": n_banos * st.session_state.pu_font_bano})
        filas.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Desagües en Cocina", "Unidad": "ud", "Cantidad": n_cocinas, "Precio Unitario (€)": st.session_state.pu_font_cocina, "Importe (€)": n_cocinas * st.session_state.pu_font_cocina})

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
        st.info("👉 Activa al menos un capítulo en el menú lateral izquierdo para generar las partidas del presupuesto.")

    st.markdown("---")
    c_bot1, c_bot2, c_bot3 = st.columns([1, 3, 1])
    with c_bot1:
        if st.button("⬅️ Paso Anterior", key="btn_prev_p4"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 5:
    st.subheader("📚 Paso 5: Biblioteca Técnica y Referencias Normativas")
    st.write("Compendio de referencias oficiales y normativas para consulta rápida:")

    tab1, tab2, tab3, tab4 = st.tabs(["⚡ REBT (Electricidad)", "🚰 CTE DB-HS (Fontanería)", "❄️ RITE (Climatización)", "📡 ICT2 (Telecomunicaciones)"])

    with tab1:
        st.markdown("### ⚡ REBT (RD 842/2002)")
        st.write("• **ITC-BT-25:** Define los 5 circuitos básicos (C1 a C5) y adicionales (C8 a C12).")
        st.write("• **Caída de Tensión:** Máximo 1.5% en derivación individual y 3% en vivienda.")

    with tab2:
        st.markdown("### 🚰 CTE DB-HS (Salubridad)")
        st.write("• **DB-HS4:** Caudales mínimos instantáneos y presiones entre 1 y 5 bar.")
        st.write("• **DB-HS5:** Evacuación de aguas residuales y pluviales.")

    with tab3:
        st.markdown("### ❄️ RITE (RD 1027/2007)")
        st.write("• **Eficiencia y Contabilización:** Requisitos para sistemas térmicos e inspecciones de mantenimiento.")

    with tab4:
        st.markdown("### 📡 ICT2 (RD 346/2011)")
        st.write("• **Infraestructura Común:** Fibra óptica (FTTH), Cat6 y coaxial con registro PAU.")

    st.markdown("---")
    c_bot1, c_bot2 = st.columns([1, 4])
    with c_bot1:
        if st.button("⬅️ Paso Anterior", key="btn_prev_p5"):
            st.session_state.paso_actual = 4
            st.rerun()
