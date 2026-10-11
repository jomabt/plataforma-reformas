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
# ESTILOS CSS PERSONALIZADOS (SOFT LIGHT + AZUL PROFUNDO #0F2C59 + AMARILLO #FFC107)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal suave y descansado */
    .stApp {
        background-color: #F8F9FA !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Encabezado Principal Corporativo */
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
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #E2E8F0 !important;
        font-size: 1.15rem !important;
        margin-top: 0.4rem;
        font-weight: 500;
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
        letter-spacing: 0.5px;
    }

    /* BARRA LATERAL (AZUL PROFUNDO #0F2C59) */
    section[data-testid="stSidebar"] {
        background-color: #0F2C59 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #FFC107 !important;
        font-weight: 800 !important;
    }

    /* ESTILO DE INPUTS Y SELECTBOX EN BARRA LATERAL Y PRINCIPAL */
    div[data-baseweb="input"] input, 
    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #FFC107 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    /* ETIQUETAS DE FORMULARIO CON FUENTE AUMENTADA (+2PT) */
    label, .stWidgetLabel, div[data-baseweb="label"] {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.3rem !important;
    }
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stWidgetLabel {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* BOTONES DE INCREMENTAR / DECREMENTAR (+) Y (-) EN NUMBER INPUTS */
    div[data-testid="stNumberInputStepDown"], 
    div[data-testid="stNumberInputStepUp"],
    button[aria-label="Decrease value"],
    button[aria-label="Increase value"] {
        background-color: #FFC107 !important;
        color: #0F2C59 !important;
        border: 1px solid #D9A000 !important;
        border-radius: 6px !important;
        font-weight: 900 !important;
    }
    div[data-testid="stNumberInputStepDown"]:hover, 
    div[data-testid="stNumberInputStepUp"]:hover {
        background-color: #E0A800 !important;
    }
    div[data-testid="stNumberInputStepDown"] p, 
    div[data-testid="stNumberInputStepUp"] p {
        color: #0F2C59 !important;
        font-weight: 900 !important;
        font-size: 1.2rem !important;
    }

    /* TARJETAS DE ESTANCIAS Y SERVICIOS */
    .card-estancia {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-top: 5px solid #0F2C59 !important;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.0rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    }
    .card-title {
        color: #0F2C59 !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.4rem !important;
    }
    .card-desc {
        color: #334155 !important;
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
        margin-bottom: 0.8rem !important;
    }

    /* TITULOS DE SECCIÓN AUMENTADOS (+2PT DE FUENTE) */
    h1 { font-size: 2.4rem !important; font-weight: 800 !important; color: #0F2C59 !important; }
    h2 { font-size: 2.0rem !important; font-weight: 800 !important; color: #0F2C59 !important; }
    h3 { font-size: 1.6rem !important; font-weight: 800 !important; color: #0F2C59 !important; }
    h4 { font-size: 1.3rem !important; font-weight: 800 !important; color: #0F2C59 !important; }

    /* BOTONES PRINCIPALES DE ACCIÓN (AMARILLO #FFC107) */
    .stButton>button {
        background-color: #FFC107 !important;
        color: #0F2C59 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border: 2px solid #D9A000 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100% !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08) !important;
    }
    .stButton>button:hover {
        background-color: #E0A800 !important;
        color: #000000 !important;
        border-color: #C69500 !important;
    }

    /* BOTÓN DE DESCARGA EXCEL EN VERDE */
    .stDownloadButton>button {
        background-color: #28A745 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
    }
    .stDownloadButton>button:hover {
        background-color: #218838 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INICIALIZACIÓN DE ESTADO DE SESIÓN
# -----------------------------------------------------------------------------
if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = "1. Estancias"

if 'cesta' not in st.session_state:
    st.session_state.cesta = {}

if 'cliente_nombre' not in st.session_state:
    st.session_state.cliente_nombre = ""

if 'cliente_obra' not in st.session_state:
    st.session_state.cliente_obra = ""

if 'superficie_m2' not in st.session_state:
    st.session_state.superficie_m2 = 80.0

# Conteo de estancias
estancias_default = {
    "dormitorios": 3,
    "salones": 1,
    "banos": 2,
    "aseos": 0,
    "cocinas": 1,
    "galerias": 1,
    "terrazas": 1,
    "trasteros": 1
}

for k, v in estancias_default.items():
    if f"estancia_{k}" not in st.session_state:
        st.session_state[f"estancia_{k}"] = v

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-rite">
    <div class="header-title">📘 GESTOR TÉCNICO DE REFORMAS E INSTALACIONES</div>
    <div class="header-subtitle">Presupuestador Guiado & Dimensionamiento según RITE, REBT, CTE DB-HS e ICT2</div>
    <div class="header-badge">CONFIGURACIÓN TÉCNICA Y COMERCIAL COMPLETA</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (DATOS DEL CLIENTE, OBRA Y CESTA ACTIVA)
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 👤 DATOS DE LA OBRA")

st.session_state.cliente_nombre = st.sidebar.text_input(
    "📌 Nombre del Cliente / Empresa:", 
    value=st.session_state.cliente_nombre, 
    placeholder="Ej. Juan Pérez / Reforma C/ Mayor"
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
st.sidebar.markdown("### 🛒 Cesta de Partidas Seleccionadas")

if not st.session_state.cesta:
    st.sidebar.info("La cesta está vacía. Añade partidas en los pasos 1, 2 o 3.")
else:
    subtotal_cesta = 0.0
    for item_id, datos in list(st.session_state.cesta.items()):
        cant = datos['cantidad']
        pu = datos['precio_unitario']
        imp = cant * pu
        subtotal_cesta += imp
        
        st.sidebar.markdown(f"**{datos['nombre']}**")
        st.sidebar.caption(f"{cant:.1f} {datos['unidad']} x {pu:.2f} € = **{imp:.2f} €**")
        if st.sidebar.button("🗑️ Eliminar", key=f"del_side_{item_id}"):
            del st.session_state.cesta[item_id]
            st.rerun()
        st.sidebar.markdown("---")
    
    iva_calc = subtotal_cesta * (tipo_iva / 100)
    total_calc = subtotal_cesta + iva_calc
    
    st.sidebar.metric("Subtotal Base", f"{subtotal_cesta:,.2f} €")
    st.sidebar.metric(f"IVA ({tipo_iva}%)", f"{iva_calc:,.2f} €")
    st.sidebar.metric("TOTAL PRESUPUESTO", f"{total_calc:,.2f} €")
    
    if st.sidebar.button("🧹 Vaciar Presupuesto Completo", key="btn_vaciar_side"):
        st.session_state.cesta = {}
        st.rerun()

# -----------------------------------------------------------------------------
# BARRA DE NAVEGACIÓN PASO A PASO
# -----------------------------------------------------------------------------
pasos_lista = [
    "1. Estancias", 
    "2. Cálculos Técnicos", 
    "3. Cuadro de Tarifas", 
    "4. Presupuesto Activo", 
    "5. Biblioteca Normativa"
]

paso_sel = st.radio(
    "Navegación del Asistente:",
    options=pasos_lista,
    index=pasos_lista.index(st.session_state.paso_actual) if st.session_state.paso_actual in pasos_lista else 0,
    horizontal=True,
    key="nav_radio_pasos"
)
st.session_state.paso_actual = paso_sel
st.markdown("---")

# -----------------------------------------------------------------------------
# BASE DE DATOS DE PARTIDAS TÉCNICAS (CON PRECIOS INICIALES EN 0.00 €)
# -----------------------------------------------------------------------------
productos_db = {
    "elec": [
        {
            "id": "e1", 
            "nombre": "⚡ Renovación Eléctrica General (REBT)", 
            "unidad": "m²", 
            "precio": 0.00, 
            "desc": "Cableado libre de halógenos (H07Z1-K), canalización empotrada y mecanismos según ITC-BT-25."
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
            "nombre": "💡 Punto de Luz / Toma Adicional REBT", 
            "unidad": "ud", 
            "precio": 0.00, 
            "desc": "Apertura de rozas, tubo corrugado, conductor 2.5mm² y caja de mecanismo instalada."
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
    ]
}

# -----------------------------------------------------------------------------
# PASO 1: CONFIGURACIÓN DE ESTANCIAS Y GEOMETRÍA
# -----------------------------------------------------------------------------
if st.session_state.paso_actual == "1. Estancias":
    st.subheader("📋 Paso 1: Configuración de Estancias y Geometría de la Vivienda/Local")
    st.write("Selecciona la cantidad de estancias y zonas que componen la reforma para estimar mediciones y circuitos:")
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    
    with col_e1:
        st.markdown('<div class="card-estancia"><div class="card-title">🛌 Dormitorios</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_dormitorios = st.number_input("Cantidad de Dormitorios", min_value=0, max_value=20, value=st.session_state.estancia_dormitorios, key="num_dorm")
        
        st.markdown('<div class="card-estancia"><div class="card-title">🛋️ Salón / Comedor</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_salones = st.number_input("Cantidad de Salones", min_value=0, max_value=10, value=st.session_state.estancia_salones, key="num_sal")

    with col_e2:
        st.markdown('<div class="card-estancia"><div class="card-title">🛁 Baños Completos</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_banos = st.number_input("Cantidad de Baños", min_value=0, max_value=10, value=st.session_state.estancia_banos, key="num_ban")
        
        st.markdown('<div class="card-estancia"><div class="card-title">🧻 Aseos (Sin Ducha)</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_aseos = st.number_input("Cantidad de Aseos", min_value=0, max_value=10, value=st.session_state.estancia_aseos, key="num_ase")

    with col_e3:
        st.markdown('<div class="card-estancia"><div class="card-title">🍳 Cocinas</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_cocinas = st.number_input("Cantidad de Cocinas", min_value=0, max_value=5, value=st.session_state.estancia_cocinas, key="num_coc")
        
        st.markdown('<div class="card-estancia"><div class="card-title">🧺 Galerías / Lavaderos</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_galerias = st.number_input("Cantidad de Galerías", min_value=0, max_value=5, value=st.session_state.estancia_galerias, key="num_gal")

    with col_e4:
        st.markdown('<div class="card-estancia"><div class="card-title">🌿 Terrazas / Balcones</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_terrazas = st.number_input("Cantidad de Terrazas", min_value=0, max_value=10, value=st.session_state.estancia_terrazas, key="num_ter")
        
        st.markdown('<div class="card-estancia"><div class="card-title">📦 Trasteros / Garaje</div></div>', unsafe_allow_html=True)
        st.session_state.estancia_trasteros = st.number_input("Cantidad de Trasteros", min_value=0, max_value=10, value=st.session_state.estancia_trasteros, key="num_tras")

    st.markdown("---")
    
    total_estancias = (st.session_state.estancia_dormitorios + st.session_state.estancia_salones + 
                       st.session_state.estancia_banos + st.session_state.estancia_aseos + 
                       st.session_state.estancia_cocinas + st.session_state.estancia_galerias + 
                       st.session_state.estancia_terrazas + st.session_state.estancia_trasteros)
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Total Estancias Configuradas", f"{total_estancias} zonas")
    col_res2.metric("Superficie Total Estimada", f"{st.session_state.superficie_m2:.1f} m²")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b2:
        if st.button("Siguiente Paso: 🛠️ Dimensionado Técnico ➔", key="btn_paso1_next"):
            st.session_state.paso_actual = "2. Cálculos Técnicos"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 2: DIMENSIONADO TÉCNICO Y CÁLCULOS NORMATIVOS
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "2. Cálculos Técnicos":
    st.subheader("🛠️ Paso 2: Dimensionado Técnico y Normativo (REBT, CTE, RITE, ICT2)")
    st.write("Cálculos automáticos de la instalación basados en la superficie y las estancias configuradas:")
    
    m2 = float(st.session_state.superficie_m2)
    
    # REBT
    tipo_electrificacion = "Elevada" if (m2 > 160 or st.session_state.estancia_banos > 2 or st.session_state.estancia_cocinas > 1) else "Básica"
    potencia_sugerida = 9.2 if tipo_electrificacion == "Elevada" else 5.75
    circuitos_num = 12 if tipo_electrificacion == "Elevada" else 5
    
    # CTE Fontanería
    caudal_fria = (st.session_state.estancia_banos * 0.30 + st.session_state.estancia_cocinas * 0.20 + st.session_state.estancia_galerias * 0.15)
    
    # RITE Climatización
    potencia_termica_kw = (m2 * 0.10) # 100 W/m2 estimado
    
    # ICT2
    tomas_rj45 = (st.session_state.estancia_dormitorios * 2 + st.session_state.estancia_salones * 2 + st.session_state.estancia_cocinas * 1)

    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("### ⚡ Electricidad (REBT - RD 842/2002)")
        st.info(f"**Grado de Electrificación:** {tipo_electrificacion}\n\n"
                f"**Potencia a Contratar Sugerida:** {potencia_sugerida} kW\n\n"
                f"**Circuitos Mínimos Mandatorios:** {circuitos_num} circuitos (C1 a C5" + (" + C8 a C12" if tipo_electrificacion=="Elevada" else "") + ")\n\n"
                f"**Protección Principal:** IGA 25A / Diferencial 40A 30mA Clase AC/A")
        
        st.markdown("### 🚰 Fontanería y Saneamiento (CTE DB-HS4 / DB-HS5)")
        st.success(f"**Caudal Instantáneo A.F.S. Estimado:** {caudal_fria:.2f} L/s\n\n"
                   f"**Diámetro Tubo Principal (Multicapa):** Ø25 mm / Ø20 mm\n\n"
                   f"**Unidades de Desagüe (U.D.):** {st.session_state.estancia_banos*6 + st.session_state.estancia_cocinas*3} U.D.")

    with col_t2:
        st.markdown("### ❄️ Climatización y Ventilación (RITE - RD 1027/2007)")
        st.warning(f"**Carga Térmica Estimada:** {potencia_termica_kw:.2f} kW ({potencia_termica_kw*860:.0f} Frigorías/h)\n\n"
                   f"**Caudal de Ventilación Mínimo (IDA2):** {m2 * 0.8:.1f} l/s\n\n"
                   f"**Recomendación:** Sistema Split Inverter o Conductos Zoned")

        st.markdown("### 📡 Telecomunicaciones y Datos (ICT2 - RD 346/2011)")
        st.info(f"**Tomas RJ45 Cat. 6 Requeridas:** {tomas_rj45} tomas\n\n"
                f"**Tomas Coaxial TV/SAT:** {st.session_state.estancia_dormitorios + st.session_state.estancia_salones} tomas\n\n"
                f"**Registro PAU:** Monocanalización Fibra Óptica + Coaxial")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Volver a Paso 1: Estancias", key="btn_paso2_prev"):
            st.session_state.paso_actual = "1. Estancias"
            st.rerun()
    with col_b2:
        if st.button("Siguiente Paso: 💶 Cuadro de Tarifas ➔", key="btn_paso2_next"):
            st.session_state.paso_actual = "3. Cuadro de Tarifas"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 3: CUADRO DE TARIFAS Y PRECIOS UNITARIOS (€0.00)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "3. Cuadro de Tarifas":
    st.subheader("💶 Paso 3: Cuadro de Tarifas y Precios Unitarios (Inician en €0.00)")
    st.write("Configura la cantidad y la tarifa unitaria (€) de cada partida antes de incluirla al presupuesto final:")

    cat_elec, cat_font, cat_clima, cat_obras = st.tabs([
        "⚡ Electricidad (REBT)",
        "🚰 Fontanería (CTE)",
        "❄️ Climatización (RITE)",
        "🏗️ Albañilería y Acabados"
    ])

    def render_seccion_tarifas(partidas):
        cols = st.columns(3)
        for idx, prod in enumerate(partidas):
            with cols[idx % 3]:
                st.markdown(f'''
                <div class="card-estancia">
                    <div class="card-title">{prod["nombre"]}</div>
                    <div class="card-desc">{prod["desc"]}</div>
                    <span style="font-weight:700; color:#0F2C59;">Medición por: {prod["unidad"]}</span>
                </div>
                ''', unsafe_allow_html=True)
                
                cant = st.number_input(f"Cantidad ({prod['unidad']})", min_value=1.0, value=1.0, step=1.0, key=f"cant_{prod['id']}")
                pu_custom = st.number_input(f"Precio Unitario (€ por {prod['unidad']})", min_value=0.0, value=0.0, step=5.0, format="%.2f", key=f"pu_{prod['id']}")
                
                if st.button(f"🛒 Añadir {prod['nombre']}", key=f"btn_add_{prod['id']}"):
                    st.session_state.cesta[prod['id']] = {
                        "nombre": prod['nombre'],
                        "unidad": prod['unidad'],
                        "cantidad": cant,
                        "precio_unitario": pu_custom
                    }
                    st.success(f"✔️ Añadido: {cant:.1f} {prod['unidad']} a {pu_custom:.2f} €")
                    st.rerun()

    with cat_elec:
        render_seccion_tarifas(productos_db["elec"])
    with cat_font:
        render_seccion_tarifas(productos_db["font"])
    with cat_clima:
        render_seccion_tarifas(productos_db["clima"])
    with cat_obras:
        render_seccion_tarifas(productos_db["obras"])

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Volver a Paso 2: Cálculos Técnicos", key="btn_paso3_prev"):
            st.session_state.paso_actual = "2. Cálculos Técnicos"
            st.rerun()
    with col_b2:
        if st.button("Siguiente Paso: 📊 Ver Presupuesto Completo ➔", key="btn_paso3_next"):
            st.session_state.paso_actual = "4. Presupuesto Activo"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 4: PRESUPUESTO ACTIVO Y EXPORTACIÓN EXCEL (.XLSX)
# -----------------------------------------------------------------------------
elif st.session_state.paso_actual == "4. Presupuesto Activo":
    st.subheader("📊 Paso 4: Resumen General del Presupuesto Comercial")
    
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
        col_r1.metric("Base Imponible Total", f"{sub:,.2f} €")
        col_r2.metric(f"IVA ({tipo_iva}%)", f"{iva_val:,.2f} €")
        col_r3.metric("TOTAL PRESUPUESTO", f"{tot_val:,.2f} €")
        
        st.markdown("---")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_pres.to_excel(writer, index=False, sheet_name='Presupuesto_Detallado')
            
            df_res = pd.DataFrame([
                {"Concepto": "Cliente / Empresa", "Valor": st.session_state.cliente_nombre if st.session_state.cliente_nombre else "Sin especificar"},
                {"Concepto": "Dirección de Obra", "Valor": st.session_state.cliente_obra if st.session_state.cliente_obra else "Sin especificar"},
                {"Concepto": "Superficie Útil (m²)", "Valor": f"{st.session_state.superficie_m2:.1f} m²"},
                {"Concepto": "Base Imponible", "Valor": f"{sub:.2f} €"},
                {"Concepto": "IVA Aplicable", "Valor": f"{iva_val:.2f} €"},
                {"Concepto": "Total Presupuesto", "Valor": f"{tot_val:.2f} €"}
            ])
            df_res.to_excel(writer, index=False, sheet_name='Datos_Cliente')
            
        excel_bytes = output.getvalue()
        
        st.download_button(
            label="🟢 Descargar Presupuesto Oficial en Excel (.xlsx)",
            data=excel_bytes,
            file_name="Presupuesto_Tecnico_Reformas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("La cesta está vacía. Ve al Paso 3 para añadir partidas y configurar sus importes.")

    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⬅️ Volver a Paso 3: Tarifas", key="btn_paso4_prev"):
            st.session_state.paso_actual = "3. Cuadro de Tarifas"
            st.rerun()
    with col_b2:
        if st.button("Siguiente Paso: 📚 Biblioteca Normativa ➔", key="btn_paso4_next"):
            st.session_state.paso_actual = "5. Biblioteca Normativa"
            st.rerun()

# -----------------------------------------------------------------------------
# PASO 5: BIBLIOTECA NORMATIVA
# -----------------------------------------------------------------------------
else:
    st.subheader("📚 Paso 5: Biblioteca Normativa e Información Técnica")
    st.write("Resumen de las normativas oficiales que rigen el diseño técnico de las instalaciones:")
    
    col_n1, col_n2 = st.columns(2)
    
    with col_n1:
        st.markdown("### 📘 RITE (RD 1027/2007 - Actualización 2021)")
        st.write("Reglamento de Instalaciones Térmicas en los Edificios. Exige máxima eficiencia energética, uso de renovables (solar/aerotermia), contabilización individual y mantenimiento preventivo obligatorio.")
        
        st.markdown("### ⚡ REBT (RD 842/2002)")
        st.write("Reglamento Electrotécnico para Baja Tensión. Define los circuitos mínimos (ITC-BT-25), caídas de tensión (máx 3% en vivienda), protecciones diferenciales y magneto-térmicas.")

    with col_n2:
        st.markdown("### 🚰 CTE DB-HS (HS4 / HS5)")
        st.write("Código Técnico de la Edificación - Salubridad. Establece caudales mínimos de agua (A.F.S. y A.C.S.), protecciones anti-retorno y dimensionado de bajantes/colectores de saneamiento.")
        
        st.markdown("### 📡 ICT2 (RD 346/2011)")
        st.write("Infraestructuras Comunes de Telecomunicación. Obliga a la instalación de cableado Par Trenzado Cat.6, Coaxial TV/SAT y Fibra Óptica hasta el PAU de cada vivienda.")

    st.markdown("---")
    if st.button("⬅️ Volver a Paso 4: Presupuesto Activo", key="btn_paso5_prev"):
        st.session_state.paso_actual = "4. Presupuesto Activo"
        st.rerun()
