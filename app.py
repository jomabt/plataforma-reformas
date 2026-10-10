import streamlit as st
import pandas as pd
import math
import io

# Configuración de página con diseño moderno e intuitivo
st.set_page_config(
    page_title="Gestor Inteligente de Reformas y Presupuestos",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para mejorar la legibilidad y UX humana
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .stNumberInput input {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏡 Gestor Inteligente de Reformas y Presupuestos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Configuración guiada paso a paso para cálculo técnico de instalaciones y elaboración de presupuestos.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR: DATOS GENERALES Y CONFIGURACIÓN
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Configuración del Proyecto")

nombre_proyecto = st.sidebar.text_input("Nombre del Proyecto / Cliente", value="", placeholder="Ej. Reforma Vivienda C/ Mayor")
superficie = st.sidebar.number_input("Superficie Útil de la Vivienda (m²)", min_value=0.0, value=0.0, step=5.0, help="Indica los m² útiles para estimar las necesidades básicas de la instalación")

st.sidebar.markdown("---")
st.sidebar.subheader("💶 Ajustes Financieros")
tipo_iva = st.sidebar.selectbox("Tipo de IVA aplicable", [21, 10, 0], format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})")

# -----------------------------------------------------------------------------
# FLUJO DE TRABAJO PRINCIPAL (PASO A PASO)
# -----------------------------------------------------------------------------

tab_paso1, tab_paso2, tab_paso3, tab_paso4 = st.tabs([
    "1️⃣ Definición de Estancias", 
    "🛠️ 2. Dimensionado Técnico", 
    "💶 3. Precios Unitarios (€0 de inicio)", 
    "📊 4. Presupuesto y Exportación"
])

# -----------------------------------------------------------------------------
# TAB 1: DEFINICIÓN DE ESTANCIAS Y ALCANCE
# -----------------------------------------------------------------------------
with tab_paso1:
    st.subheader("📋 Paso 1: Configura las Estancias de la Vivienda")
    st.write("Indica la cantidad de cada estancia para determinar automáticamente los puntos de luz, tomas de agua y redes de datos requeridos.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_dormitorios = st.number_input("Número de Dormitorios", min_value=0, value=0, step=1)
        num_banos = st.number_input("Número de Baños Completos", min_value=0, value=0, step=1)
    with col2:
        num_salones = st.number_input("Número de Salones / Comedores", min_value=0, value=0, step=1)
        num_aseos = st.number_input("Número de Aseos (Sin ducha)", min_value=0, value=0, step=1)
    with col3:
        num_cocinas = st.number_input("Número de Cocinas", min_value=0, value=0, step=1)
        num_terrazas = st.number_input("Terrazas / Trasteros / Garaje", min_value=0, value=0, step=1)

    estancias_totales = num_dormitorios + num_salones + num_banos + num_aseos + num_cocinas + num_terrazas
    
    st.info(f"💡 **Resumen del Inmueble:** {estancias_totales} estancias configuradas para una superficie de {superficie:.1f} m².")

# -----------------------------------------------------------------------------
# TAB 2: DIMENSIONADO TÉCNICO SIMPLIFICADO
# -----------------------------------------------------------------------------
with tab_paso2:
    st.subheader("🛠️ Paso 2: Cálculo y Dimensionado Técnico")
    st.write("Cálculos normativos automatizados basados en el REBT, CTE DB-HS, RITE e ICT2.")
    
    with st.expander("⚡ **Instalación Eléctrica (REBT - Regla Electrotécnica)**", expanded=True):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            electrificacion = st.selectbox(
                "Nivel de Electrificación", 
                ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"],
                help="Básica: consumo estándar. Elevada: si hay aire acondicionado por conductos, secadora o calefacción eléctrica."
            )
            p_contratada = st.selectbox("Potencia Recomendada de Cálculo (kW)", [0.0, 3.45, 4.6, 5.75, 7.36, 9.2], index=0)
        with col_e2:
            longitud_di = st.number_input("Longitud Derivación Individual (m)", min_value=0.0, value=0.0, step=1.0)
            if p_contratada > 0 and longitud_di > 0:
                I_calc = (p_contratada * 1000) / (230 * 0.9)
                cd_max = 230 * 0.015
                s_min = (2 * longitud_di * (p_contratada * 1000)) / (56 * cd_max * 230)
                st.success(f"✔️ **Intensidad de cálculo:** {I_calc:.2f} A | **Sección Mínima Cable DI:** {max(6.0, s_min):.2f} mm²")
            else:
                st.caption("Introduce la potencia y longitud para ver la sección recomendada del cable.")
        
        st.markdown("**Circuitos exigidos para la vivienda:**")
        circuitos = [
            {"Circuito": "C1 - Iluminación", "Sección": "1.5 mm²", "Protección PIA": "10A", "Estado": "Incluido" if estancias_totales > 0 else "Pendiente"},
            {"Circuito": "C2 - Tomas uso general", "Sección": "2.5 mm²", "Protección PIA": "16A", "Estado": "Incluido" if estancias_totales > 0 else "Pendiente"},
            {"Circuito": "C3 - Cocina y Horno", "Sección": "6.0 mm²", "Protección PIA": "25A", "Estado": "Incluido" if num_cocinas > 0 else "No requerido"},
            {"Circuito": "C4 - Lavadora / Lavavajillas / Termo", "Sección": "2.5 mm²", "Protección PIA": "20A", "Estado": "Incluido" if num_cocinas > 0 or num_banos > 0 else "No requerido"},
            {"Circuito": "C5 - Baños y auxiliares de cocina", "Sección": "2.5 mm²", "Protección PIA": "16A", "Estado": "Incluido" if num_banos > 0 or num_cocinas > 0 else "No requerido"}
        ]
        if "Elevada" in electrificacion:
            circuitos.append({"Circuito": "C8/C9 - Climatización / Aire Acondicionado", "Sección": "6.0 mm²", "Protección PIA": "25A", "Estado": "Electrificación Elevada"})
        
        st.dataframe(pd.DataFrame(circuitos), use_container_width=True)

    with st.expander("🚰 **Fontanería y Saneamiento (CTE DB-HS4 / HS5)**"):
        if (num_banos + num_aseos + num_cocinas) > 0:
            caudal_total = (num_banos * 0.35) + (num_aseos * 0.20) + (num_cocinas * 0.40)
            coef_simultaneidad = 1 / math.sqrt(max(1, (num_banos + num_aseos + num_cocinas) * 3))
            caudal_diseno = caudal_total * coef_simultaneidad
            
            c_f1, c_f2 = st.columns(2)
            c_f1.metric("Caudal Total Instalado", f"{caudal_total:.2f} L/s")
            c_f2.metric("Caudal Simultáneo de Diseño", f"{caudal_diseno:.2f} L/s")
        else:
            st.info("Configura los baños o cocinas en el Paso 1 para ver el cálculo de caudal.")

    with st.expander("❄️ **Climatización y Calefacción (RITE)**"):
        if superficie > 0:
            zona = st.selectbox("Calidad de Aislamiento / Zona Climática", ["Buena (80 W/m²)", "Media (100 W/m²)", "Deficiente (120 W/m²)"])
            w_m2 = int(zona.split("(")[1].split(" W")[0])
            p_clima_kw = (superficie * w_m2) / 1000
            frig_h = p_clima_kw * 860
            st.metric("Potencia Térmica Necesaria", f"{p_clima_kw:.2f} kW", f"{frig_h:.0f} Frigorías/h")
        else:
            st.info("Introduce la superficie en la barra lateral para calcular necesidades térmicas.")

    with st.expander("📡 **Telecomunicaciones (ICT2) y Redes LAN**"):
        tomas_teleco = (num_dormitorios + num_salones) * 2
        st.write(f"• **Tomas de Datos RJ45 Cat6 recomendadas:** {tomas_teleco} tomas en estancias principales.")
        st.write("• **Punto de Acceso al Usuario (PAU):** Envolvente centralizada de 500x300x80 mm.")

# -----------------------------------------------------------------------------
# TAB 3: ASIGNACIÓN DE PRECIOS UNITARIOS (€0 DE INICIO)
# -----------------------------------------------------------------------------
with tab_paso3:
    st.subheader("💶 Paso 3: Asignación de Precios Unitarios")
    st.write("⚠️ **Todos los precios unitarios comienzan en 0.00 €.** Introduce las tarifas de mano de obra y material pactadas para cada partida.")
    
    st.markdown("---")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("#### ⚡ Partidas de Electricidad")
        pu_elec = st.number_input("Precio Renovación Eléctrica (€ / m²)", min_value=0.0, value=0.0, step=5.0, format="%.2f")
        pu_cuadro = st.number_input("Precio Cuadro General Mando y Protecciones (€ / ud)", min_value=0.0, value=0.0, step=50.0, format="%.2f")
        
        st.markdown("#### 🚰 Partidas de Fontanería")
        pu_bano = st.number_input("Precio Fontanería Completa Baño (€ / baño)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        pu_cocina = st.number_input("Precio Fontanería Completa Cocina (€ / cocina)", min_value=0.0, value=0.0, step=100.0, format="%.2f")

    with col_p2:
        st.markdown("#### ❄️ Climatización y Telecomunicaciones")
        pu_clima = st.number_input("Precio Instalación Climatización (€ / kW)", min_value=0.0, value=0.0, step=50.0, format="%.2f")
        pu_teleco = st.number_input("Precio Toma de Datos Cat6 (€ / toma)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        
        st.markdown("#### 🏗️ Albañilería / Ayuda de Trabajos")
        pu_albanileria = st.number_input("Precio Rozas, Sellados y Ayuda Albañilería (€ / m²)", min_value=0.0, value=0.0, step=5.0, format="%.2f")

# -----------------------------------------------------------------------------
# TAB 4: PRESUPUESTO Y EXPORTACIÓN EXCEL
# -----------------------------------------------------------------------------
with tab_paso4:
    st.subheader("📊 Paso 4: Presupuesto Resultante y Exportación")
    
    # Construcción dinámica del presupuesto
    tomas_teleco_calc = (num_dormitorios + num_salones) * 2
    potencia_clima_calc = (superficie * 100) / 1000 if superficie > 0 else 0.0
    
    filas_presupuesto = [
        {"Partida": "Instalación Eléctrica General (Mecanismos y Cableado)", "Unidad": "m²", "Cantidad": superficie, "Precio Unitario (€)": pu_elec, "Importe (€)": superficie * pu_elec},
        {"Partida": "Cuadro General de Mando y Protecciones (CGMP)", "Unidad": "ud", "Cantidad": 1 if superficie > 0 else 0, "Precio Unitario (€)": pu_cuadro, "Importe (€)": (1 if superficie > 0 else 0) * pu_cuadro},
        {"Partida": "Instalación Fontanería y Saneamiento Baños", "Unidad": "ud", "Cantidad": num_banos + num_aseos, "Precio Unitario (€)": pu_bano, "Importe (€)": (num_banos + num_aseos) * pu_bano},
        {"Partida": "Instalación Fontanería Cocina", "Unidad": "ud", "Cantidad": num_cocinas, "Precio Unitario (€)": pu_cocina, "Importe (€)": num_cocinas * pu_cocina},
        {"Partida": "Red de Datos RJ45 Cat6 e ICT2", "Unidad": "toma", "Cantidad": tomas_teleco_calc, "Precio Unitario (€)": pu_teleco, "Importe (€)": tomas_teleco_calc * pu_teleco},
        {"Partida": "Equipamiento Climatización y RITE", "Unidad": "kW", "Cantidad": potencia_clima_calc, "Precio Unitario (€)": pu_clima, "Importe (€)": potencia_clima_calc * pu_clima},
        {"Partida": "Rozas, Ayuda Albañilería y Sellado", "Unidad": "m²", "Cantidad": superficie, "Precio Unitario (€)": pu_albanileria, "Importe (€)": superficie * pu_albanileria},
    ]
    
    df_presupuesto = pd.DataFrame(filas_presupuesto)
    
    # Mostrar tabla con formato limpio de moneda
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
    total_general = subtotal + impuesto
    
    st.markdown("---")
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Base Imponible (Subtotal)", f"{subtotal:,.2f} €")
    res2.metric(f"IVA ({tipo_iva}%)", f"{impuesto:,.2f} €")
    res3.metric("TOTAL PRESUPUESTO", f"{total_general:,.2f} €")
    
    st.markdown("---")
    st.subheader("📥 Exportación del Presupuesto")
    
    # Generación de archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_presupuesto.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')
        
        # Hoja resumen
        df_resumen = pd.DataFrame([
            {"Concepto": "Cliente / Proyecto", "Valor": nombre_proyecto if nombre_proyecto else "Sin especificar"},
            {"Concepto": "Superficie Útil", "Valor": f"{superficie} m²"},
            {"Concepto": "Subtotal (Base Imponible)", "Valor": f"{subtotal:.2f} €"},
            {"Concepto": f"IVA ({tipo_iva}%)", "Valor": f"{impuesto:.2f} €"},
            {"Concepto": "Total Presupuesto", "Valor": f"{total_general:.2f} €"}
        ])
        df_resumen.to_excel(writer, index=False, sheet_name='Resumen_General')
        
    excel_data = output.getvalue()
    
    nombre_archivo = f"Presupuesto_{(nombre_proyecto if nombre_proyecto else 'Reforma').replace(' ', '_')}.xlsx"
    
    st.download_button(
        label="🟢 Descargar Presupuesto en Excel (.xlsx)",
        data=excel_data,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
