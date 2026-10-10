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
# ESTILOS CSS CON ALTA VISIBILIDAD (COMPATIBLE CON MODO CLARO Y OSCURO)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal claro y limpio */
    .stApp {
        background-color: #F8FAFC !important;
    }
    
    /* Encabezado principal estilo Manual Técnico */
    .header-rite {
        background: linear-gradient(135deg, #1B365D 0%, #0F2540 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
        border-left: 8px solid #E65100;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #CBD5E1 !important;
        font-size: 1.0rem;
        margin-top: 0.3rem;
    }
    .header-badge {
        background-color: #E65100;
        color: #FFFFFF !important;
        padding: 0.35rem 0.9rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        margin-top: 0.6rem;
    }

    /* Tarjeta de producto con excelente legibilidad */
    .card-product {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-top: 5px solid #1B365D !important;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .card-title {
        color: #0F172A !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    .card-desc {
        color: #334155 !important;
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
        margin-bottom: 0.8rem !important;
        min-height: 50px;
    }
    .price-tag {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #1B365D !important;
    }
    .unit-tag {
        font-size: 0.85rem !important;
        color: #475569 !important;
        font-weight: 700 !important;
    }

    /* Forzar legibilidad extrema en etiquetas de formularios e inputs */
    label, .stWidgetLabel, div[data-baseweb="label"] {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    
    /* Cajas de número e inputs con bordes oscuros y texto nítido */
    input {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border: 1px solid #94A3B8 !important;
        font-weight: 700 !important;
    }

    /* Botones de acción principales (Naranja de seguridad) */
    .stButton>button {
        background-color: #E65100 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
        font-size: 0.95rem !important;
    }
    .stButton>button:hover {
        background-color: #C64000 !important;
        color: #FFFFFF !important;
    }

    /* Botón secundario de volver */
    .btn-volver button {
        background-color: #334155 !important;
        color: #FFFFFF !important;
    }
    .btn-volver button:hover {
        background-color: #1E293B !important;
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

if 'seccion_actual' not in st.session_state:
    st.session_state.seccion_actual = "catalogo"

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-rite">
    <div class="header-title">📘 ALMACÉN TÉCNICO & SERVICIOS NORMATIVOS</div>
    <div class="header-subtitle">Presupuestador Guiado según Reglamento RITE, REBT, CTE DB-HS e ICT2</div>
    <div class="header-badge">PRECIOS 100% CONFIGURABLES EN €0.00 DE INICIO</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA DE NAVEGACIÓN Y BOTONES "VOLVER / IR A"
# -----------------------------------------------------------------------------
col_nav1, col_nav2, col_nav3 = st.columns([2, 2, 2])

with col_nav1:
    if st.button("📋 1. Ir al Catálogo de Servicios", key="nav_cat"):
        st.session_state.seccion_actual = "catalogo"
        st.rerun()

with col_nav2:
    if st.button("🛒 2. Ver Presupuesto Activo", key="nav_pres"):
        st.session_state.seccion_actual = "presupuesto"
        st.rerun()

with col_nav3:
    if st.button("🔄 Reiniciar Todo / Limpiar Cesta", key="nav_clear"):
        st.session_state.cesta = {}
        st.session_state.cliente_nombre = ""
        st.session_state.cliente_obra = ""
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (CESTA Y DATOS DE OBRA)
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
st.sidebar.markdown("### 📋 Partidas en Cesta")

if not st.session_state.cesta:
    st.sidebar.info("La cesta está vacía. Selecciona partidas o paquetes en el catálogo.")
else:
    subtotal_cesta = 0.0
    
    for item_id, datos in list(st.session_state.cesta.items()):
        cant = datos['cantidad']
        pu = datos['precio_unitario']
        imp = cant * pu
        subtotal_cesta += imp
        
        st.sidebar.markdown(f"**{datos['nombre']}**")
        col_c1, col_c2 = st.sidebar.columns([3, 1])
        with col_c1:
            st.caption(f"Cant: **{cant:.1f} {datos['unidad']}** | PU: **{pu:.2f} €** | Total: **{imp:.2f} €**")
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
    
    if st.sidebar.button("🧹 Vaciar Presupuesto", key="btn_vaciar_side"):
        st.session_state.cesta = {}
        st.rerun()

# -----------------------------------------------------------------------------
# BASE DE DATOS CON PRECIOS EN 0.00 € POR DEFECTO
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

def render_categoria(lista_prods):
    cols = st.columns(3)
    for idx, prod in enumerate(lista_prods):
        with cols[idx % 3]:
            # Tarjeta de producto con alta visibilidad
            st.markdown(f"""
            <div class="card-product">
                <div class="card-title">{prod['nombre']}</div>
                <div class="card-desc">{prod['desc']}</div>
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.5rem;">
                    <span class="unit-tag">Medida: por {prod['unidad']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cant = st.number_input(
                f"Cantidad de {prod['nombre']} ({prod['unidad']})", 
                min_value=1.0, 
                value=1.0, 
                step=1.0, 
                key=f"cant_{prod['id']}"
            )
            pu_custom = st.number_input(
                f"Precio Unitario (€ por {prod['unidad']})", 
                min_value=0.0, 
                value=0.0, 
                step=10.0, 
                format="%.2f",
                key=f"pu_{prod['id']}"
            )
            
            if st.button(f"🛒 Añadir {prod['nombre']} al Presupuesto", key=f"btn_{prod['id']}"):
                st.session_state.cesta[prod['id']] = {
                    "nombre": prod['nombre'],
                    "unidad": prod['unidad'],
                    "cantidad": cant,
                    "precio_unitario": pu_custom
                }
                st.success(f"✔️ Añadido: {cant:.1f} {prod['unidad']} a {pu_custom:.2f} €/unidad")
                st.rerun()

# -----------------------------------------------------------------------------
# RENDERIZADO DE SECCIÓN SEGÚN NAVEGACIÓN
# -----------------------------------------------------------------------------
if st.session_state.seccion_actual == "catalogo":
    st.subheader("📋 Catálogo Técnico por Especialidad (Inicia en 0.00 €)")
    st.write("Configura la cantidad y la tarifa unitaria (€) de cada elemento antes de añadirlo al presupuesto:")
    
    cat_elec, cat_font, cat_clima, cat_obras, cat_packs = st.tabs([
        "⚡ Electricidad (REBT)",
        "🚰 Fontanería (CTE)",
        "❄️ Climatización (RITE)",
        "🏗️ Albañilería y Acabados",
        "📦 Packs Llave en Mano"
    ])

    with cat_elec:
        st.markdown("#### ⚡ Instalaciones Eléctricas (REBT - RD 842/2002)")
        render_categoria(productos_db["elec"])

    with cat_font:
        st.markdown("#### 🚰 Fontanería y Saneamiento (CTE DB-HS4 / DB-HS5)")
        render_categoria(productos_db["font"])

    with cat_clima:
        st.markdown("#### ❄️ Climatización, Calefacción y ACS (RITE - RD 1027/2007)")
        render_categoria(productos_db["clima"])

    with cat_obras:
        st.markdown("#### 🏗️ Ayuda de Albañilería, Rozas y Remates")
        render_categoria(productos_db["obras"])

    with cat_packs:
        st.markdown("#### 📦 Packs Integrales de Reforma")
        render_categoria(productos_db["packs"])

    st.markdown("---")
    col_bottom1, col_bottom2 = st.columns([2, 2])
    with col_bottom1:
        if st.button("🛒 Ir a Ver el Presupuesto Completo", key="btn_ir_pres_bot"):
            st.session_state.seccion_actual = "presupuesto"
            st.rerun()

# -----------------------------------------------------------------------------
# SECCIÓN PRESUPUESTO
# -----------------------------------------------------------------------------
else:
    st.subheader("📊 Resumen General del Presupuesto Comercial")
    
    # Botón explícito para VOLVER AL CATÁLOGO
    if st.button("⬅️ Volver al Catálogo de Servicios", key="btn_volver_cat_top"):
        st.session_state.seccion_actual = "catalogo"
        st.rerun()

    st.markdown("---")

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
        col_r2.metric(f"IVA ({tipo_iva}%)", f"{iva_val:,.2f} €")
        col_r3.metric("TOTAL PRESUPUESTO", f"{tot_val:,.2f} €")
        
        st.markdown("---")
        
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
        st.info("La cesta está vacía. Haz clic en el botón de abajo para ir al catálogo y añadir elementos.")
    
    st.markdown("---")
    if st.button("⬅️ Volver al Catálogo de Servicios", key="btn_volver_cat_bot"):
        st.session_state.seccion_actual = "catalogo"
        st.rerun()
