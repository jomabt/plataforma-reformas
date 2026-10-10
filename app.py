import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y TEMA SAAS PROFESIONAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PRO-REFORMAS | Software de Cálculo Técnico y Presupuestos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS CON ALTA VISIBILIDAD Y CONTRASTE (APLICA A MODO CLARO Y OSCURO)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo de la aplicación */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* FORZAR LEGIBILIDAD EXTREMA EN TODOS LOS TÍTULOS Y ENCABEZADOS */
    h1, h2, h3, h4, h5, h6, 
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        color: #0F172A !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px !important;
    }

    /* Subtítulos de sección destacados */
    .section-header-title {
        color: #0F172A !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        border-bottom: 3px solid #2563EB;
        padding-bottom: 0.4rem;
    }

    /* Encabezado principal del Software */
    .saas-header {
        background-color: #0F172A !important;
        border-left: 8px solid #2563EB !important;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        color: #FFFFFF !important;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .saas-title {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0 !important;
        letter-spacing: -0.5px !important;
    }
    .saas-subtitle {
        color: #94A3B8 !important;
        font-size: 1.0rem !important;
        margin-top: 0.3rem !important;
    }

    /* Forzar visibilidad en cajas de texto y etiquetas de inputs */
    label, .stWidgetLabel, div[data-baseweb="label"] {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
    }
    
    input, select, textarea {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border: 1px solid #94A3B8 !important;
        font-weight: 700 !important;
    }

    /* Cajas y contenedores del menú lateral */
    .sidebar-section-box {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .sidebar-title {
        color: #0F172A !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.6rem !important;
        border-bottom: 2px solid #2563EB;
        padding-bottom: 0.2rem;
    }

    /* Botones de acción principal (Azul SaaS / Naranja) */
    .stButton>button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100% !important;
        font-size: 0.98rem !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }

    /* Tarjetas de cálculo */
    .card-calc {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 5px solid #2563EB !important;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA Y NAVEGACIÓN)
# -----------------------------------------------------------------------------
if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = 1

if 'cliente_nombre' not in st.session_state:
    st.session_state.cliente_nombre = ""

if 'cliente_obra' not in st.session_state:
    st.session_state.cliente_obra = ""

if 'superficie' not in st.session_state:
    st.session_state.superficie = 0.0

# Estancias de la vivienda
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 0
if 'n_banos' not in st.session_state: st.session_state.n_banos = 0
if 'n_salones' not in st.session_state: st.session_state.n_salones = 0
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 0

# Especialidades activas
if 'inc_elec' not in st.session_state: st.session_state.inc_elec = True
if 'inc_font' not in st.session_state: st.session_state.inc_font = True
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = False
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = False
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = False

# Precios Unitarios (€0.00 de inicio)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# CABECERA PRINCIPAL DEL SOFTWARE
# -----------------------------------------------------------------------------
st.markdown("""
<div class="saas-header">
    <div class="saas-title">⚡ PRO-REFORMAS | Gestor Técnico & Presupuestos</div>
    <div class="saas-subtitle">Software SaaS de Ingeniería para Cálculo Normativo (REBT, CTE, RITE, ICT2) y Mediciones.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL: DATOS DEL CLIENTE, UBICACIÓN Y ESPECIALIDADES
# -----------------------------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-section-box">
    <div class="sidebar-title">👤 DATOS DEL CLIENTE Y OBRA</div>
</div>
""", unsafe_allow_html=True)

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

st.session_state.superficie = st.sidebar.number_input(
    "📐 Superficie Útil Afectada (m²):", 
    min_value=0.0, 
    value=st.session_state.superficie, 
    step=5.0
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div class="sidebar-section-box">
    <div class="sidebar-title">🔧 CAPÍTULOS DE INSTALACIÓN</div>
</div>
""", unsafe_allow_html=True)

st.session_state.inc_elec = st.sidebar.checkbox("⚡ Capítulo 1: Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Capítulo 2: Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Capítulo 3: Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Capítulo 4: Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Capítulo 5: Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox(
    "💶 Tipo de IVA Aplicable:",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})"
)

# -----------------------------------------------------------------------------
# BOTONES DE NAVEGACIÓN PRINCIPALES (BARRA SUPERIOR)
# -----------------------------------------------------------------------------
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)

with col_p1:
    if st.button("📋 1. Estancias", key="top_p1"):
        st.session_state.paso_actual = 1
        st.rerun()

with col_p2:
    if st.button("🛠️ 2. Cálculos", key="top_p2"):
        st.session_state.paso_actual = 2
        st.rerun()

with col_p3:
    if st.button("💶 3. Tarifas (€0)", key="top_p3"):
        st.session_state.paso_actual = 3
        st.rerun()

with col_p4:
    if st.button("📊 4. Presupuesto", key="top_p4"):
        st.session_state.paso_actual = 4
        st.rerun()

with col_p5:
    if st.button("📚 5. Biblioteca", key="top_p5"):
        st.session_state.paso_actual = 5
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# PASO 1: DEFINICIÓN DE ESTANCIAS Y GEOMETRÍA
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == 1:
    st.markdown('<div class="section-header-title">📋 Paso 1: Configuración de Estancias y Geometría</div>', unsafe_allow_html=True)
    st.write("Indica las estancias de la vivienda para estimar automáticamente los puntos de utilización según normativa.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.n_dormitorios = st.number_input("Número de Dormitorios:", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_banos = st.number_input("Baños Completos:", min_value=0, value=st.session_state.n_banos, step=1)
    with col2:
        st.session_state.n_salones = st.number_input("Salones / Comedores:", min_value=0, value=st.session_state.n_salones, step=1)
        st.session_state.n_aseos = st.number_input("Aseos (Sin ducha):", min_value=0, value=st.session_state.n_aseos, step=1)
    with col3:
        st.session_state.n_cocinas = st.number_input("Número de Cocinas:", min_value=0, value=st.session_state.n_cocinas, step=1)

    estancias_totales = st.session_state.n_dormitorios + st.session_state.n_salones + st.session_state.n_banos + st.session_state.n_aseos + st.session_state.n_cocinas

    st.markdown("---")
    st.info(f"💡 **Resumen del Inmueble:** {estancias_totales} estancias configuradas | **Superficie Afectada:** {st.session_state.superficie:.1f} m².")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([3, 1])
    with col_nav_b2:
        if st.button("Siguiente: Cálculos Normativos ➔", key="btn_next_1"):
            st.session_state.paso_actual = 2
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 2: CÁLCULOS NORMATIVOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 2:
    st.markdown('<div class="section-header-title">🛠️ Paso 2: Cálculos Técnicos y Normativa Vigente</div>', unsafe_allow_html=True)
    st.write("Cálculos automatizados ajustados al REBT, CTE DB-HS, RITE e ICT2.")

    # REBT
    with st.expander("⚡ **Cálculo Electrotécnico (REBT - RD 842/2002)**", expanded=True):
        if not st.session_state.inc_elec:
            st.warning("⚠️ Capítulo de Electricidad marcado como EXCLUIDO en el menú lateral.")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            electrificacion = st.selectbox("Nivel de Electrificación:", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
            potencia_kw = st.selectbox("Potencia de Cálculo (kW):", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
        with col_e2:
            longitud_m = st.number_input("Longitud Derivación Individual (m):", min_value=0.0, value=15.0, step=1.0)
            
            # Motor
            I_calc = (potencia_kw * 1000) / (230 * 0.9)
            cd_max = 230 * 0.015
            s_min = (2 * longitud_m * (potencia_kw * 1000)) / (56 * cd_max * 230)
            st.success(f"✔️ **Intensidad:** {I_calc:.2f} A | **Sección Mínima Cable DI:** {max(6.0, s_min):.2f} mm² (Cu)")

    # Fontanería CTE
    with st.expander("🚰 **Cálculo Hidráulico y Saneamiento (CTE DB-HS4 / HS5)**", expanded=True):
        if not st.session_state.inc_font:
            st.warning("⚠️ Capítulo de Fontanería marcado como EXCLUIDO en el menú lateral.")
        n_puntos = (st.session_state.n_banos * 3) + (st.session_state.n_aseos * 2) + (st.session_state.n_cocinas * 3)
        if n_puntos > 0:
            caudal_instalado = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40)
            coef_simult = 1 / math.sqrt(max(1, n_puntos))
            caudal_diseno = caudal_instalado * coef_simult
            
            f1, f2 = st.columns(2)
            f1.metric("Caudal Total Instalado", f"{caudal_instalado:.2f} L/s")
            f2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
        else:
            st.info("Configura los baños o cocinas en el Paso 1 para ver el cálculo de caudal.")

    # Climatización RITE
    with st.expander("❄️ **Cálculo Térmico y Climatización (RITE - RD 1027/2007)**", expanded=True):
        if not st.session_state.inc_clima:
            st.warning("⚠️ Capítulo de Climatización marcado como EXCLUIDO en el menú lateral.")
        if st.session_state.superficie > 0:
            zona = st.selectbox("Calidad Térmica de Aislamiento:", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_kw = (st.session_state.superficie * w_m2) / 1000
            frig = p_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie útil en el menú lateral para calcular la potencia térmica.")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([1, 1])
    with col_nav_b1:
        if st.button("⬅️ Anterior: Configurar Estancias", key="btn_prev_2"):
            st.session_state.paso_actual = 1
            st.rerun()
    with col_nav_b2:
        if st.button("Siguiente: Asignar Precios ➔", key="btn_next_2"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 3: CUADRO DE PRECIOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 3:
    st.markdown('<div class="section-header-title">💶 Paso 3: Asignación de Precios Unitarios (€0.00 de inicio)</div>', unsafe_allow_html=True)
    st.write("⚠️ **Todos los precios inician en 0.00 €.** Introduce tus tarifas pactadas por m², unidad o punto.")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### ⚡ Capítulo 1: Electricidad")
        st.session_state.pu_elec_m2 = st.number_input("Precio Renovación Eléctrica (€/m²):", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0, format="%.2f")
        st.session_state.pu_elec_cgmp = st.number_input("Precio Cuadro CGMP y Protecciones (€/ud):", min_value=0.0, value=st.session_state.pu_elec_cgmp, step=25.0, format="%.2f")

        st.markdown("#### 🚰 Capítulo 2: Fontanería")
        st.session_state.pu_font_bano = st.number_input("Precio Fontanería Baño Completo (€/baño):", min_value=0.0, value=st.session_state.pu_font_bano, step=50.0, format="%.2f")
        st.session_state.pu_font_cocina = st.number_input("Precio Fontanería Cocina Completa (€/cocina):", min_value=0.0, value=st.session_state.pu_font_cocina, step=50.0, format="%.2f")

    with col_p2:
        st.markdown("#### ❄️ Capítulo 3: Climatización")
        st.session_state.pu_clima_kw = st.number_input("Precio Climatización RITE (€/kW):", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0, format="%.2f")

        st.markdown("#### 📡 Capítulo 4: Telecomunicaciones")
        st.session_state.pu_teleco_toma = st.number_input("Precio Toma Cat6 e ICT2 (€/toma):", min_value=0.0, value=st.session_state.pu_teleco_toma, step=5.0, format="%.2f")

        st.markdown("#### 🏗️ Capítulo 5: Albañilería Auxiliar")
        st.session_state.pu_albanil_m2 = st.number_input("Precio Rozas, Ayuda y Sellado (€/m²):", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0, format="%.2f")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([1, 1])
    with col_nav_b1:
        if st.button("⬅️ Anterior: Cálculos Normativos", key="btn_prev_3"):
            st.session_state.paso_actual = 2
            st.rerun()
    with col_nav_b2:
        if st.button("Siguiente: Ver Presupuesto ➔", key="btn_next_3"):
            st.session_state.paso_actual = 4
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO GENERAL Y EXPORTACIÓN
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 4:
    st.markdown('<div class="section-header-title">📊 Paso 4: Estado de Mediciones y Presupuesto General</div>', unsafe_allow_html=True)

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
        st.info("👉 Activa al menos un capítulo en la barra lateral para ver las partidas del presupuesto.")

    st.markdown("---")
    col_nav_b1, col_nav_b2 = st.columns([1, 1])
    with col_nav_b1:
        if st.button("⬅️ Anterior: Cuadro de Precios", key="btn_prev_4"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 5:
    st.markdown('<div class="section-header-title">📚 Biblioteca Técnica y Referencias Normativas</div>', unsafe_allow_html=True)

    tab_n1, tab_n2, tab_n3, tab_n4 = st.tabs(["⚡ REBT (Electricidad)", "🚰 CTE DB-HS (Fontanería)", "❄️ RITE (Climatización)", "📡 ICT2 (Telecomunicaciones)"])

    with tab_n1:
        st.markdown("### ⚡ Reglamento Electrotécnico para Baja Tensión (REBT)")
        st.write("• **ITC-BT-25:** Circuitos de electrificación C1 a C5 y elevada.")
        st.write("• **Caída de Tensión:** Máximo 1.5% en DI y 3% en viviendas.")

    with tab_n2:
        st.markdown("### 🚰 Código Técnico de la Edificación (CTE DB-HS4/HS5)")
        st.write("• **Caudales:** Lavabo (0.10 L/s), Ducha (0.20 L/s), Fregadero (0.20 L/s).")

    with tab_n3:
        st.markdown("### ❄️ Reglamento de Instalaciones Térmicas (RITE)")
        st.write("• **Eficiencia:** Termostatos obligatorios y mantenimientos periódicos MITECO.")

    with tab_n4:
        st.markdown("### 📡 Telecomunicaciones (ICT2)")
        st.write("• **Infraestructura:** Par trenzado Cat6, Fibra Óptica FTTH y PAU empotrado.")

    st.markdown("---")
    if st.button("⬅️ Volver a Ver Presupuesto General", key="btn_prev_5"):
        st.session_state.paso_actual = 4
        st.rerun()
