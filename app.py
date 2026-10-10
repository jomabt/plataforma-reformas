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
# PALETA DE COLORES SOLICITADA (CSS)
# Azul Profundo: #0F2C59 (Color Principal / Fondo de Secciones)
# Azul Eléctrico: #007BFF (Enlaces, Subtítulos y Bordes)
# Amarillo Energía: #FFC107 (Botones de Acción CTA)
# Gris Oscuro: #212529 (Textos Principales)
# Blanco Fondo: #F8F9FA (Fondo General Suave)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo General Suave */
    .stApp {
        background-color: #F8F9FA !important;
        color: #212529 !important;
    }
    
    /* Cabecera Principal - Azul Profundo */
    .header-branding {
        background-color: #0F2C59;
        border-left: 8px solid #007BFF;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(15, 44, 89, 0.15);
    }
    .header-branding h1 {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-branding p {
        color: #E0E7FF !important;
        font-size: 1.0rem;
        margin-top: 0.4rem;
    }
    .header-badge {
        background-color: #FFC107;
        color: #212529 !important;
        padding: 0.35rem 0.9rem;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.85rem;
        display: inline-block;
        margin-top: 0.6rem;
    }

    /* Subtítulos y Enlaces - Azul Eléctrico */
    h2, h3, h4, .sub-blue {
        color: #007BFF !important;
        font-weight: 700 !important;
    }
    
    /* Textos Principales - Gris Oscuro */
    p, span, div, label, .stWidgetLabel, div[data-baseweb="label"] {
        color: #212529 !important;
        font-weight: 600 !important;
    }

    /* Tarjetas de Módulo y Contenedores */
    .card-box {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-top: 5px solid #0F2C59 !important;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    /* Botones Principales CTA - Amarillo Energía con Texto Gris Oscuro */
    .stButton>button {
        background-color: #FFC107 !important;
        color: #212529 !important;
        font-weight: 800 !important;
        border: 1px solid #D39E00 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100% !important;
        font-size: 1.0rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #E0A800 !important;
        color: #000000 !important;
        transform: translateY(-1px);
    }

    /* Sidebar Estilo Limpio */
    div[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #007BFF !important;
    }
    
    /* Cajas de entrada de números y texto */
    input {
        color: #212529 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #007BFF !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA DE DATOS Y NAVEGACIÓN)
# -----------------------------------------------------------------------------
if 'paso_actual' not in st.session_state: st.session_state.paso_actual = 0  # 0: Inicio, 1: Estancias, 2: Cálculos, 3: Precios, 4: Presupuesto, 5: Biblioteca

if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 0.0

# Matriz de Estancias Completa
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 0
if 'n_salones' not in st.session_state: st.session_state.n_salones = 0
if 'n_banos' not in st.session_state: st.session_state.n_banos = 0
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 0
if 'n_galerias' not in st.session_state: st.session_state.n_galerias = 0
if 'n_terrazas' not in st.session_state: st.session_state.n_terrazas = 0
if 'n_trasteros' not in st.session_state: st.session_state.n_trasteros = 0

# Toggles de Alcance por Especialidad
if 'inc_elec' not in st.session_state: st.session_state.inc_elec = True
if 'inc_font' not in st.session_state: st.session_state.inc_font = True
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = False
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = False
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = False

# Precios Unitarios (0.00 € de inicio)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# CABECERA INSTITUCIONAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-branding">
    <h1>⚡ PRO-REFORMAS | Software de Ingeniería & Presupuestos</h1>
    <p>Plataforma técnica profesional para dimensionado normativo (REBT, CTE, RITE, ICT2) y presupuestación comercial.</p>
    <div class="header-badge">EDICIÓN COMERCIAL SAAS</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL DE CONTROL Y RESUMEN
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 👤 Datos del Cliente y Obra")
st.session_state.cliente_nombre = st.sidebar.text_input("Nombre del Cliente / Empresa", value=st.session_state.cliente_nombre, placeholder="Ej. Juan Pérez / D. Antonio López")
st.session_state.cliente_obra = st.sidebar.text_input("Dirección / Ubicación de la Obra", value=st.session_state.cliente_obra, placeholder="Ej. Av. Constitución 45, Castelldefels")
st.session_state.superficie = st.sidebar.number_input("Superficie Útil Afectada (m²)", min_value=0.0, value=st.session_state.superficie, step=5.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Especialidades Incluidas")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox("Tipo de IVA Aplicable", [21, 10, 0], format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})")

# -----------------------------------------------------------------------------
# BARRA DE NAVEGACIÓN PRINCIPAL (BOTONES DE NAVEGACIÓN SUPERIOR)
# -----------------------------------------------------------------------------
col_n1, col_n2, col_n3, col_n4, col_n5, col_n6 = st.columns(6)

with col_n1:
    if st.button("🏠 Inicio", key="btn_top_0"):
        st.session_state.paso_actual = 0
        st.rerun()

with col_n2:
    if st.button("📋 1. Estancias", key="btn_top_1"):
        st.session_state.paso_actual = 1
        st.rerun()

with col_n3:
    if st.button("🛠️ 2. Cálculos", key="btn_top_2"):
        st.session_state.paso_actual = 2
        st.rerun()

with col_n4:
    if st.button("💶 3. Precios", key="btn_top_3"):
        st.session_state.paso_actual = 3
        st.rerun()

with col_n5:
    if st.button("📊 4. Presupuesto", key="btn_top_4"):
        st.session_state.paso_actual = 4
        st.rerun()

with col_n6:
    if st.button("📚 5. Biblioteca", key="btn_top_5"):
        st.session_state.paso_actual = 5
        st.rerun()

st.markdown("---")

# Helper de navegación inferior
def barra_navegacion_inferior():
    st.markdown("---")
    col_b1, col_b2, col_b3, col_b4 = st.columns([2, 2, 2, 2])
    with col_b1:
        if st.button("🏠 Ir a Inicio", key=f"nav_home_{st.session_state.paso_actual}"):
            st.session_state.paso_actual = 0
            st.rerun()
    with col_b2:
        if st.session_state.paso_actual > 0:
            if st.button("⬅️ Atrás", key=f"nav_prev_{st.session_state.paso_actual}"):
                st.session_state.paso_actual -= 1
                st.rerun()
    with col_b3:
        if st.session_state.paso_actual < 5:
            if st.button("Siguiente ➔", key=f"nav_next_{st.session_state.paso_actual}"):
                st.session_state.paso_actual += 1
                st.rerun()
    with col_b4:
        if st.button("📊 Ver Presupuesto", key=f"nav_pres_{st.session_state.paso_actual}"):
            st.session_state.paso_actual = 4
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 0: INICIO Y PRESENTACIÓN
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == 0:
    st.markdown("## 🏠 Bienvenido al Gestor Técnico PRO-REFORMAS")
    st.write("Herramienta web integrada para la realización de dimensionados normativos y la elaboración de presupuestos comerciales de reformas e instalaciones.")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("""
        <div class="card-box">
            <h3 style="margin-top:0;">🚀 Flujo de Trabajo Guiado</h3>
            <ol style="line-height: 1.8;">
                <td><b>Paso 1 (Estancias):</b> Configura la superficie y todas las zonas del inmueble (Dormitorios, Baños, Cocina, Galerías, Terrazas, etc.).</td><br>
                <td><b>Paso 2 (Cálculos):</b> Revisa los cálculos automáticos según REBT, CTE DB-HS, RITE e ICT2.</td><br>
                <td><b>Paso 3 (Precios):</b> Define los precios unitarios convenidos (parten de 0.00 €).</td><br>
                <td><b>Paso 4 (Presupuesto):</b> Revisa el desglose general y descarga el informe oficial en Excel (.xlsx).</td><br>
                <td><b>Paso 5 (Biblioteca):</b> Consulta las normativas vigentes y guías técnicas.</td>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col_in2:
        st.markdown("""
        <div class="card-box">
            <h3 style="margin-top:0;">💡 Ventajas del Sistema</h3>
            <ul>
                <li><b>Modularidad total:</b> Activa o desactiva instalaciones desde la barra lateral.</li>
                <li><b>Cálculo en vivo:</b> Modifica los m² o las estancias para ver el impacto en tiempo real.</li>
                <li><b>Exportación comercial:</b> Genera presupuestos formateados para entregar a clientes.</li>
                <li><b>Estabilidad visual:</b> Paleta Soft Light diseñada para evitar la fatiga visual.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Comenzar Configuración (Paso 1)", key="btn_start_wizard"):
            st.session_state.paso_actual = 1
            st.rerun()

    barra_navegacion_inferior()

# -----------------------------------------------------------------------------
# PASO 1: DEFINICIÓN DE ESTANCIAS Y GEOMETRÍA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 1:
    st.markdown("## 📋 Paso 1: Configuración de Estancias y Geometría")
    st.write("Indica la cantidad de estancias de la vivienda o local para determinar automáticamente las necesidades de la instalación.")

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
        st.session_state.n_trasteros = st.number_input("📦 Trasteros / Garajes / Otros", min_value=0, value=st.session_state.n_trasteros, step=1)

    total_estancias = (
        st.session_state.n_dormitorios + st.session_state.n_salones + st.session_state.n_banos + 
        st.session_state.n_aseos + st.session_state.n_cocinas + st.session_state.n_galerias + 
        st.session_state.n_terrazas + st.session_state.n_trasteros
    )

    st.markdown("---")
    st.info(f"💡 **Resumen Inmueble:** {total_estancias} estancias configuradas | **Superficie Afectada:** {st.session_state.superficie:.1f} m².")

    barra_navegacion_inferior()

# -----------------------------------------------------------------------------
# PASO 2: DIMENSIONADO TÉCNICO NORMATIVO
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 2:
    st.markdown("## 🛠️ Paso 2: Dimensionado Técnico Normativo")
    st.write("Cálculos ingenieriles automáticos ajustados a las normativas técnicas en España.")

    # REBT
    with st.expander("⚡ **Instalación Eléctrica (REBT - RD 842/2002)**", expanded=True):
        if not st.session_state.inc_elec:
            st.warning("⚠️ El capítulo de Electricidad está marcado como NO INCLUIDO en el menú lateral.")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            electrificacion = st.selectbox("Nivel de Electrificación", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
            potencia_kw = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
        with col_e2:
            longitud_m = st.number_input("Longitud Derivación Individual (m)", min_value=0.0, value=15.0, step=1.0)
            I_calc = (potencia_kw * 1000) / (230 * 0.9)
            cd_max = 230 * 0.015
            s_min = (2 * longitud_m * (potencia_kw * 1000)) / (56 * cd_max * 230)
            st.success(f"✔️ **Intensidad Nominal:** {I_calc:.2f} A | **Sección Mínima Cable DI:** {max(6.0, s_min):.2f} mm² (Cu)")

    # CTE DB-HS
    with st.expander("🚰 **Fontanería y Saneamiento (CTE DB-HS4 / HS5)**", expanded=True):
        if not st.session_state.inc_font:
            st.warning("⚠️ El capítulo de Fontanería está marcado como NO INCLUIDO en el menú lateral.")
        n_puntos = (st.session_state.n_banos * 3) + (st.session_state.n_aseos * 2) + (st.session_state.n_cocinas * 3) + (st.session_state.n_galerias * 2)
        if n_puntos > 0:
            caudal_instalado = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40) + (st.session_state.n_galerias * 0.20)
            coef_simult = 1 / math.sqrt(max(1, n_puntos))
            caudal_diseno = caudal_instalado * coef_simult
            
            c1, c2 = st.columns(2)
            c1.metric("Caudal Total Instalado", f"{caudal_instalado:.2f} L/s")
            c2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
        else:
            st.info("Configura los baños o cocina en el Paso 1 para ver el cálculo hidráulico.")

    # RITE
    with st.expander("❄️ **Climatización y Calefacción (RITE - RD 1027/2007)**", expanded=True):
        if not st.session_state.inc_clima:
            st.warning("⚠️ El capítulo de Climatización está marcado como NO INCLUIDO en el menú lateral.")
        if st.session_state.superficie > 0:
            zona = st.selectbox("Calidad Térmica / Aislamiento", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_kw = (st.session_state.superficie * w_m2) / 1000
            frig = p_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie útil en la barra lateral para ver la carga térmica.")

    barra_navegacion_inferior()

# -----------------------------------------------------------------------------
# PASO 3: CUADRO DE PRECIOS UNITARIOS (€0 DE INICIO)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 3:
    st.markdown("## 💶 Paso 3: Asignación de Precios Unitarios")
    st.write("⚠️ **Todos los precios inician en 0.00 €.** Asigna las tarifas convenidas para cada partida.")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### ⚡ Capítulo 1: Electricidad")
        st.session_state.pu_elec_m2 = st.number_input("Instalación Eléctrica General (€/m²)", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0, format="%.2f")
        st.session_state.pu_elec_cgmp = st.number_input("Cuadro CGMP y Protecciones (€/ud)", min_value=0.0, value=st.session_state.pu_elec_cgmp, step=25.0, format="%.2f")

        st.markdown("#### 🚰 Capítulo 2: Fontanería")
        st.session_state.pu_font_bano = st.number_input("Instalación Completa Baño (€/baño)", min_value=0.0, value=st.session_state.pu_font_bano, step=50.0, format="%.2f")
        st.session_state.pu_font_cocina = st.number_input("Instalación Completa Cocina (€/cocina)", min_value=0.0, value=st.session_state.pu_font_cocina, step=50.0, format="%.2f")

    with col_p2:
        st.markdown("#### ❄️ Capítulo 3: Climatización")
        st.session_state.pu_clima_kw = st.number_input("Instalación Climatización RITE (€/kW)", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0, format="%.2f")

        st.markdown("#### 📡 Capítulo 4: Telecomunicaciones")
        st.session_state.pu_teleco_toma = st.number_input("Toma de Datos RJ45 Cat6 (€/toma)", min_value=0.0, value=st.session_state.pu_teleco_toma, step=5.0, format="%.2f")

        st.markdown("#### 🏗️ Capítulo 5: Albañilería Auxiliar")
        st.session_state.pu_albanil_m2 = st.number_input("Rozas, Ayuda y Tapado (€/m²)", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0, format="%.2f")

    barra_navegacion_inferior()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO FINAL Y EXPORTACIÓN EXCEL
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 4:
    st.markdown("## 📊 Paso 4: Estado de Mediciones y Presupuesto General")

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
        st.info("👉 Selecciona al menos un capítulo en la barra lateral para ver las partidas en la tabla.")

    barra_navegacion_inferior()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 5:
    st.markdown("## 📚 Paso 5: Biblioteca Técnica y Normativa")
    st.write("Compendio de referencias reglamentarias oficiales para consulta.")

    tab_n1, tab_n2, tab_n3, tab_n4 = st.tabs(["⚡ REBT", "🚰 CTE DB-HS", "❄️ RITE", "📡 ICT2"])

    with tab_n1:
        st.markdown("### ⚡ Reglamento Electrotécnico para Baja Tensión (REBT)")
        st.write("• **ITC-BT-25:** Regula los circuitos C1 al C5 para vivienda.")
        st.write("• **Caída de Tensión:** Límite máximo del 1.5% en derivación individual.")

    with tab_n2:
        st.markdown("### 🚰 CTE DB-HS4 y DB-HS5 Fontanería")
        st.write("• **Caudales:** Lavabo (0.10 L/s), Ducha (0.20 L/s), Fregadero (0.20 L/s).")

    with tab_n3:
        st.markdown("### ❄️ RITE Climatización")
        st.write("• **Regulación:** Obligatoriedad de termostatos de control y eficiencia.")

    with tab_n4:
        st.markdown("### 📡 ICT2 Telecomunicaciones")
        st.write("• **Infraestructura:** Cableado Cat6, PAU centralizado y canalizaciones.")

    barra_navegacion_inferior()
