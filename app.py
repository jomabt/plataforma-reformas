import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA - SAAS COMERCIAL "PREMIUM LIGHT"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PRO-REFORMAS | Software Técnico y Presupuestos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DISEÑO VISUAL ATRACTIVO, ERGONÓMICO Y FRESCO (DISEÑO SAAS COMERCIAL MODERNO)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. Fondo general de la app */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 2. Barra lateral (Sidebar) clara, fresca y descansada */
    [data-testid="stSidebar"] {
        background-color: #F0F4FF !important; /* Soft Indigo Light Tint */
        border-right: 1px solid #C7D2FE !important;
        padding-top: 1.5rem;
    }
    
    [data-testid="stSidebar"] * {
        color: #1E1B4B !important; /* Azul/Indigo profundo para lectura óptima */
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #312E81 !important;
        font-weight: 800 !important;
    }

    /* 3. Estilo de los campos de entrada e inputs en el Sidebar y Cuerpo */
    input[type="text"], input[type="number"], .stSelectbox select, div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #A5B4FC !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }

    input:focus, div[data-baseweb="select"]:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }

    /* 4. Arreglo visual completo para botones de + y - (Step Buttons en Number Inputs) */
    div[data-testid="stNumberInput"] button {
        background-color: #E0E7FF !important;
        color: #3730A3 !important;
        border: 1.5px solid #A5B4FC !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stNumberInput"] button:hover {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border-color: #4F46E5 !important;
    }

    /* 5. Header de la aplicación estilo SaaS comercial moderno */
    .hero-saas {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4F46E5 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 14px;
        color: #FFFFFF;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #E0E7FF !important;
        font-size: 1.02rem;
        margin-top: 0.4rem;
    }

    /* 6. Botones de acción principales */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.2rem !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35) !important;
        background: linear-gradient(135deg, #4338CA 0%, #3730A3 100%) !important;
    }

    /* Labels de todo el sistema */
    label, div[data-baseweb="label"] {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA DE DATOS)
# -----------------------------------------------------------------------------
if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 0.0

# Cantidad de estancias completas
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
if 'inc_font' not in st.session_state: st.session_state.inc_font = False
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = False
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = False
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = False

