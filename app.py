import streamlit as st
import pandas as pd
import io

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gestor Técnico de Reformas e Instalaciones",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS - AZUL PROFUNDO (#0F2C59) Y AMARILLO ENERGÍA (#FFC107)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Barra lateral (Sidebar) en Azul Profundo #0F2C59 */
    [data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }
    
    /* ESTILO ESPECÍFICO PARA LAS 3 CASILLAS: Nombre, Dirección y Tipo de IVA */
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important; /* +2pt */
        margin-bottom: 0.3rem !important;
    }
    [data-testid="stSidebar"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 6px !important;
        border: 2px solid #FFC107 !important;
        font-weight: 700 !important;
        padding: 0.5rem !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 2px solid #FFC107 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* Botones de + y - en Amarillo Energía #FFC107 */
    button[aria-label="Increase value"], 
    button[aria-label="Decrease value"],
    div[data-testid="stNumberInputStepDown"],
    div[data-testid="stNumberInputStepUp"] {
        background-color: #FFC107 !important;
        color: #212529 !important;
        border-radius: 4px !important;
        border: 1px solid #D39E00 !important;
    }
    button[aria-label="Increase value"] *, 
    button[aria-label="Decrease value"] * {
        color: #212529 !important;
        font-weight: bold !important;
    }

    /* Encabezado principal estilo Manual Técnico */
    .header-rite {
        background: linear-gradient(135deg, #0F2C59 0%, #081B38 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
        border-left: 8px solid #FFC107;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 2.3rem !important; /* Aumentado 2 puntos (era 2.1rem) */
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #CBD5E1;
        font-size: 1.1rem !important; /* Aumentado 2 puntos (era 0.98rem) */
        margin-top: 0.3rem;
    }
    .header-badge {
        background-color: #FFC107;
        color: #212529 !important;
        padding: 0.35rem 0.9rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.95rem !important; /* Aumentado 2 puntos */
        display: inline-block;
        margin-top: 0.6rem;
    }
    
    /* Aumento de 2 puntos en los títulos generales */
    h1 { font-size: 2.3rem !important; }
    h2 { font-size: 1.9rem !important; }
    h3 { font-size: 1.6rem !important; }
    h4 { font-size: 1.3rem !important; }
    .stSubheader, div[data-testid="stSubheader"] { font-size: 1.4rem !important; }

    .card-product {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #0F2C59;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .price-tag {
        font-size: 1.55rem !important; /* Aumentado 2 pt */
        font-weight: 800;
        color: #0F2C59;
    }
    .unit-tag {
        font-size: 0.95rem !important; /* Aumentado 2 pt */
        color: #64748B;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #FFC107;
        color: #212529 !important;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #E0A800;
        color: #212529 !important;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #1E293B;
        font-weight: 700;
        font-size: 1.05rem !important; /* Aumentado 2 puntos */
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INICIALIZACIÓN DE ESTADO DE SESIÓN
# -----------------------------------------------------------------------------
if 'cesta' not in st.session_state:
    st.session_state.cesta = {}

if 'cliente_nombre' not in st.session_state:
    st.session_state.cliente_nombre = ""

if 'cliente_obra' not in st.session_state:
    st.session_state.cliente_obra = ""

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL ESTILO MANUAL TÉCNICO RITE/REBT
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-rite">
    <div class="header-title">📘 ALMACÉN TÉCNICO & SERVICIOS NORMATIVOS</div>
    <div class="header-subtitle">Presupuestador Guiado según Reglamento RITE, REBT, CTE DB-HS e ICT2</div>
    <div class="header-badge">EDICIÓN TÉCNICA PROFESIONAL 2026</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL: CESTA Y CONFIGURACIÓN DE FACTURACIÓN
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🛒 Presupuesto Activo")

st.session_state.cliente_nombre = st.sidebar.text_input(
    "Cliente / Empresa", 
    value=st.session_state.cliente_nombre, 
    placeholder="Ej. Juan Pérez / Reforma C/ Mayor"
)
st.session_state.cliente_obra = st.sidebar.text_input(
    "Dirección de la Obra", 
    value=st.session_state.cliente_obra, 
    placeholder="Ej. Castelldefels, Barcelona"
)

tipo_iva = st.sidebar.selectbox(
    "Tipo de IVA Aplicable",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Partidas Seleccionadas")

if not st.session_state.cesta:
    st.sidebar.info("La cesta está vacía. Selecciona partidas o materiales en las pestañas principales.")
else:
    subtotal_cesta = 0.0
    
    for item_id, datos in list(st.session_state.cesta.items()):
        cant = datos['cantidad']
        pu = datos['precio_unitario']
        imp = cant * pu
        subtotal_cesta += imp
        
        st.sidebar.markdown(f"**{datos['nombre']}**")
        col_c1, col_c2 = st.sidebar.columns()
        with col_c1:
            st.caption(f"{cant:.1f} {datos['unidad']} x {pu:.2f} € = **{imp:.2f} €**")
        with col_c2:
            if st.button("🗑️", key=f"del_{item_id}"):
                del st.session_state.cesta[item_id]
                st.rerun()
        st.sidebar.markdown("---")
    
    iva_calc = subtotal_cesta * (tipo_iva / 100)
    total_calc = subtotal_cesta + iva_calc
    
    st.sidebar.metric("Subtotal Base", f"{subtotal_cesta:,.2f} €")
    st.sidebar.metric(f"IVA ({tipo_iva}%)", f"{iva_calc:,.2f} €")
    st.sidebar.metric("TOTAL PRESUPUESTO", f"{total_calc:,.2f} €")
    
    if st.sidebar.button("🧹 Vaciar Presupuesto"):
        st.session_state.cesta = {}
        st.rerun()

# -----------------------------------------------------------------------------
# BASE DE DATOS DE PARTIDAS Y MATERIALES
# -----------------------------------------------------------------------------
productos_db = {
    "elec": [
        {
            "id": "e1", 
            "nombre": "⚡ Renovación Eléctrica General (REBT)", 
            "unidad": "m²", 
            "precio": 35.00, 
            "desc": "Cableado libre de halógenos (H07Z1-K), canalización y mecanismos según ITC-BT-25."
        },
        {
            "id": "e2", 
            "nombre": "🎛️ Cuadro General de Mando (CGMP)", 
            "unidad": "ud", 
            "precio": 380.00, 
            "desc": "Cuadro empotrado con IGA, protector de sobretensiones, diferencial 40A/30mA y PIAs C1-C5."
        },
        {
            "id": "e3", 
            "nombre": "💡 Punto de Luz / Toma Adicional", 
            "unidad": "ud", 
            "precio": 45.00, 
            "desc": "Apertura de rozas, tubo corrugado, conductor 2.5mm² y caja de mecanismo instalada."
        }
    ],
    "font": [
        {
            "id": "f1", 
            "nombre": "Shower Instalación Fontanería Baño (CTE DB-HS4/HS5)", 
            "unidad": "baño", 
            "precio": 850.00, 
            "desc": "Red de distribución Multicapa/PEX para agua fría/caliente y desagües de PVC."
        },
        {
            "id": "f2", 
            "nombre": "🚰 Instalación Fontanería Cocina", 
            "unidad": "cocina", 
            "precio": 620.00, 
            "desc": "Tomas de agua y desagües para fregadero, lavavajillas y lavadora con llaves de escuadra."
        },
        {
            "id": "f3", 
            "nombre": "🛁 Cambio de Bañera por Plato de Ducha", 
            "unidad": "ud", 
            "precio": 790.00, 
            "desc": "Demolición, plato de resina antideslizante, válvula de gran caudal, grifería y sellado."
        }
    ],
    "clima": [
        {
            "id": "c1", 
            "nombre": "❄️ Equipo Aire Acondicionado Split RITE", 
            "unidad": "ud", 
            "precio": 690.00, 
            "desc": "Split Inverter 3000 frig/h A++ con instalación frigorífica y línea de condensados."
        },
        {
            "id": "c2", 
            "nombre": "🌀 Climatización por Conductos RITE", 
            "unidad": "kW", 
            "precio": 320.00, 
            "desc": "Red de conductos Climaver, rejillas de impulsión/retorno y zonificación térmica."
        },
        {
            "id": "c3", 
            "nombre": "🔥 Termo Eléctrico 80L Carga Rápida", 
            "unidad": "ud", 
            "precio": 310.00, 
            "desc": "Termo mural con válvula de seguridad, latiguillos e instalación de fontanería."
        }
    ],
    "obras": [
        {
            "id": "o1", 
            "nombre": "🧱 Ayuda de Albañilería y Rozas", 
            "unidad": "m²", 
            "precio": 18.00, 
            "desc": "Apertura de canalizaciones, recebado con mortero de agarre y tendido de yeso."
        },
        {
            "id": "o2", 
            "nombre": "🔲 Alicatado y Solado Cerámico", 
            "unidad": "m²", 
            "precio": 38.00, 
            "desc": "Colocación de gres/azulejo con cemento cola C2TE y rejuntado antimoho."
        },
        {
            "id": "o3", 
            "nombre": "🎨 Pintura Plástica Lavable", 
            "unidad": "m²", 
            "precio": 12.00, 
            "desc": "Preparación de paramentos, imprimación fijadora y dos manos de pintura plástica."
        }
    ],
    "packs": [
        {
            "id": "p1", 
            "nombre": "📦 Pack Reforma Eléctrica Integral 80m²", 
            "unidad": "pack", 
            "precio": 2950.00, 
            "desc": "Cuadro CGMP + 5 Circuitos REBT + 35 Puntos de luz/enchufes + Boletín Certificado."
        },
        {
            "id": "p2", 
            "nombre": "📦 Pack Reforma Integral Baño Completo", 
            "unidad": "pack", 
            "precio": 3200.00, 
            "desc": "Fontanería CTE + Electricidad + Alicatado + Sanitaros + Ducha + Grifería."
        }
    ]
}

def render_categoria(lista_prods):
    cols = st.columns(3)
    for idx, prod in enumerate(lista_prods):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card-product">
                <h4 style="margin:0 0 0.4rem 0; color:#0F2C59; font-size:1.2rem;">{prod['nombre']}</h4>
                <p style="font-size:0.9rem; color:#475569; min-height:48px; margin-bottom:0.8rem; line-height:1.3;">{prod['desc']}</p>
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.8rem;">
                    <span class="price-tag">{prod['precio']:.2f} €</span>
                    <span class="unit-tag">por {prod['unidad']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cant = st.number_input(f"Cantidad ({prod['unidad']})", min_value=1.0, value=1.0, step=1.0, key=f"cant_{prod['id']}")
            pu_custom = st.number_input(f"Precio Unitario (€)", min_value=0.0, value=float(prod['precio']), step=5.0, key=f"pu_{prod['id']}")
            
            if st.button(f"🛒 Añadir al Presupuesto", key=f"btn_{prod['id']}"):
                st.session_state.cesta[prod['id']] = {
                    "nombre": prod['nombre'],
                    "unidad": prod['unidad'],
                    "cantidad": cant,
                    "precio_unitario": pu_custom
                }
                st.success(f"Añadido: {cant:.1f} {prod['unidad']} de {prod['nombre']}")
                st.rerun()

# -----------------------------------------------------------------------------
# PESTAÑAS DEL CATÁLOGOS TÉCNICO
# -----------------------------------------------------------------------------
cat_elec, cat_font, cat_clima, cat_obras, cat_packs = st.tabs([
    "⚡ Electricidad (REBT)",
    "🚰 Fontanería (CTE)",
    "❄️ Climatización (RITE)",
    "🏗️ Albañilería y Acabados",
    "📦 Packs Llave en Mano"
])

with cat_elec:
    st.subheader("⚡ Catálogo de Instalaciones Eléctricas (REBT - RD 842/2002)")
    render_categoria(productos_db["elec"])

with cat_font:
    st.subheader("🚰 Catálogo de Fontanería y Saneamiento (CTE DB-HS4 / DB-HS5)")
    render_categoria(productos_db["font"])

with cat_clima:
    st.subheader("❄️ Catálogo de Climatización, Calefacción y ACS (RITE - RD 1027/2007)")
    render_categoria(productos_db["clima"])

with cat_obras:
    st.subheader("🏗️ Ayuda de Albañilería, Rozas y Remates")
    render_categoria(productos_db["obras"])

with cat_packs:
    st.subheader("📦 Packs de Reforma Completa")
    render_categoria(productos_db["packs"])

# -----------------------------------------------------------------------------
# TABLA RESUMEN Y EXPORTACIÓN A EXCEL
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Resumen General del Presupuesto")

if st.session_state.cesta:
    filas_pres = []
    for item_id, d in st.session_state.cesta.items():
        filas_pres.append({
            "Partida / Material": d['nombre'],
            "Unidad": d['unidad'],
            "Cantidad": d['cantidad'],
            "Precio Unitario (€)": d['precio_unitario'],
            "Importe (€)": d['cantidad'] * d['precio_unitario']
        })
    
    df_pres = pd.DataFrame(filas_pres)
    
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
    
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Base Imponible", f"{sub:,.2f} €")
    col_r2.metric(f"IVA ({tipo_iva}%)\", f\"{iva_val:,.2f} €\")
    col_r3.metric("TOTAL PRESUPUESTO", f"{tot_val:,.2f} €")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_pres.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')
        
        df_res = pd.DataFrame([
            {"Concepto": "Cliente / Empresa", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
            {"Concepto": "Dirección de Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
            {"Concepto": "Base Imponible", "Valor": f"{sub:.2f} €"},
            {"Concepto": "IVA", "Valor": f"{iva_val:.2f} €"},
            {"Concepto": "Total Presupuesto", "Valor": f"{tot_val:.2f} €"}
        ])
        df_res.to_excel(writer, index=False, sheet_name='Datos_Cliente')
        
    excel_bytes = output.getvalue()
    
    st.download_button(
        label="🟢 Descargar Presupuesto en Excel (.xlsx)",
        data=excel_bytes,
        file_name="Presupuesto_Tecnico_Reformas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Añade partidas desde las pestañas superiores para generar la tabla y descargar el presupuesto en Excel.")
