import streamlit as st
import pandas as pd
import math
import io

# Configuración de la página
st.set_page_config(
    page_title="Plataforma de Cálculo Técnico y Presupuestos de Reforma",
    page_icon="🏗️",
    layout="wide"
)

# Título Principal
st.title("🏗️ Plataforma de Cálculo Técnico y Presupuestos de Reforma")
st.markdown("**Cumplimiento Normativo:** REBT (Electrónica), CTE DB-HS4/HS5 (Fontanería y Saneamiento), ICT2 (Teleco) y RITE (Climatización).")

# Sidebar: Datos del Proyecto
st.sidebar.header("📋 Datos del Proyecto")
nombre_proyecto = st.sidebar.text_input("Nombre del Proyecto / Cliente", "Reforma Integral Vivienda")
superficie = st.sidebar.number_input("Superficie Útil (m²)", min_value=20.0, max_value=500.0, value=85.0, step=5.0)
electrificacion = st.sidebar.selectbox("Nivel de Electrificación (REBT)", ["Básica (hasta 5.75 kW)", "Elevada (hasta 9.2 kW)"])

# Tabs para Navegación
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚡ 1. Electricidad (REBT)", 
    "🚰 2. Fontanería y Saneamiento", 
    "📡 3. Telecomunicaciones (ICT2)", 
    "❄️ 4. Climatización (RITE)",
    "🎥 5. Domótica y CCTV",
    "📊 6. Presupuesto Global"
])

