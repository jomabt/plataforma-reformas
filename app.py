import streamlit as st
import pandas as pd
import math
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gestor Profesional de Reformas y Presupuestos",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS ligeros y no invasivos para garantizar legibilidad perfecta
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .info-card {
        background-color: #F1F5F9;
        border-left: 5px solid #2563EB;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">🏢 Gestor Profesional de Reformas e Instalaciones</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plataforma SaaS para cálculo normativo de instalaciones (REBT, CTE, RITE, ICT2) y presupuestación comercial.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN (PERSISTENCIA)
# -----------------------------------------------------------------------------
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

# Especialidades activas
if 'inc_elec' not in st.session_state: st.session_state.inc_elec = True
if 'inc_font' not in st.session_state: st.session_state.inc_font = True
if 'inc_clima' not in st.session_state: st.session_state.inc_clima = False
if 'inc_teleco' not in st.session_state: st.session_state.inc_teleco = False
if 'inc_albanil' not in st.session_state: st.session_state.inc_albanil = True

# Precios Unitarios (Inician en 0.00 €)
if 'pu_elec_m2' not in st.session_state: st.session_state.pu_elec_m2 = 0.0
if 'pu_elec_cgmp' not in st.session_state: st.session_state.pu_elec_cgmp = 0.0
if 'pu_font_bano' not in st.session_state: st.session_state.pu_font_bano = 0.0
if 'pu_font_cocina' not in st.session_state: st.session_state.pu_font_cocina = 0.0
if 'pu_clima_kw' not in st.session_state: st.session_state.pu_clima_kw = 0.0
if 'pu_teleco_toma' not in st.session_state: st.session_state.pu_teleco_toma = 0.0
if 'pu_albanil_m2' not in st.session_state: st.session_state.pu_albanil_m2 = 0.0

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.header("👤 Datos del Cliente y Obra")
st.session_state.cliente_nombre = st.sidebar.text_input("Nombre del Cliente / Empresa", value=st.session_state.cliente_nombre, placeholder="Ej. D. Antonio López")
st.session_state.cliente_obra = st.sidebar.text_input("Dirección / Ubicación de la Obra", value=st.session_state.cliente_obra, placeholder="Ej. Av. Constitución 45, Castelldefels")
st.session_state.superficie = st.sidebar.number_input("Superficie Útil Afectada (m²)", min_value=0.0, value=st.session_state.superficie, step=5.0)

st.sidebar.markdown("---")
st.sidebar.header("🔧 Especialidades Incluidas")
st.session_state.inc_elec = st.sidebar.checkbox("⚡ Electricidad (REBT)", value=st.session_state.inc_elec)
st.session_state.inc_font = st.sidebar.checkbox("🚰 Fontanería y Saneamiento (CTE)", value=st.session_state.inc_font)
st.session_state.inc_clima = st.sidebar.checkbox("❄️ Climatización (RITE)", value=st.session_state.inc_clima)
st.session_state.inc_teleco = st.sidebar.checkbox("📡 Telecomunicaciones (ICT2)", value=st.session_state.inc_teleco)
st.session_state.inc_albanil = st.sidebar.checkbox("🏗️ Albañilería Auxiliar", value=st.session_state.inc_albanil)

st.sidebar.markdown("---")
st.sidebar.header("💶 Configuración Financiera")
tipo_iva = st.sidebar.selectbox("Tipo de IVA Aplicable", [21, 10, 0], format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})")

# -----------------------------------------------------------------------------
# NAVEGACIÓN EN PESTAÑAS (TABS)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 1. Estancias y Alcance", 
    "🛠️ 2. Dimensionado Técnico", 
    "💶 3. Precios Unitarios (€0)", 
    "📊 4. Presupuesto y Exportación",
    "📚 5. Biblioteca Normativa"
])

# -----------------------------------------------------------------------------
# TAB 1: ESTANCIAS Y ALCANCE
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría")
    st.write("Indica la cantidad de cada estancia para determinar las cargas de instalación necesarias:")
    
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
        st.session_state.n_trasteros = st.number_input("Trasteros / Garajes / Otros", min_value=0, value=st.session_state.n_trasteros, step=1)

    estancias_totales = (
        st.session_state.n_dormitorios + st.session_state.n_salones + 
        st.session_state.n_banos + st.session_state.n_aseos + 
        st.session_state.n_cocinas + st.session_state.n_galerias + 
        st.session_state.n_terrazas + st.session_state.n_trasteros
    )
    
    st.info(f"💡 **Resumen del Inmueble:** {estancias_totales} estancias/zonas configuradas para una superficie de **{st.session_state.superficie:.1f} m²**.")

