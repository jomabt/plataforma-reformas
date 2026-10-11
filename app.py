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
# ESTILOS CSS CON PALETA CORPORATIVA SOFT LIGHT & AZUL PROFUNDO (#0F2C59)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal claro y limpio */
    .stApp {
        background-color: #F8F9FA !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Encabezado principal estilo Manual Técnico */
    .header-rite {
        background: linear-gradient(135deg, #0F2C59 0%, #1B365D 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.8rem;
        border-left: 10px solid #FFC107;
        box-shadow: 0 6px 15px rgba(15, 44, 89, 0.15);
    }
    .header-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #E2E8F0 !important;
        font-size: 1.15rem !important;
        margin-top: 0.4rem;
    }
    .header-badge {
        background-color: #FFC107;
        color: #0F2C59 !important;
        padding: 0.4rem 1.0rem;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 0.8rem;
    }

    /* Barra lateral (Sidebar) en Azul Profundo (#0F2C59) */
    [data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFC107 !important;
        font-weight: 800 !important;
    }

    /* Estilo de Inputs y Cuadros del Menú Izquierdo (Fondo Blanco, Texto Oscuro, Borde Amarillo) */
    [data-testid="stSidebar"] input, 
    [data-testid="stSidebar"] div[data-baseweb="select"],
    [data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 2px solid #FFC107 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] input::placeholder {
        color: #6C757D !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #212529 !important;
        background-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.0rem !important;
    }

    /* Tarjetas de Estancias y Productos */
    .card-estancia {
        background-color: #FFFFFF !important;
        border: 2px solid #007BFF !important;
        border-top: 6px solid #0F2C59 !important;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.0rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .card-product {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-top: 5px solid #0F2C59 !important;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.04);
    }
    .card-title {
        color: #0F2C59 !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    .card-desc {
        color: #334155 !important;
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
        margin-bottom: 0.8rem !important;
        min-height: 48px;
    }
    .price-tag {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #0F2C59 !important;
    }
    .unit-tag {
        font-size: 0.9rem !important;
        color: #007BFF !important;
        font-weight: 700 !important;
    }

    /* Botones de Incrementar y Decrementar (+ / -) */
    div[data-testid="stNumberInput"] button {
        background-color: #FFC107 !important;
        color: #212529 !important;
        border: 1px solid #D39E00 !important;
        font-weight: 900 !important;
        font-size: 1.2rem !important;
        border-radius: 6px !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background-color: #E0A800 !important;
        color: #000000 !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #212529 !important;
        border: 2px solid #007BFF !important;
        font-weight: 800 !important;
        text-align: center !important;
        font-size: 1.1rem !important;
    }

    /* Aumento de Tipografía en Títulos (+4pt) */
    h1 { font-size: 2.6rem !important; font-weight: 800 !important; color: #0F2C59 !important; }
    h2 { font-size: 2.2rem !important; font-weight: 800 !important; color: #0F2C59 !important; }
    h3 { font-size: 1.8rem !important; font-weight: 800 !important; color: #0F2C59 !important; }
    h4 { font-size: 1.4rem !important; font-weight: 700 !important; color: #007BFF !important; }

    /* Botones Principales de Acción */
    .stButton>button {
        background-color: #007BFF !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.2rem !important;
        width: 100% !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
    }
    .stButton>button:hover {
        background-color: #0056B3 !important;
        color: #FFFFFF !important;
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

if 'superficie_m2' not in st.session_state:
    st.session_state.superficie_m2 = 80.0

if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = "1. Estancias"

# Inicialización de cantidades de estancias
estancias_def = {
    'dormitorios': 3,
    'salones': 1,
    'banos': 2,
    'aseos': 0,
    'cocinas': 1,
    'galerias': 1,
    'terrazas': 1,
    'trasteros': 0
}
for k, v in estancias_def.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-rite">
    <div class="header-title">📘 ALMACÉN TÉCNICO & SERVICIOS NORMATIVOS</div>
    <div class="header-subtitle">Presupuestador Guiado según Reglamento RITE, REBT, CTE DB-HS e ICT2</div>
    <div class="header-badge">EDICIÓN TÉCNICA PROFESIONAL 2026</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# NAVEGACIÓN PASO A PASO (BARRA SUPERIOR)
# -----------------------------------------------------------------------------
opciones_pasos = [
    "1. Estancias",
    "2. Cálculos Técnicos",
    "3. Tarifas (€0)",
    "4. Presupuesto",
    "5. Biblioteca Normativa"
]

paso_sel = st.radio(
    "Navegación del Proyecto:",
    opciones_pasos,
    index=opciones_pasos.index(st.session_state.paso_actual) if st.session_state.paso_actual in opciones_pasos else 0,
    horizontal=True,
    key="radio_paso_top"
)
st.session_state.paso_actual = paso_sel
st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (MENU IZQUIERDO) - DATOS DE CLIENTE Y CESTA
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🛒 Presupuesto Activo")

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
st.session_state.superficie_m2 = st.sidebar.number_input(
    "📐 Superficie Útil Afectada (m²):", 
    min_value=10.0, 
    max_value=1000.0, 
    value=float(st.session_state.superficie_m2), 
    step=5.0
)

tipo_iva = st.sidebar.selectbox(
    "💶 Tipo de IVA Aplicable:",
    [21, 10, 0],
    format_func=lambda x: f"{x}% ({'General' if x==21 else 'Reducido Reforma' if x==10 else 'Exento'})"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Partidas Seleccionadas")

if not st.session_state.cesta:
    st.sidebar.info("La cesta está vacía. Añade partidas en el paso 3 (Tarifas).")
else:
    subtotal_cesta = 0.0
    for item_id, datos in list(st.session_state.cesta.items()):
        cant = datos['cantidad']
        pu = datos['precio_unitario']
        imp = cant * pu
        subtotal_cesta += imp
        
        st.sidebar.markdown(f"**{datos['nombre']}**")
        st.sidebar.caption(f"{cant:.1f} {datos['unidad']} x {pu:.2f} € = **{imp:.2f} €**")
        if st.sidebar.button(f"🗑️ Quitar {datos['nombre'][:15]}...", key=f"del_side_{item_id}"):
            del st.session_state.cesta[item_id]
            st.rerun()
        st.sidebar.markdown("---")
    
    iva_calc = subtotal_cesta * (tipo_iva / 100)
    total_calc = subtotal_cesta + iva_calc
    
    st.sidebar.metric("Base Imponible", f"{subtotal_cesta:,.2f} €")
    st.sidebar.metric(f"IVA ({tipo_iva}%)", f"{iva_calc:,.2f} €")
    st.sidebar.metric("TOTAL PRESUPUESTO", f"{total_calc:,.2f} €")
    
    if st.sidebar.button("🧹 Vaciar Presupuesto", key="btn_clear_sidebar"):
        st.session_state.cesta = {}
        st.rerun()

# -----------------------------------------------------------------------------
# BASE DE DATOS DE PARTIDAS TÉCNICAS (CON PRECIOS EN 0.00 €)
# -----------------------------------------------------------------------------
productos_db = {
    "elec": [
        {
            "id": "e1", 
            "nombre": "⚡ Renovación Eléctrica General (REBT)", 
            "unidad": "m²", 
            "precio": 0.00, 
            "desc": "Cableado libre de halógenos (H07Z1-K), canalización y mecanismos según ITC-BT-25."
        },
        {
            "id": "e2", 
            "nombre": "🎛️ Cuadro General de Mando (CGMP)", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Cuadro empotrado con IGA, protector de sobretensiones, diferencial 40A/30mA y PIAs C1-C5."
        },
        {
            "id": "e3", 
            "nombre": "💡 Punto de Luz / Toma Adicional", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Apertura de rozas, tubo corrugado, conductor 2.5mm² y caja de mecanismo instalada."
        },
        {
            "id": "e4", 
            "nombre": "📜 Certificado de Instalación (Boletín Eléctrico)", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Memoria Técnica de Diseño (MTD), inspección y tramitación en Industria."
        }
    ],
    "font": [
        {
            "id": "f1", 
            "nombre": "🚿 Instalación Fontanería Baño (CTE DB-HS4/HS5)", 
            "unidad": "baño", 
            "precio": 0.00, 
            "desc": "Red de distribución Multicapa/PEX para agua fría/caliente y desagües de PVC."
        },
        {
            "id": "f2", 
            "nombre": "🚰 Instalación Fontanería Cocina", 
            "unidad": "cocina", 
            "precio": 0.00, 
            "desc": "Tomas de agua y desagües para fregadero, lavavajillas y lavadora con llaves de escuadra."
        },
        {
            "id": "f3", 
            "nombre": "🛁 Cambio de Bañera por Plato de Ducha", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Demolición, plato de resina antideslizante, válvula de gran caudal, grifería y sellado."
        }
    ],
    "clima": [
        {
            "id": "c1", 
            "nombre": "❄️ Equipo Aire Acondicionado Split RITE", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Split Inverter 3000 frig/h A++ con instalación frigorífica y línea de condensados."
        },
        {
            "id": "c2", 
            "nombre": "🌀 Climatización por Conductos RITE", 
            "unidad": "kW", 
            "precio": 0.00, 
            "desc": "Red de conductos Climaver, rejillas de impulsión/retorno y zonificación térmica."
        },
        {
            "id": "c3", 
            "nombre": "🔥 Termo Eléctrico 80L Carga Rápida", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Termo mural con válvula de seguridad, latiguillos e instalación de fontanería."
        }
    ],
    "obras": [
        {
            "id": "o1", 
            "nombre": "🧱 Ayuda de Albañilería y Rozas", 
            "unidad": "m²", 
            "precio": 0.00, 
            "desc": "Apertura de canalizaciones, recebado con mortero de agarre y tendido de yeso."
        },
        {
            "id": "o2", 
            "nombre": "🔲 Alicatado y Solado Cerámico", 
            "unidad": "m²", 
            "precio": 0.00, 
            "desc": "Colocación de gres/azulejo con cemento cola C2TE y rejuntado antimoho."
        },
        {
            "id": "o3", 
            "nombre": "🎨 Pintura Plástica Lavable", 
            "unidad": "m²", 
            "precio": 0.00, 
            "desc": "Preparación de paramentos, imprimación fijadora y dos manos de pintura plástica."
        }
    ],
    "packs": [
        {
            "id": "p1", 
            "nombre": "📦 Pack Reforma Eléctrica Integral 80m²", 
            "unidad": "pack", 
            "precio": 0.00, 
            "desc": "Cuadro CGMP + 5 Circuitos REBT + 35 Puntos de luz/enchufes + Boletín Certificado."
        },
        {
            "id": "p2", 
            "nombre": "📦 Pack Reforma Integral Baño Completo", 
            "unidad": "pack", 
            "precio": 0.00, 
            "desc": "Fontanería CTE + Electricidad + Alicatado + Sanitarios + Ducha + Grifería."
        }
    ]
}

# -----------------------------------------------------------------------------
# PASO 1: ALCANCE Y ESTANCIAS
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == "1. Estancias":
    st.subheader("📋 Paso 1: Configuración de Estancias de la Vivienda o Local")
    st.write("Selecciona la cantidad de cada estancia para dimensionar la reforma y calcular las necesidades normativas:")
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    
    with col_e1:
        st.markdown('<div class="card-estancia"><div class="card-title">🛌 Dormitorios</div></div>', unsafe_allow_html=True)
        st.session_state.dormitorios = st.number_input("Cantidad", min_value=0, max_value=10, value=st.session_state.dormitorios, key="num_dorm")
        
        st.markdown('<div class="card-estancia"><div class="card-title">🍳 Cocinas</div></div>', unsafe_allow_html=True)
        st.session_state.cocinas = st.number_input("Cantidad", min_value=0, max_value=5, value=st.session_state.cocinas, key="num_coc")

    with col_e2:
        st.markdown('<div class="card-estancia"><div class="card-title">🛋️ Salones / Comedores</div></div>', unsafe_allow_html=True)
        st.session_state.salones = st.number_input("Cantidad", min_value=0, max_value=5, value=st.session_state.salones, key="num_sal")
        
        st.markdown('<div class="card-estancia"><div class="card-title">🧺 Galerías / Lavaderos</div></div>', unsafe_allow_html=True)
        st.session_state.galerias = st.number_input("Cantidad", min_value=0, max_value=5, value=st.session_state.galerias, key="num_gal")

    with col_e3:
        st.markdown('<div class="card-estancia"><div class="card-title">🛁 Baños Completos</div></div>', unsafe_allow_html=True)
        st.session_state.banos = st.number_input("Cantidad", min_value=0, max_value=10, value=st.session_state.banos, key="num_ban")
        
        st.markdown('<div class="card-estancia"><div class="card-title">🌿 Terrazas / Balcones</div></div>', unsafe_allow_html=True)
        st.session_state.terrazas = st.number_input("Cantidad", min_value=0, max_value=10, value=st.session_state.terrazas, key="num_ter")

    with col_e4:
        st.markdown('<div class="card-estancia"><div class="card-title">🧻 Aseos (Sin Ducha)</div></div>', unsafe_allow_html=True)
        st.session_state.aseos = st.number_input("Cantidad", min_value=0, max_value=5, value=st.session_state.aseos, key="num_ase")
        
        st.markdown('<div class="card-estancia"><div class="card-title">📦 Trasteros / Garajes</div></div>', unsafe_allow_html=True)
        st.session_state.trasteros = st.number_input("Cantidad", min_value=0, max_value=5, value=st.session_state.trasteros, key="num_tras")

    st.markdown("---")
    
    col_p1_btn1, col_p1_btn2 = st.columns([2, 2])
    with col_p1_btn2:
        if st.button("Siguiente Paso: Dimensionado Técnico ➔", key="btn_p1_next"):
            st.session_state.paso_actual = "2. Cálculos Técnicos"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 2: DIMENSIONADO TÉCNICO NORMATIVO
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "2. Cálculos Técnicos":
    st.subheader("🛠️ Paso 2: Dimensionado Técnico Normativo (REBT, CTE, RITE, ICT2)")
    st.write("Cálculos automáticos basados en las estancias seleccionadas y la superficie afectada:")
    
    m2 = st.session_state.superficie_m2
    num_b = st.session_state.banos + st.session_state.aseos
    num_c = st.session_state.cocinas
    
    # REBT
    tipo_electrif = "Elevada (>= 9.2 kW)" if (m2 > 160 or num_b >= 2) else "Básica (5.75 kW)"
    num_circuitos = 5 if tipo_electrif.startswith("Básica") else 8
    
    # CTE DB-HS4/HS5
    caudal_l_s = (num_b * 0.35) + (num_c * 0.40)
    ud_saneamiento = (num_b * 6) + (num_c * 5)
    
    # RITE
    potencia_clima_kw = (m2 * 0.09) # 90 W/m2
    termo_litros = 80 if num_b <= 1 else 150
    
    # ICT2
    tomas_rj45 = (st.session_state.dormitorios * 2) + (st.session_state.salones * 2) + (st.session_state.cocinas * 1)
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.markdown("#### ⚡ Requisitos Eléctricos (REBT RD 842/2002)")
        st.info(f"**Grado de Electrificación:** {tipo_electrif}\n\n"
                f"• **Circuitos Mínimos:** {num_circuitos} líneas independientes (C1, C2, C3, C4, C5...)\n\n"
                f"• **Interruptor General (IGA):** 25A / 32A según potencia contratada\n\n"
                f"• **Protección Diferencial:** 40A / 30mA Superinmunizado")
        
        st.markdown("#### 💧 Requisitos de Fontanería (CTE DB-HS4 / HS5)")
        st.info(f"**Caudal Instantáneo Estimado:** {caudal_l_s:.2f} l/s\n\n"
                f"• **Carga de Saneamiento:** {ud_saneamiento} Unidades de Desagüe (UD)\n\n"
                f"• **Tuberías Principales:** Multicapa Ø20mm / PEX Ø16mm a derivaciones")

    with col_calc2:
        st.markdown("#### ❄️ Climatización y ACS (RITE RD 1027/2007)")
        st.info(f"**Potencia Térmica Necesaria:** {potencia_clima_kw:.1f} kW (~90 W/m²)\n\n"
                f"• **Acumulación ACS Recomendada:** {termo_litros} Litros\n\n"
                f"• **Eficiencia Estacional:** A++ / Inverter con refrigerante R32")
        
        st.markdown("#### 📡 Telecomunicaciones (ICT2 RD 346/2011)")
        st.info(f"**Tomas RJ45 Cat.6 Calculadas:** {tomas_rj45} tomas de datos\n\n"
                f"• **Puntos de Registro:** PAU centralizado con Coaxial TV/SAT y Fibra Óptica")

    st.markdown("---")
    col_p2_btn1, col_p2_btn2 = st.columns([2, 2])
    with col_p2_btn1:
        if st.button("⬅️ Paso Anterior: Estancias", key="btn_p2_prev"):
            st.session_state.paso_actual = "1. Estancias"
            st.rerun()
    with col_p2_btn2:
        if st.button("Siguiente Paso: Cuadro de Tarifas ➔", key="btn_p2_next"):
            st.session_state.paso_actual = "3. Tarifas (€0)"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 3: CUADRO DE TARIFAS (€0 DE INICIO)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "3. Tarifas (€0)":
    st.subheader("💶 Paso 3: Tarifas y Precios Unitarios (€0.00 de Inicio)")
    st.write("Selecciona los trabajos e introduce el precio unitario personalizado (€) para cada partida:")
    
    cat_elec, cat_font, cat_clima, cat_obras, cat_packs = st.tabs([
        "⚡ Electricidad (REBT)",
        "🚰 Fontanería (CTE)",
        "❄️ Climatización (RITE)",
        "🏗️ Albañilería y Acabados",
        "📦 Packs Llave en Mano"
    ])
    
    def render_cat_items(items):
        cols = st.columns(2)
        for idx, item in enumerate(items):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="card-product">
                    <div class="card-title">{item['nombre']}</div>
                    <div class="card-desc">{item['desc']}</div>
                    <div class="unit-tag">Medida por: {item['unidad']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c_cant = st.number_input(f"Cantidad ({item['unidad']})", min_value=1.0, value=1.0, step=1.0, key=f"c_{item['id']}")
                c_pu = st.number_input(f"Precio Unitario (€ por {item['unidad']})", min_value=0.0, value=0.0, step=10.0, format="%.2f", key=f"pu_{item['id']}")
                
                if st.button(f"🛒 Añadir {item['nombre'][:20]}...", key=f"add_{item['id']}"):
                    st.session_state.cesta[item['id']] = {
                        "nombre": item['nombre'],
                        "unidad": item['unidad'],
                        "cantidad": c_cant,
                        "precio_unitario": c_pu
                    }
                    st.success(f"✔️ Añadido: {c_cant:.1f} {item['unidad']} a {c_pu:.2f} €/unidad")
                    st.rerun()

    with cat_elec:
        render_cat_items(productos_db["elec"])
    with cat_font:
        render_cat_items(productos_db["font"])
    with cat_clima:
        render_cat_items(productos_db["clima"])
    with cat_obras:
        render_cat_items(productos_db["obras"])
    with cat_packs:
        render_cat_items(productos_db["packs"])

    st.markdown("---")
    col_p3_btn1, col_p3_btn2 = st.columns([2, 2])
    with col_p3_btn1:
        if st.button("⬅️ Paso Anterior: Cálculos Técnicos", key="btn_p3_prev"):
            st.session_state.paso_actual = "2. Cálculos Técnicos"
            st.rerun()
    with col_p3_btn2:
        if st.button("Siguiente Paso: Ver Presupuesto Completo ➔", key="btn_p3_next"):
            st.session_state.paso_actual = "4. Presupuesto"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO Y EXPORTACIÓN A EXCEL
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "4. Presupuesto":
    st.subheader("📊 Paso 4: Resumen General del Presupuesto Comercial")
    
    if not st.session_state.cesta:
        st.warning("Aún no has añadido partidas al presupuesto. Ve al paso 3 (Tarifas) para incluir trabajos.")
    else:
        filas_pres = []
        for item_id, d in st.session_state.cesta.items():
            filas_pres.append({
                "Partida / Material": d['nombre'],
                "Unidad": d['unidad'],
                "Cantidad": d['cantidad'],
                "Precio Unitario (€)": d['precio_unitario'],
                "Importe Total (€)": d['cantidad'] * d['precio_unitario']
            })
        
        df_pres = pd.DataFrame(filas_pres)
        
        st.dataframe(
            df_pres.style.format({
                "Cantidad": "{:.1f}",
                "Precio Unitario (€)": "{:.2f} €",
                "Importe Total (€)": "{:.2f} €"
            }),
            use_container_width=True
        )
        
        sub = df_pres["Importe Total (€)"].sum()
        iva_val = sub * (tipo_iva / 100)
        tot_val = sub + iva_val
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Base Imponible", f"{sub:,.2f} €")
        col_r2.metric(f"IVA ({tipo_iva}%)", f"{iva_val:,.2f} €")
        col_r3.metric("TOTAL PRESUPUESTO", f"{tot_val:,.2f} €")
        
        st.markdown("---")
        
        # Generar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_pres.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')
            
            df_res = pd.DataFrame([
                {"Concepto": "Cliente / Empresa", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
                {"Concepto": "Dirección de Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
                {"Concepto": "Superficie Útil (m²)", "Valor": f"{st.session_state.superficie_m2:.1f} m²"},
                {"Concepto": "Base Imponible", "Valor": f"{sub:.2f} €"},
                {"Concepto": "IVA Aplicable", "Valor": f"{tipo_iva}% ({iva_val:.2f} €)"},
                {"Concepto": "Total Presupuesto", "Valor": f"{tot_val:.2f} €"}
            ])
            df_res.to_excel(writer, index=False, sheet_name='Datos_Cliente')
            
        excel_bytes = output.getvalue()
        
        st.download_button(
            label="🟢 Descargar Presupuesto Completo en Excel (.xlsx)",
            data=excel_bytes,
            file_name="Presupuesto_Tecnico_Reformas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("---")
    col_p4_btn1, col_p4_btn2 = st.columns([2, 2])
    with col_p4_btn1:
        if st.button("⬅️ Paso Anterior: Tarifas", key="btn_p4_prev"):
            st.session_state.paso_actual = "3. Tarifas (€0)"
            st.rerun()
    with col_p4_btn2:
        if st.button("Ir a Biblioteca Normativa ➔", key="btn_p4_next"):
            st.session_state.paso_actual = "5. Biblioteca Normativa"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA NORMATIVA DE CONSULTA
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "5. Biblioteca Normativa":
    st.subheader("📚 Paso 5: Biblioteca de Normas Técnicas y Guías de Apoyo")
    st.write("Resumen ejecutivo de reglamentos oficiales aplicables a instalaciones residenciales y comerciales:")
    
    st.markdown("### ⚡ REBT (Real Decreto 842/2002)")
    st.info("Reglamento Electrotécnico para Baja Tensión. Establece las instrucciones técnicas complementarias (ITC-BT) "
            "para garantizar la seguridad de las personas y el correcto funcionamiento de las instalaciones eléctricas.")
    
    st.markdown("### 💧 CTE DB-HS4 y DB-HS5 (Código Técnico de la Edificación)")
    st.info("Documentos Básicos de Salubridad. El DB-HS4 regula el suministro de agua fría y caliente sanitaria (caudales, dimensiones y materiales), "
            "mientras que el DB-HS5 establece el diseño y evacuación de las redes de aguas pluviales y residuales.")
    
    st.markdown("### ❄️ RITE (Real Decreto 1027/2007)")
    st.info("Reglamento de Instalaciones Térmicas en los Edificios. Dicta las exigencias de eficiencia energética, "
            "seguridad y confort térmico en calefacción, climatización, ventilación y agua caliente sanitaria (ACS).")

    st.markdown("### 📡 ICT2 (Real Decreto 346/2011)")
    st.info("Reglamento de Infraestructuras Comunes de Telecomunicaciones. Obliga a la instalación de cableado de datos "
            "Categoría 6, distribución de TV/SAT y acceso de Fibra Óptica (FTTH) hasta el PAU de cada vivienda.")

    st.markdown("---")
    if st.button("🏠 Volver al Inicio (Paso 1: Estancias)", key="btn_p5_home"):
        st.session_state.paso_actual = "1. Estancias"
        st.rerun()