# ---------------------------------------------------------
# TAB 1: ELECTRICIDAD (REBT)
# ---------------------------------------------------------
with tab1:
    st.header("⚡ Instalación Eléctrica (REBT - ITC-BT-25 / ITC-BT-19)")
    
    col1, col2 = st.columns(2)
    with col1:
        longitud_di = st.number_input("Longitud Derivación Individual (m)", min_value=1.0, value=15.0)
        p_contratada = st.selectbox("Potencia de Cálculo (kW)", [3.45, 4.6, 5.75, 7.36, 9.2])
    
    with col2:
        cos_phi = 0.9
        tension = 230
        I_calc = (p_contratada * 1000) / (tension * cos_phi)
        st.metric("Intensidad de Cálculo (A)", f"{I_calc:.2f} A")
        
        # Caída de tensión máxima permitida en DI: 1.5%
        cd_max = 230 * 0.015
        s_min = (2 * longitud_di * (p_contratada * 1000)) / (56 * cd_max * tension)
        st.metric("Sección Mínima DI Calculada", f"{s_min:.2f} mm²")
    
    st.subheader("Circuitos de la Vivienda")
    
    circuitos_base = [
        {"Circuito": "C1 - Iluminación", "P_max (W)": 2300, "Sección (mm²)": 1.5, "PIA (A)": 10, "Tubo (mm)": 16},
        {"Circuito": "C2 - Tomas de uso general y frigorífico", "P_max (W)": 3450, "Sección (mm²)": 2.5, "PIA (A)": 16, "Tubo (mm)": 20},
        {"Circuito": "C3 - Cocina y horno", "P_max (W)": 5400, "Sección (mm²)": 6.0, "PIA (A)": 25, "Tubo (mm)": 25},
        {"Circuito": "C4 - Lavadora, lavavajillas y termo", "P_max (W)": 3450, "Sección (mm²)": 2.5, "PIA (A)": 20, "Tubo (mm)": 20},
        {"Circuito": "C5 - Baños y auxiliares de cocina", "P_max (W)": 3450, "Sección (mm²)": 2.5, "PIA (A)": 16, "Tubo (mm)": 20},
    ]
    
    if electrificacion.startswith("Elevada"):
        circuitos_base.extend([
            {"Circuito": "C8 - Calefacción / Aire Acondicionado", "P_max (W)": 5750, "Sección (mm²)": 6.0, "PIA (A)": 25, "Tubo (mm)": 25},
            {"Circuito": "C9 - Aire Acondicionado adic.", "P_max (W)": 3450, "Sección (mm²)": 4.0, "PIA (A)": 20, "Tubo (mm)": 20},
            {"Circuito": "C10 - Secadora independiente", "P_max (W)": 3450, "Sección (mm²)": 2.5, "PIA (A)": 16, "Tubo (mm)": 20},
        ])
    
    df_elec = pd.DataFrame(circuitos_base)
    st.dataframe(df_elec, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: FONTANERÍA Y SANEAMIENTO (CTE DB-HS4 / HS5)
# ---------------------------------------------------------
with tab2:
    st.header("🚰 Fontanería y Saneamiento (CTE DB-HS4 y DB-HS5)")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        num_banos = st.number_input("Número de Baños completos", min_value=1, value=2)
        num_aseos = st.number_input("Número de Aseos", min_value=0, value=0)
    with c2:
        num_cocinas = st.number_input("Número de Cocinas", min_value=1, value=1)
        material_tubo = st.selectbox("Material de Tubería", ["Multicapa (PEX-Al-PEX)", "Cobre", "Polietileno (PE)"])
    with c3:
        caudal_total = (num_banos * 0.35) + (num_aseos * 0.20) + (num_cocinas * 0.40)
        coef_simultaneidad = 1 / math.sqrt(max(1, (num_banos + num_aseos + num_cocinas) * 3))
        caudal_diseno = caudal_total * coef_simultaneidad
        st.metric("Caudal Total Instalado (L/s)", f"{caudal_total:.2f} L/s")
        st.metric("Caudal de Diseño Simultáneo", f"{caudal_diseno:.2f} L/s")

    st.subheader("Diámetros Mínimos Recomendados")
    datos_fontaneria = [
        {"Servicio": "LAVABO", "Caudal AF (L/s)": 0.10, "Caudal ACS (L/s)": 0.10, "Diámetro Tubo (mm)": 16, "Desagüe UD": 1},
        {"Servicio": "INODORO", "Caudal AF (L/s)": 0.10, "Caudal ACS (L/s)": 0.00, "Diámetro Tubo (mm)": 16, "Desagüe UD": 4},
        {"Servicio": "DUCHA / BAÑERA", "Caudal AF (L/s)": 0.20, "Caudal ACS (L/s)": 0.20, "Diámetro Tubo (mm)": 16, "Desagüe UD": 2},
        {"Servicio": "FREGADERO / LAVAVAJILLAS", "Caudal AF (L/s)": 0.20, "Caudal ACS (L/s)": 0.20, "Diámetro Tubo (mm)": 20, "Desagüe UD": 3},
        {"Servicio": "LAVADORA", "Caudal AF (L/s)": 0.20, "Caudal ACS (L/s)": 0.00, "Diámetro Tubo (mm)": 20, "Desagüe UD": 3},
    ]
    st.dataframe(pd.DataFrame(datos_fontaneria), use_container_width=True)

# ---------------------------------------------------------
# TAB 3: TELECOMUNICACIONES (ICT2)
# ---------------------------------------------------------
with tab3:
    st.header("📡 Redes de Telecomunicaciones e ICT2 (RD 346/2011)")
    
    c1, c2 = st.columns(2)
    with c1:
        num_estancias = st.number_input("Número de Estancias Principales (Salones + Dormitorios)", min_value=2, value=4)
        tomas_cat6 = num_estancias * 2
        st.metric("Tomas RJ45 Cat6 Mínimas (PAU)", tomas_cat6)
    with c2:
        st.info("📌 Exigencia CPR: Todo el cableado de datos debe poseer clasificación de reacción al fuego mínima Dca-s2,d2,a2.")

    st.markdown("### Esquema de Infraestructura Interna")
    st.write("• **PAU (Punto de Acceso al Usuario):** Caja registro de 500x300x80 mm.")
    st.write("• **Cable Par Trenzado:** Categoría 6 UTP/FTP.")
    st.write("• **Fibra Óptica:** 2 fibras desde RITI hasta PAU.")

# ---------------------------------------------------------
# TAB 4: CLIMATIZACIÓN (RITE)
# ---------------------------------------------------------
with tab4:
    st.header("❄️ Climatización y Calefacción (RITE)")
    
    col1, col2 = st.columns(2)
    with col1:
        zona_climatica = st.selectbox("Zona Climática / Aislamiento", ["Bueno (80 W/m²)", "Medio (100 W/m²)", "Bajo / Antiguo (120 W/m²)"])
        w_m2 = int(zona_climatica.split("(")[1].split(" W")[0])
        potencia_clima_kw = (superficie * w_m2) / 1000
        frig_h = potencia_clima_kw * 860
    
    with col2:
        st.metric("Potencia Térmica Necesaria", f"{potencia_clima_kw:.2f} kW")
        st.metric("Capacidad de Frigorías Necesaria", f"{frig_h:.0f} frig/h")

# ---------------------------------------------------------
# TAB 5: DOMÓTICA Y CCTV
# ---------------------------------------------------------
with tab5:
    st.header("🎥 Seguridad, CCTV y Domótica")
    
    col1, col2 = st.columns(2)
    with col1:
        num_camaras = st.number_input("Número de Cámaras IP CCTV", min_value=0, value=4)
        dias_grabacion = st.number_input("Días de Grabación Continuos", min_value=1, value=15)
    with col2:
        gb_por_dia_cam = (4 * 1000000 * 86400) / (8 * 1024**3)
        disco_tb = (num_camaras * gb_por_dia_cam * dias_grabacion) / 1024
        st.metric("Almacenamiento HDD Necesario (TB)", f"{disco_tb:.2f} TB")

# ---------------------------------------------------------
# TAB 6: PRESUPUESTO GLOBAL
# ---------------------------------------------------------
with tab6:
    st.header("📊 Presupuesto Desglosado y Resumen Ejecutivo")
    
    data_presupuesto = [
        {"Partida": "Instalación Eléctrica Completa (Cuadro, Mecanismos, Cableado REBT)", "P.U. (€)": 45.0, "Unidad": "m²", "Cantidad": superficie, "Total (€)": 45.0 * superficie},
        {"Partida": "Fontanería, Saneamiento y Sanitarios (CTE DB-HS)", "P.U. (€)": 1200.0, "Unidad": "Baño/Cocina", "Cantidad": num_banos + num_cocinas, "Total (€)": 1200.0 * (num_banos + num_cocinas)},
        {"Partida": "Red de Telecomunicaciones ICT2 y LAN Cat6", "P.U. (€)": 60.0, "Unidad": "Toma", "Cantidad": tomas_cat6, "Total (€)": 60.0 * tomas_cat6},
        {"Partida": "Climatización Por Conductos / Aerotermia RITE", "P.U. (€)": 450.0, "Unidad": "kW", "Cantidad": potencia_clima_kw, "Total (€)": 450.0 * potencia_clima_kw},
        {"Partida": "Sistema de Seguridad CCTV y Domótica", "P.U. (€)": 150.0, "Unidad": "Punto", "Cantidad": num_camaras, "Total (€)": 150.0 * num_camaras},
    ]
    
    df_presup = pd.DataFrame(data_presupuesto)
    st.dataframe(df_presup, use_container_width=True)
    
    subtotal = df_presup["Total (€)"].sum()
    iva = subtotal * 0.21
    total_general = subtotal + iva
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Subtotal (sin IVA)", f"{subtotal:,.2f} €")
    col_b.metric("IVA (21%)", f"{iva:,.2f} €")
    col_c.metric("TOTAL PRESUPUESTO", f"{total_general:,.2f} €")
    
    st.subheader("📥 Exportar Presupuesto")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_presup.to_excel(writer, index=False, sheet_name='Presupuesto')
        df_elec.to_excel(writer, index=False, sheet_name='Electricidad_REBT')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📄 Descargar Presupuesto Completo en Excel (.xlsx)",
        data=excel_data,
        file_name=f"Presupuesto_{nombre_proyecto.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