# Precios Unitarios (€0 de inicio)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# HEADER DEL SOFTWARE
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-saas">
    <div>
        <div class="hero-title">⚡ PRO-REFORMAS | Gestor Técnico & Presupuestos</div>
        <div class="hero-subtitle">Plataforma SaaS para dimensionado normativo (REBT, CTE, RITE, ICT2) y ofertas comerciales de reformas.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR): CLARA, LUMINOSA Y DE ALTO CONTRASTE
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 👤 DATOS DEL CLIENTE Y OBRA")

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
st.sidebar.markdown("### 🔧 CAPÍTULOS INCLUIDOS")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Capítulo 1: Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Capítulo 2: Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Capítulo 3: Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Capítulo 4: Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Capítulo 5: Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox("Tipo de IVA Aplicable", [21, 10, 0], format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido' if x==10 else 'Exento'})")

# -----------------------------------------------------------------------------
# NAVEGACIÓN PRINCIPAL
# -----------------------------------------------------------------------------
menu_opcion = st.radio(
    "Navegación del Proyecto:",
    ["📋 1. Alcance y Estancias", "🛠️ 2. Cálculos Normativos", "💶 3. Cuadro de Precios (€0)", "📊 4. Presupuesto Final y Excel", "📚 5. Biblioteca Normativa"],
    horizontal=True
)

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVEGACIÓN 1: ALCANCE Y ESTANCIAS COMPLETA
# -----------------------------------------------------------------------------
if menu_opcion == "📋 1. Alcance y Estancias":
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría")
    st.write("Indica la cantidad de cada tipo de estancia para determinar las necesidades mínimas normativas del proyecto.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state.n_dormitorios = st.number_input("Dormitorios", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_salones = st.number_input("Salones / Comedores", min_value=0, value=st.session_state.n_salones, step=1)
    with col2:
        st.session_state.n_banos = st.number_input("Baños Completos", min_value=0, value=st.session_state.n_banos, step=1)
        st.session_state.n_aseos = st.number_input("Aseos (Sin Ducha)", min_value=0, value=st.session_state.n_aseos, step=1)
    with col3:
        st.session_state.n_cocinas = st.number_input("Cocinas", min_value=0, value=st.session_state.n_cocinas, step=1)
        st.session_state.n_galerias = st.number_input("Galerías / Lavaderos", min_value=0, value=st.session_state.n_galerias, step=1)
    with col4:
        st.session_state.n_terrazas = st.number_input("Terrazas / Balcones", min_value=0, value=st.session_state.n_terrazas, step=1)
        st.session_state.n_trasteros = st.number_input("Trasteros / Garajes", min_value=0, value=st.session_state.n_trasteros, step=1)

    estancias_totales = (
        st.session_state.n_dormitorios + st.session_state.n_salones + 
        st.session_state.n_banos + st.session_state.n_aseos + 
        st.session_state.n_cocinas + st.session_state.n_galerias + 
        st.session_state.n_terrazas + st.session_state.n_trasteros
    )
    
    st.info(f"💡 **Resumen del Inmueble:** {estancias_totales} estancias/zonas configuradas | **Superficie Afectada:** {st.session_state.superficie:.1f} m².")

# -----------------------------------------------------------------------------
# NAVEGACIÓN 2: CÁLCULOS NORMATIVOS
# -----------------------------------------------------------------------------
elif menu_opcion == "🛠️ 2. Cálculos Normativos":
    st.subheader("🛠️ Paso 2: Dimensionado Técnico de Instalaciones")
    st.write("Cálculos ingenieriles automáticos ajustados a las normativas españolas (REBT, CTE DB-HS, RITE e ICT2).")

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
            s_rec = max(6.0, s_min)
            st.success(f"✔️ **Intensidad Nominal:** {I_calc:.2f} A | **Sección Mínima Calculada DI:** {s_rec:.2f} mm² (Cu)")

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
            st.info("Configura los baños y cocinas en el Paso 1 para calcular el caudal hidráulico.")

    with st.expander("❄️ **Cálculo Térmico y Climatización (RITE - RD 1027/2007)**", expanded=True):
        if not st.session_state.inc_clima:
            st.caption("ℹ️ Capítulo de Climatización marcado como NO INCLUIDO.")
        if st.session_state.superficie > 0:
            zona = st.selectbox("Calidad Térmica / Aislamiento", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_kw = (st.session_state.superficie * w_m2) / 1000
            frig = p_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie útil en el menú lateral para calcular la potencia térmica.")

# -----------------------------------------------------------------------------
# NAVEGACIÓN 3: CUADRO DE PRECIOS UNITARIOS
# -----------------------------------------------------------------------------
elif menu_opcion == "💶 3. Cuadro de Precios (€0)":
    st.subheader("💶 Paso 3: Tarifación y Cuadro de Precios Unitarios")
    st.write("⚠️ **Todos los precios inician en 0.00 €.** Define los precios unitarios convenidos para cada partida.")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### ⚡ Capítulo 1: Electricidad")
        st.session_state.pu_elec_m2 = st.number_input("Instalación Eléctrica General (€/m²)", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0)
        st.session_state.pu_elec_cgmp = st.number_input("Cuadro CGMP y Protecciones (€/ud)", min_value=0.0, value=st.session_state.pu_elec_cgmp, step=25.0)

        st.markdown("#### 🚰 Capítulo 2: Fontanería")
        st.session_state.pu_font_bano = st.number_input("Instalación Completa Baño (€/baño)", min_value=0.0, value=st.session_state.pu_font_bano, step=50.0)
        st.session_state.pu_font_cocina = st.number_input("Instalación Completa Cocina (€/cocina)", min_value=0.0, value=st.session_state.pu_font_cocina, step=50.0)

    with col_p2:
        st.markdown("#### ❄️ Capítulo 3: Climatización")
        st.session_state.pu_clima_kw = st.number_input("Instalación Climatización RITE (€/kW)", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0)

        st.markdown("#### 📡 Capítulo 4: Telecomunicaciones")
        st.session_state.pu_teleco_toma = st.number_input("Toma de Datos RJ45 Cat6 (€/toma)", min_value=0.0, value=st.session_state.pu_teleco_toma, step=5.0)

        st.markdown("#### 🏗️ Capítulo 5: Albañilería Auxiliar")
        st.session_state.pu_albanil_m2 = st.number_input("Rozas, Ayuda y Tapado (€/m²)", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0)

# -----------------------------------------------------------------------------
# NAVEGACIÓN 4: PRESUPUESTO FINAL Y EXCEL
# -----------------------------------------------------------------------------
elif menu_opcion == "📊 4. Presupuesto Final y Excel":
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
        st.info("👉 Selecciona al menos un capítulo en la barra lateral izquierda para generar el cuadro de presupuesto.")

# -----------------------------------------------------------------------------
# NAVEGACIÓN 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
elif menu_opcion == "📚 5. Biblioteca Normativa":
    st.subheader("📚 Biblioteca Técnica y Referencias Normativas")
    st.write("Compendio normativo de consulta para proyectos técnicos e instalaciones.")

    tab_n1, tab_n2, tab_n3, tab_n4 = st.tabs(["⚡ REBT (Electricidad)", "🚰 CTE DB-HS (Fontanería)", "❄️ RITE (Climatización)", "📡 ICT2 (Telecomunicaciones)"])

    with tab_n1:
        st.markdown("### ⚡ Reglamento Electrotécnico para Baja Tensión (REBT)")
        st.write("• **ITC-BT-25:** Define los circuitos C1 (iluminación), C2 (enchufes generales), C3 (cocina/horno), C4 (lavadora/lavavajillas/termo) y C5 (baños/auxiliares).")
        st.write("• **Límite de Caída de Tensión:** Máximo 1.5% en derivación individual y 3% en instalaciones interiores.")

    with tab_n2:
        st.markdown("### 🚰 Código Técnico de la Edificación (CTE DB-HS4/HS5)")
        st.write("• **Caudales Mínimos:** Lavabo: 0.10 L/s | Ducha: 0.20 L/s | Fregadero: 0.20 L/s.")
        st.write("• **Presión de Servicio:** Mínima 1 bar, máxima 5 bar.")

    with tab_n3:
        st.markdown("### ❄️ Reglamento de Instalaciones Térmicas (RITE)")
        st.write("• **Mantenimiento y Eficiencia:** Obligatoriedad de regulación por termostato y contabilización de consumos.")

    with tab_n4:
        st.markdown("### 📡 Infraestructuras de Telecomunicaciones (ICT2)")
        st.write("• **Redes:** Par trenzado Cat6, Fibra Óptica (FTTH) y Coaxial. Instalación de PAU centralizado.")
