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
# ESTILOS CSS CON PALETA CORPORATIVA OFICIAL
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo general suave */
    .stApp {
        background-color: #F8F9FA !important;
    }
    
    /* Barra lateral en Azul Profundo (#0F2C59) */
    section[data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] label {
        color: #FFC107 !important;
        font-weight: 700 !important;
    }

    /* Encabezado Principal */
    .saas-header {
        background-color: #0F2C59;
        border-left: 8px solid #007BFF;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
    }
    .saas-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
    }
    .saas-subtitle {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }

    /* Estilo específico para los cuadros de cantidades e inputs de número */
    div[data-testid="stNumberInputContainer"] {
        background-color: #FFFFFF !important;
        border: 2px solid #007BFF !important;
        border-radius: 6px !important;
    }
    div[data-testid="stNumberInputContainer"] input {
        color: #212529 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }
    /* Botones + y - en Amarillo Energía (#FFC107) */
    div[data-testid="stNumberInputContainer"] button {
        background-color: #FFC107 !important;
        color: #212529 !important;
        border: none !important;
        font-weight: 900 !important;
    }
    div[data-testid="stNumberInputContainer"] button:hover {
        background-color: #E0A800 !important;
        color: #212529 !important;
    }

    /* Botones principales en Amarillo Energía (#FFC107) */
    .stButton>button {
        background-color: #FFC107 !important;
        color: #212529 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100% !important;
        font-size: 1rem !important;
    }
    .stButton>button:hover {
        background-color: #E0A800 !important;
        color: #212529 !important;
    }

    /* Títulos y Subtítulos */
    h1, h2, h3 {
        color: #0F2C59 !important;
        font-weight: 800 !important;
    }
    h4, h5, h6 {
        color: #007BFF !important;
        font-weight: 700 !important;
    }
    p, label, span {
        color: #212529 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN
# -----------------------------------------------------------------------------
if 'paso_actual' not in st.session_state: st.session_state.paso_actual = 1
if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 0.0

# Estancias
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 0
if 'n_salones' not in st.session_state: st.session_state.n_salones = 0
if 'n_banos' not in st.session_state: st.session_state.n_banos = 0
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 0
if 'n_galerias' not in st.session_state: st.session_state.n_galerias = 0
if 'n_terrazas' not in st.session_state: st.session_state.n_terrazas = 0
if 'n_trasteros' not in st.session_state: st.session_state.n_trasteros = 0

# Toggles de Capítulos
if 'inc_elec' not in st.session_state: st.session_state.inc_elec = True
if 'inc_font' not in st.session_state: st.session_state.inc_font = True
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = True
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = True
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = True

# Precios Unitarios (€0 de inicio)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# ENCABEZADO
# -----------------------------------------------------------------------------
st.markdown("""
<div class="saas-header">
    <div class="saas-title">⚡ PRO-REFORMAS | Software de Cálculo & Presupuestos</div>
    <div class="saas-subtitle">Gestión Técnica Normativa según REBT, CTE DB-HS, RITE e ICT2</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (AZUL PROFUNDO)
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 👤 DATOS DEL CLIENTE Y OBRA")
st.session_state.cliente_nombre = st.sidebar.text_input(
    "📌 Nombre del Cliente / Empresa", 
    value=st.session_state.cliente_nombre, 
    placeholder="Ej. Juan Pérez / D. Antonio López"
)
st.session_state.cliente_obra = st.sidebar.text_input(
    "📍 Dirección / Ubicación de Obra", 
    value=st.session_state.cliente_obra, 
    placeholder="Ej. Av. Constitución 45, Castelldefels"
)
st.session_state.superficie = st.sidebar.number_input(
    "📐 Superficie Útil Afectada (m²)", 
    min_value=0.0, 
    value=st.session_state.superficie, 
    step=5.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ CAPÍTULOS INCLUIDOS")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox(
    "💶 Tipo de IVA Aplicable",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido' if x==10 else 'Exento'})"
)

# -----------------------------------------------------------------------------
# BARRA SUPERIOR DE NAVEGACIÓN
# -----------------------------------------------------------------------------
col_n1, col_n2, col_n3, col_n4, col_n5 = st.columns(5)

with col_n1:
    if st.button("📋 1. Estancias", key="nav_p1"):
        st.session_state.paso_actual = 1
        st.rerun()
with col_n2:
    if st.button("🛠️ 2. Cálculos", key="nav_p2"):
        st.session_state.paso_actual = 2
        st.rerun()
with col_n3:
    if st.button("💶 3. Precios", key="nav_p3"):
        st.session_state.paso_actual = 3
        st.rerun()
with col_n4:
    if st.button("📊 4. Presupuesto", key="nav_p4"):
        st.session_state.paso_actual = 4
        st.rerun()
with col_n5:
    if st.button("📚 5. Biblioteca", key="nav_p5"):
        st.session_state.paso_actual = 5
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# PASO 1: ESTANCIAS
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == 1:
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría")
    st.write("Indica la cantidad de cada tipo de estancia para dimensionar los circuitos, puntos de agua y tomas de datos:")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.session_state.n_dormitorios = st.number_input("🛌 Dormitorios", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_salones = st.number_input("🛋️ Salones / Comedores", min_value=0, value=st.session_state.n_salones, step=1)
    with c2:
        st.session_state.n_banos = st.number_input("🛁 Baños Completos", min_value=0, value=st.session_state.n_banos, step=1)
        st.session_state.n_aseos = st.number_input("🧻 Aseos (Sin Ducha)", min_value=0, value=st.session_state.n_aseos, step=1)
    with c3:
        st.session_state.n_cocinas = st.number_input("🍳 Cocinas", min_value=0, value=st.session_state.n_cocinas, step=1)
        st.session_state.n_galerias = st.number_input("🧺 Galerías / Lavaderos", min_value=0, value=st.session_state.n_galerias, step=1)
    with c4:
        st.session_state.n_terrazas = st.number_input("🌿 Terrazas / Balcones", min_value=0, value=st.session_state.n_terrazas, step=1)
        st.session_state.n_trasteros = st.number_input("📦 Trasteros / Garajes / Otros", min_value=0, value=st.session_state.n_trasteros, step=1)

    tot_estancias = (
        st.session_state.n_dormitorios + st.session_state.n_salones + 
        st.session_state.n_banos + st.session_state.n_aseos + 
        st.session_state.n_cocinas + st.session_state.n_galerias + 
        st.session_state.n_terrazas + st.session_state.n_trasteros
    )

    st.info(f"💡 **Resumen:** {tot_estancias} estancias configuradas | **Superficie Afectada:** {st.session_state.superficie:.1f} m².")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b2:
        if st.button("Siguiente: 🛠️ 2. Cálculos Normativos ➔", key="btn_next_1"):
            st.session_state.paso_actual = 2
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 2: CÁLCULOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 2:
    st.subheader("🛠️ Paso 2: Dimensionado Técnico Normativo")

    with st.expander("⚡ **Cálculo Electrotécnico (REBT - RD 842/2002)**", expanded=True):
        if not st.session_state.inc_elec:
            st.caption("ℹ️ Capítulo de Electricidad marcado como NO INCLUIDO.")
        else:
            pot_kw = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
            long_m = st.number_input("Longitud Derivación Individual (m)", min_value=1.0, value=15.0, step=1.0)
            I_calc = (pot_kw * 1000) / (230 * 0.9)
            s_rec = max(6.0, (2 * long_m * (pot_kw * 1000)) / (56 * 3.45 * 230))
            st.success(f"✔️ **Intensidad:** {I_calc:.2f} A | **Sección Mínima DI:** {s_rec:.2f} mm² (Cu)")

    with st.expander("🚰 **Cálculo Hidráulico (CTE DB-HS4 / HS5)**", expanded=True):
        if not st.session_state.inc_font:
            st.caption("ℹ️ Capítulo de Fontanería marcado como NO INCLUIDO.")
        else:
            n_puntos = (st.session_state.n_banos * 3) + (st.session_state.n_aseos * 2) + (st.session_state.n_cocinas * 3) + (st.session_state.n_galerias * 2)
            caudal_tot = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40) + (st.session_state.n_galerias * 0.20)
            caudal_sim = caudal_tot * (1 / math.sqrt(max(1, n_puntos)))
            st.metric("Caudal Simultáneo de Diseño", f"{caudal_sim:.2f} L/s", f"{n_puntos} Puntos de Agua")

    with st.expander("❄️ **Cálculo Térmico (RITE - RD 1027/2007)**", expanded=True):
        if not st.session_state.inc_clima:
            st.caption("ℹ️ Capítulo de Climatización marcado como NO INCLUIDO.")
        else:
            p_kw = (st.session_state.superficie * 100) / 1000
            st.metric("Carga Térmica Estimada", f"{p_kw:.2f} kW", f"{p_kw * 860:.0f} Frigorías/h")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Paso Anterior: 📋 1. Estancias", key="btn_prev_2"):
            st.session_state.paso_actual = 1
            st.rerun()
    with col_b2:
        if st.button("Siguiente: 💶 3. Precios Unitarios ➔", key="btn_next_2"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 3: PRECIOS UNITARIOS (€0)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 3:
    st.subheader("💶 Paso 3: Tarifación y Cuadro de Precios (€0 de Inicio)")
    st.write("Establece los precios unitarios de cada capítulo antes de generar la liquidación final:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("#### ⚡ Electricidad")
        st.session_state.pu_elec_m2 = st.number_input("Instalación Eléctrica General (€/m²)", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0)
        st.session_state.pu_elec_cgmp = st.number_input("Cuadro CGMP y Protecciones (€/ud)", min_value=0.0, value=st.session_state.pu_elec_cgmp, step=25.0)

        st.markdown("#### 🚰 Fontanería")
        st.session_state.pu_font_bano = st.number_input("Instalación Baño (€/baño)", min_value=0.0, value=st.session_state.pu_font_bano, step=50.0)
        st.session_state.pu_font_cocina = st.number_input("Instalación Cocina (€/cocina)", min_value=0.0, value=st.session_state.pu_font_cocina, step=50.0)

    with col_p2:
        st.markdown("#### ❄️ Climatización")
        st.session_state.pu_clima_kw = st.number_input("Equipamiento Climatización RITE (€/kW)", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0)

        st.markdown("#### 📡 Telecomunicaciones")
        st.session_state.pu_teleco_toma = st.number_input("Toma de Datos RJ45 Cat6 (€/toma)", min_value=0.0, value=st.session_state.pu_teleco_toma, step=5.0)

        st.markdown("#### 🏗️ Albañilería")
        st.session_state.pu_albanil_m2 = st.number_input("Rozas, Ayuda y Remates (€/m²)", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0)

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Paso Anterior: 🛠️ 2. Cálculos", key="btn_prev_3"):
            st.session_state.paso_actual = 2
            st.rerun()
    with col_b2:
        if st.button("Siguiente: 📊 4. Presupuesto Final ➔", key="btn_next_3"):
            st.session_state.paso_actual = 4
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO Y EXCEL
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 4:
    st.subheader("📊 Paso 4: Estado de Mediciones y Presupuesto Comercial")

    sup = st.session_state.superficie
    n_banos = st.session_state.n_banos + st.session_state.n_aseos
    n_cocinas = st.session_state.n_cocinas + st.session_state.n_galerias
    tomas_teleco = (st.session_state.n_dormitorios + st.session_state.n_salones) * 2
    pot_clima = (sup * 100) / 1000 if sup > 0 else 0.0

    filas = []
    if st.session_state.inc_elec:
        filas.append({"Capítulo": "⚡ Electricidad", "Partida": "Instalación Eléctrica General (REBT)", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_elec_m2, "Importe (€)": sup * st.session_state.pu_elec_m2})
        filas.append({"Capítulo": "⚡ Electricidad", "Partida": "Cuadro CGMP y Protecciones", "Unidad": "ud", "Cantidad": 1 if sup > 0 else 0, "Precio Unitario (€)": st.session_state.pu_elec_cgmp, "Importe (€)": (1 if sup > 0 else 0) * st.session_state.pu_elec_cgmp})

    if st.session_state.inc_font:
        filas.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Desagües en Baños", "Unidad": "ud", "Cantidad": n_banos, "Precio Unitario (€)": st.session_state.pu_font_bano, "Importe (€)": n_banos * st.session_state.pu_font_bano})
        filas.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería en Cocina/Lavadero", "Unidad": "ud", "Cantidad": n_cocinas, "Precio Unitario (€)": st.session_state.pu_font_cocina, "Importe (€)": n_cocinas * st.session_state.pu_font_cocina})

    if st.session_state.inc_clima:
        filas.append({"Capítulo": "❄️ Climatización", "Partida": "Instalación Climatización RITE", "Unidad": "kW", "Cantidad": pot_clima, "Precio Unitario (€)": st.session_state.pu_clima_kw, "Importe (€)": pot_clima * st.session_state.pu_clima_kw})

    if st.session_state.inc_teleco:
        filas.append({"Capítulo": "📡 Telecomunicaciones", "Partida": "Red de Datos Cat6 e ICT2", "Unidad": "toma", "Cantidad": tomas_teleco, "Precio Unitario (€)": st.session_state.pu_teleco_toma, "Importe (€)": tomas_teleco * st.session_state.pu_teleco_toma})

    if st.session_state.inc_albanil:
        filas.append({"Capítulo": "🏗️ Albañilería", "Partida": "Rozas, Ayudas e Instalaciones", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_albanil_m2, "Importe (€)": sup * st.session_state.pu_albanil_m2})

    if filas:
        df_pres = pd.DataFrame(filas)
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
        cr1, cr2, cr3 = st.columns(3)
        cr1.metric("Base Imponible (Subtotal)", f"{sub:,.2f} €")
        cr2.metric(f"IVA ({tipo_iva}%)", f"{iva_val:,.2f} €")
        cr3.metric("TOTAL PRESUPUESTO", f"{tot_val:,.2f} €")

        st.markdown("---")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_pres.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')
            df_res = pd.DataFrame([
                {"Concepto": "Cliente / Empresa", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
                {"Concepto": "Dirección Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
                {"Concepto": "Base Imponible", "Valor": f"{sub:.2f} €"},
                {"Concepto": f"IVA ({tipo_iva}%)", "Valor": f"{iva_val:.2f} €"},
                {"Concepto": "Total Presupuesto", "Valor": f"{tot_val:.2f} €"}
            ])
            df_res.to_excel(writer, index=False, sheet_name='Resumen_Ejecutivo')

        st.download_button(
            label="🟢 Descargar Presupuesto Profesional en Excel (.xlsx)",
            data=output.getvalue(),
            file_name="Presupuesto_Tecnico_Reforma.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Selecciona al menos un capítulo en el menú lateral para ver el presupuesto.")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Paso Anterior: 💶 3. Precios", key="btn_prev_4"):
            st.session_state.paso_actual = 3
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == 5:
    st.subheader("📚 Paso 5: Biblioteca Técnica y Guía Normativa")
    st.write("Consulta rápida de la normativa aplicable en reformas e instalaciones en España:")

    tn1, tn2, tn3, tn4 = st.tabs(["⚡ REBT", "🚰 CTE DB-HS", "❄️ RITE", "📡 ICT2"])
    with tn1:
        st.markdown("### ⚡ REBT (RD 842/2002)")
        st.write("• ITC-BT-19: Caídas de tensión admisibles (máx. 3% en viviendas).")
        st.write("• ITC-BT-25: Circuitos mínimos C1, C2, C3, C4 y C5.")
    with tn2:
        st.markdown("### 🚰 CTE DB-HS4 / HS5")
        st.write("• Caudales instantáneos mínimos por aparato (Lavabo: 0.10 L/s, Ducha: 0.20 L/s).")
    with tn3:
        st.markdown("### ❄️ RITE (RD 1027/2007)")
        st.write("• Exigencias de rendimiento, aislamiento térmico y contabilización de consumos.")
    with tn4:
        st.markdown("### 📡 ICT2 (RD 346/2011)")
        st.write("• Canalización y red de datos Cat6 con PAU centralizado.")

    st.markdown("---")
    if st.button("⬅️ Volver a: 📋 1. Configuración de Estancias", key="btn_prev_5"):
        st.session_state.paso_actual = 1
        st.rerun()