# -----------------------------------------------------------------------------
# TAB 2: DIMENSIONADO TÉCNICO
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("🛠️ Paso 2: Cálculos y Dimensionado Técnico")
    st.write("Cálculos normativos automáticos basados en las reglamentaciones vigentes:")

    with st.expander("⚡ **Instalación Eléctrica (REBT - RD 842/2002)**", expanded=st.session_state.inc_elec):
        if not st.session_state.inc_elec:
            st.warning("Especialidad de Electricidad desactivada en el menú lateral.")
        else:
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                electrificacion = st.selectbox("Nivel de Electrificación", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])
                potencia_kw = st.selectbox("Potencia Recomendada (kW)", [3.45, 4.60, 5.75, 7.36, 9.20], index=2)
            with col_e2:
                longitud_di = st.number_input("Longitud Derivación Individual (m)", min_value=0.0, value=15.0, step=1.0)
                I_calc = (potencia_kw * 1000) / (230 * 0.9)
                cd_max = 230 * 0.015
                s_min = (2 * longitud_di * (potencia_kw * 1000)) / (56 * cd_max * 230)
                st.success(f"✔️ **Intensidad de Cálculo:** {I_calc:.2f} A | **Sección Mínima Cable DI:** {max(6.0, s_min):.2f} mm²")

            st.markdown("**Circuitos exigidos para la vivienda:**")
            circuitos = [
                {"Circuito": "C1 - Iluminación", "Sección": "1.5 mm²", "PIA": "10A", "Uso": "Puntos de luz y alumbrado"},
                {"Circuito": "C2 - Tomas uso general", "Sección": "2.5 mm²", "PIA": "16A", "Uso": "Tomas generales y frigorífico"},
                {"Circuito": "C3 - Cocina y Horno", "Sección": "6.0 mm²", "PIA": "25A", "Uso": "Vitrocerámica y horno"},
                {"Circuito": "C4 - Lavadora / Lavavajillas / Termo", "Sección": "2.5 mm²", "PIA": "20A", "Uso": "Electrodomésticos de potencia"},
                {"Circuito": "C5 - Baños y aux. cocina", "Sección": "2.5 mm²", "PIA": "16A", "Uso": "Tomas húmedas y encimera"}
            ]
            if "Elevada" in electrificacion:
                circuitos.append({"Circuito": "C8/C9 - Climatización / Calefacción", "Sección": "6.0 mm²", "PIA": "25A", "Uso": "Aire acondicionado / calefacción"})
            st.dataframe(pd.DataFrame(circuitos), use_container_width=True)

    with st.expander("🚰 **Fontanería y Saneamiento (CTE DB-HS4 / HS5)**", expanded=st.session_state.inc_font):
        if not st.session_state.inc_font:
            st.warning("Especialidad de Fontanería desactivada en el menú lateral.")
        else:
            n_humedas = st.session_state.n_banos + st.session_state.n_aseos + st.session_state.n_cocinas + st.session_state.n_galerias
            if n_humedas > 0:
                caudal_total = (st.session_state.n_banos * 0.35) + (st.session_state.n_aseos * 0.20) + (st.session_state.n_cocinas * 0.40) + (st.session_state.n_galerias * 0.20)
                coef_simult = 1 / math.sqrt(max(1, n_humedas * 2))
                caudal_diseno = caudal_total * coef_simult
                
                c_f1, c_f2 = st.columns(2)
                c_f1.metric("Caudal Total Instalado", f"{caudal_total:.2f} L/s")
                c_f2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
            else:
                st.info("Configura baños, cocinas o galerías en el Paso 1 para ver el cálculo de caudal.")

    with st.expander("❄️ **Climatización y Calefacción (RITE)**", expanded=st.session_state.inc_clima):
        if not st.session_state.inc_clima:
            st.warning("Especialidad de Climatización desactivada en el menú lateral.")
        else:
            if st.session_state.superficie > 0:
                zona = st.selectbox("Calidad de Aislamiento / Zona Climática", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
                w_m2 = int(zona.split("(")[1].split(" W")[0])
                p_kw = (st.session_state.superficie * w_m2) / 1000
                frig = p_kw * 860
                st.metric("Potencia Térmica Necesaria", f"{p_kw:.2f} kW", f"{frig:.0f} Frigorías/h")
            else:
                st.info("Introduce la superficie en el menú lateral para calcular cargas térmicas.")

    with st.expander("📡 **Telecomunicaciones (ICT2) y Redes LAN**", expanded=st.session_state.inc_teleco):
        if not st.session_state.inc_teleco:
            st.warning("Especialidad de Telecomunicaciones desactivada en el menú lateral.")
        else:
            tomas_teleco = (st.session_state.n_dormitorios + st.session_state.n_salones) * 2
            st.write(f"• **Tomas de Datos RJ45 Cat6 recomendadas:** {tomas_teleco} tomas en zonas principales.")
            st.write("• **Punto de Acceso al Usuario (PAU):** Envolvente empotrada con toma de corriente.")

# -----------------------------------------------------------------------------
# TAB 3: PRECIOS UNITARIOS (€0)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("💶 Paso 3: Asignación de Precios Unitarios")
    st.write("⚠️ **Todos los precios unitarios comienzan en 0.00 €.** Introduce tus tarifas de mano de obra y materiales para cada partida:")

    st.markdown("---")
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        if st.session_state.inc_elec:
            st.markdown("#### ⚡ Partidas de Electricidad")
            st.session_state.pu_elec_m2 = st.number_input("Precio Renovación Eléctrica (€ / m²)", min_value=0.0, value=st.session_state.pu_elec_m2, step=5.0, format="%.2f")
            st.session_state.pu_elec_cgmp = st.number_input("Precio Cuadro General (CGMP) (€ / ud)", min_value=0.0, value=st.session_state.pu_elec_cgmp, step=25.0, format="%.2f")

        if st.session_state.inc_font:
            st.markdown("#### 🚰 Partidas de Fontanería")
            st.session_state.pu_font_bano = st.number_input("Precio Fontanería Baño Completo (€ / baño)", min_value=0.0, value=st.session_state.pu_font_bano, step=50.0, format="%.2f")
            st.session_state.pu_font_cocina = st.number_input("Precio Fontanería Cocina (€ / cocina)", min_value=0.0, value=st.session_state.pu_font_cocina, step=50.0, format="%.2f")

    with col_p2:
        if st.session_state.inc_clima:
            st.markdown("#### ❄️ Partidas de Climatización")
            st.session_state.pu_clima_kw = st.number_input("Precio Instalación Climatización RITE (€ / kW)", min_value=0.0, value=st.session_state.pu_clima_kw, step=25.0, format="%.2f")

        if st.session_state.inc_teleco:
            st.markdown("#### 📡 Partidas de Telecomunicaciones")
            st.session_state.pu_teleco_toma = st.number_input("Precio Toma de Datos Cat6 e ICT2 (€ / toma)", min_value=0.0, value=st.session_state.pu_teleco_toma, step=5.0, format="%.2f")

        if st.session_state.inc_albanil:
            st.markdown("#### 🏗️ Partidas de Albañilería Auxiliar")
            st.session_state.pu_albanil_m2 = st.number_input("Precio Rozas, Ayuda y Sellados (€ / m²)", min_value=0.0, value=st.session_state.pu_albanil_m2, step=5.0, format="%.2f")

# -----------------------------------------------------------------------------
# TAB 4: PRESUPUESTO Y EXPORTACIÓN
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("📊 Paso 4: Estado de Mediciones y Presupuesto General")

    sup = st.session_state.superficie
    n_banos = st.session_state.n_banos + st.session_state.n_aseos
    n_cocinas = st.session_state.n_cocinas
    tomas_teleco_calc = (st.session_state.n_dormitorios + st.session_state.n_salones) * 2
    potencia_clima_calc = (sup * 100) / 1000 if sup > 0 else 0.0

    filas_presupuesto = []

    if st.session_state.inc_elec:
        filas_presupuesto.append({"Capítulo": "⚡ Electricidad", "Partida": "Instalación Eléctrica General en Vivienda", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_elec_m2, "Importe (€)": sup * st.session_state.pu_elec_m2})
        filas_presupuesto.append({"Capítulo": "⚡ Electricidad", "Partida": "Cuadro General de Mando y Protecciones (CGMP)", "Unidad": "ud", "Cantidad": 1 if sup > 0 else 0, "Precio Unitario (€)": st.session_state.pu_elec_cgmp, "Importe (€)": (1 if sup > 0 else 0) * st.session_state.pu_elec_cgmp})

    if st.session_state.inc_font:
        filas_presupuesto.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Saneamiento en Baños", "Unidad": "ud", "Cantidad": n_banos, "Precio Unitario (€)": st.session_state.pu_font_bano, "Importe (€)": n_banos * st.session_state.pu_font_bano})
        filas_presupuesto.append({"Capítulo": "🚰 Fontanería", "Partida": "Instalación Fontanería y Desagües en Cocina", "Unidad": "ud", "Cantidad": n_cocinas, "Precio Unitario (€)": st.session_state.pu_font_cocina, "Importe (€)": n_cocinas * st.session_state.pu_font_cocina})

    if st.session_state.inc_clima:
        filas_presupuesto.append({"Capítulo": "❄️ Climatización", "Partida": "Equipamiento Climatización RITE", "Unidad": "kW", "Cantidad": potencia_clima_calc, "Precio Unitario (€)": st.session_state.pu_clima_kw, "Importe (€)": potencia_clima_calc * st.session_state.pu_clima_kw})

    if st.session_state.inc_teleco:
        filas_presupuesto.append({"Capítulo": "📡 Telecomunicaciones", "Partida": "Red de Datos Cat6 e Instalación ICT2", "Unidad": "toma", "Cantidad": tomas_teleco_calc, "Precio Unitario (€)": st.session_state.pu_teleco_toma, "Importe (€)": tomas_teleco_calc * st.session_state.pu_teleco_toma})

    if st.session_state.inc_albanil:
        filas_presupuesto.append({"Capítulo": "🏗️ Albañilería", "Partida": "Rozas, Ayuda a Instalaciones y Sellados", "Unidad": "m²", "Cantidad": sup, "Precio Unitario (€)": st.session_state.pu_albanil_m2, "Importe (€)": sup * st.session_state.pu_albanil_m2})

    if filas_presupuesto:
        df_presupuesto = pd.DataFrame(filas_presupuesto)
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
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Base Imponible (Subtotal)", f"{subtotal:,.2f} €")
        col_res2.metric(f"IVA ({tipo_iva}%)", f"{impuesto:,.2f} €")
        col_res3.metric("TOTAL PRESUPUESTO", f"{total:,.2f} €")

        st.markdown("---")
        st.subheader("📥 Exportación del Presupuesto Comercial")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_presupuesto.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')

            df_resumen = pd.DataFrame([
                {"Concepto": "Cliente / Empresa", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
                {"Concepto": "Dirección de Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
                {"Concepto": "Superficie Útil", "Valor": f"{sup} m²"},
                {"Concepto": "Subtotal (Base Imponible)", "Valor": f"{subtotal:.2f} €"},
                {"Concepto": f"IVA ({tipo_iva}%)", "Valor": f"{impuesto:.2f} €"},
                {"Concepto": "Total Presupuesto", "Valor": f"{total:.2f} €"}
            ])
            df_resumen.to_excel(writer, index=False, sheet_name='Resumen_Ejecutivo')

        excel_data = output.getvalue()
        nombre_archivo = f"Presupuesto_{(st.session_state.cliente_nombre if st.session_state.cliente_nombre else 'Reforma').replace(' ', '_')}.xlsx"

        st.download_button(
            label="🟢 Descargar Presupuesto en Excel (.xlsx)",
            data=excel_data,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("👉 Activa al menos una especialidad en el menú lateral para generar el cuadro de presupuesto.")

# -----------------------------------------------------------------------------
# TAB 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("📚 Biblioteca de Referencias Normativas")
    st.write("Compendio de reglamentación oficial técnica para consulta durante el proyecto:")

    t_n1, t_n2, t_n3, t_n4 = st.tabs(["⚡ REBT (Electricidad)", "🚰 CTE DB-HS (Fontanería)", "❄️ RITE (Climatización)", "📡 ICT2 (Telecomunicaciones)"])

    with t_n1:
        st.markdown("### ⚡ Reglamento Electrotécnico para Baja Tensión (REBT - RD 842/2002)")
        st.write("• **ITC-BT-25:** Define los 5 circuitos básicos para vivienda (C1 Iluminación, C2 Tomas Uso General, C3 Cocina/Horno, C4 Lavadora/Termo, C5 Baños/Auxiliares).")
        st.write("• **Caída de Tensión:** Máximo 1.5% en Derivaciones Individuales y 3% en instalaciones interiores.")

    with t_n2:
        st.markdown("### 🚰 Código Técnico de la Edificación - Salubridad (CTE DB-HS4/HS5)")
        st.write("• **Caudales Mínimos:** Lavabo: 0.10 L/s | Ducha: 0.20 L/s | Fregadero: 0.20 L/s.")
        st.write("• **Presión de Servicio:** Mínima 1 bar (100 kPa) y máxima 5 bar (500 kPa).")

    with t_n3:
        st.markdown("### ❄️ Reglamento de Instalaciones Térmicas en los Edificios (RITE)")
        st.write("• **Eficiencia Térmica:** Regulación por termostato por zonas y mantenimiento preventivo periódico.")

    with t_n4:
        st.markdown("### 📡 Infraestructuras Comunes de Telecomunicaciones (ICT2 - RD 346/2011)")
        st.write("• **Redes Exigidas:** Fibra Óptica (FTTH), Cobre Cat6 y Coaxial para TV/SAT con PAU centralizado
