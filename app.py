import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA - SAAS PROFESIONAL DE INGENIERÍA Y REFORMAS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PRO-REFORMAS | Software de Cálculo Técnico y Presupuestos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alto contraste y acabado SaaS comercial (Slate & Tech Blue)
st.markdown("""
<style>
    /* Estructura general */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Encabezado principal estilo Software Profesional */
    .saas-header {
        background-color: #0F172A;
        border-left: 6px solid #2563EB;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .saas-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .saas-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    
    /* Tarjetas de parámetros y módulos */
    .module-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .module-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
    }
    
    /* Garantía de legibilidad en etiquetas y números */
    label {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* Botones de acción */
    .stButton>button {
        background-color: #2563EB;
        color: #FFFFFF;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA DE DATOS)
# -----------------------------------------------------------------------------
if 'cliente_nombre' not in st.session_state: st.session_state.cliente_nombre = ""
if 'cliente_obra' not in st.session_state: st.session_state.cliente_obra = ""
if 'superficie' not in st.session_state: st.session_state.superficie = 0.0

# Cantidad de estancias
if 'n_dormitorios' not in st.session_state: st.session_state.n_dormitorios = 0
if 'n_banos' not in st.session_state: st.session_state.n_banos = 0
if 'n_salones' not in st.session_state: st.session_state.n_salones = 0
if 'n_aseos' not in st.session_state: st.session_state.n_aseos = 0
if 'n_cocinas' not in st.session_state: st.session_state.n_cocinas = 0

# Toggles de Alcance por Especialidad (Persistentes)
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
<div class="saas-header">
    <div class="saas-title">⚡ PRO-REFORMAS | Software de Cálculo & Presupuestos</div>
    <div class="saas-subtitle">Plataforma SaaS profesional para dimensionado normativo (REBT, CTE, RITE, ICT2) y medición de obras.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL: DATOS DE PROYECTO Y RESUMEN FINANCIERO
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ⚙️ Datos del Proyecto")
st.session_state.cliente_nombre = st.sidebar.text_input("Cliente / Referencia", value=st.session_state.cliente_nombre, placeholder="Ej. D. Juan Martínez")
st.session_state.cliente_obra = st.sidebar.text_input("Ubicación de la Obra", value=st.session_state.cliente_obra, placeholder="Ej. Av. Constitución 45, Barcelona")
st.session_state.superficie = st.sidebar.number_input("Superficie Útil (m²)", min_value=0.0, value=st.session_state.superficie, step=5.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Capítulos Incluidos")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Capítulo 1: Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Capítulo 2: Fontanería (CTE DB-HS)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Capítulo 3: Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Capítulo 4: Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Capítulo 5: Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
tipo_iva = st.sidebar.selectbox("Tipo de IVA", [21, 10, 0], format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido' if x==10 else 'Exento'})")

# -----------------------------------------------------------------------------
# NAVEGACIÓN PRINCIPAL
# -----------------------------------------------------------------------------
menu_opcion = st.radio(
    "Navegación:",
    ["📋 1. Alcance y Estancias", "🛠️ 2. Cálculos Normativos", "💶 3. Cuadro de Precios (€0)", "📊 4. Presupuesto Final y Excel", "📚 5. Biblioteca Normativa"],
    horizontal=True
)

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVEGACIÓN 1: ALCANCE Y ESTANCIAS
# -----------------------------------------------------------------------------
if menu_opcion == "📋 1. Alcance y Estancias":
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría")
    st.write("Indica la cantidad de estancias para determinar las necesidades mínimas de puntos de luz, agua y telecomunicaciones.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.n_dormitorios = st.number_input("Dormitorios", min_value=0, value=st.session_state.n_dormitorios, step=1)
        st.session_state.n_banos = st.number_input("Baños Completos", min_value=0, value=st.session_state.n_banos, step=1)
    with col2:
        st.session_state.n_salones = st.number_input("Salones / Comedores", min_value=0, value=st.session_state.n_salones, step=1)
        st.session_state.n_aseos = st.number_input("Aseos (Sin Ducha)", min_value=0, value=st.session_state.n_aseos, step=1)
    with col3:
        st.session_state.n_cocinas = st.number_input("Cocinas", min_value=0, value=st.session_state.n_cocinas, step=1)

    estancias_totales = st.session_state.n_dormitorios + st.session_state.n_salones + st.session_state.n_banos + st.session_state.n_aseos + st.session_state.n_cocinas
    
    st.info(f"💡 **Resumen del Inmueble:** {estancias_totales} estancias totales | **Superficie Afectada:** {st.session_state.superficie:.1f} m².")

# -----------------------------------------------------------------------------
# NAVEGACIÓN 2: CÁLCULOS NORMATIVOS
# -----------------------------------------------------------------------------
elif menu_opcion == "🛠️ 2. Cálculos Normativos":
    st.subheader("🛠️ Paso 2: Dimensionado Técnico de Instalaciones")
    st.write("Cálculos ingenieriles automáticos ajustados a las normativas vigentes en España.")

    # Electricidad REBT
    with st.expander("⚡ **Cálculo Electrotécnico (REBT - RD 842/2002)**", expanded=True):
        if not st.session_state.inc_elec:
            st.caption("ℹ️ Capítulo de Electricidad marcado como NO INCLUIDO en el presupuesto actual.")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            electrificacion = st.selectbox("Nivel de Electrificación", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
            potencia_kw = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
        with col_e2:
            longitud_m = st.number_input("Longitud Derivación Individual (m)", min_value=0.0, value=15.0, step=1.0)
            
            # Motor de cálculo
            I_calc = (potencia_kw * 1000) / (230 * 0.9)
            cd_max = 230 * 0.015
            s_min = (2 * longitud_m * (potencia_kw * 1000)) / (56 * cd_max * 230)
            s_rec = max(6.0, s_min)
            st.success(f"✔️ **Intensidad Nominal:** {I_calc:.2f} A | **Sección Mínima Calculada DI:** {s_rec:.2f} mm² (Cu)")

    # Fontanería CTE DB-HS
    with st.expander("🚰 **Cálculo Hidráulico y Saneamiento (CTE DB-HS4 / HS5)**", expanded=True):
        if not st.session_state.inc_font:
            st.caption("ℹ️ Capítulo de Fontanería marcado como NO INCLUIDO en el presupuesto actual.")
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

    # Climatización RITE
    with st.expander("❄️ **Cálculo Térmico y Climatización (RITE - RD 1027/2007)**", expanded=True):
        if not st.session_state.inc_clima:
            st.caption("ℹ️ Capítulo de Climatización marcado como NO INCLUIDO en el presupuesto actual.")
        if st.session_state.superficie > 0:
            zona = st.selectbox("Calidad Térmica / Aislamiento", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_kw = (st.session_state.superficie * w_m2) / 1000
            frig = p_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie en el menú lateral para calcular la carga térmica.")

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

        # Generación de Excel Profesional
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
""",TargetFile:
