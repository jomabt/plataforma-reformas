"""PRO-REFORMAS: cálculo técnico orientativo y presupuestos (versión en un solo archivo).

AVISO: resultados ORIENTATIVOS. No sustituyen la memoria técnica ni el proyecto de un
instalador autorizado o técnico competente.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    HAY_OPENPYXL = True
except ImportError:
    HAY_OPENPYXL = False


# ----------------------------------------------------------------------------
# ELECTRICIDAD (REBT)
# ----------------------------------------------------------------------------
TENSION_V = 230.0
# Conductividad del cobre a temperatura de servicio (no a 20 °C, que da 56).
CONDUCTIVIDAD_CU = {"PVC (70 °C)": 48.0, "XLPE/EPR (90 °C)": 44.0}
SECCIONES_MM2 = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50]
# Intensidad admisible ORIENTATIVA (Cu, empotrado en tubo). Valores conservadores (PVC):
# con XLPE la admisible real es mayor. Verificar con ITC-BT-19, tabla 1.
I_ADMISIBLE_A = {1.5: 15, 2.5: 21, 4: 27, 6: 36, 10: 50, 16: 66, 25: 84, 35: 104, 50: 125}
SECCION_MIN_DI_MM2 = 6  # ITC-BT-15
POTENCIAS_PREVISTAS_W = {"Básica": [5750], "Elevada": [9200, 11500, 14490]}

# Circuitos (ITC-BT-25): descripción, PIA (A), sección (mm²), tubo (mm)
CIRCUITOS = {
    "C1": ("Iluminación", 10, 1.5, 16),
    "C2": ("Tomas de uso general y frigorífico", 16, 2.5, 20),
    "C3": ("Cocina y horno", 25, 6, 25),
    "C4": ("Lavadora, lavavajillas y termo", 20, 4, 20),
    "C5": ("Baños y tomas auxiliares de cocina", 16, 2.5, 20),
    "C8": ("Calefacción eléctrica", 25, 6, 25),
    "C9": ("Aire acondicionado", 25, 6, 25),
    "C10": ("Secadora", 16, 2.5, 20),
}
MAX_PUNTOS = {"C1": 30, "C2": 20, "C5": 6}

# Mínimos SIMPLIFICADOS por estancia: (puntos de luz, tomas C2, tomas C5).
# En salones y pasillos aumentan con la superficie/longitud (ITC-BT-25, tabla 2).
MINIMOS_ESTANCIA = {
    "dormitorios": (1, 3, 0),
    "salones": (1, 3, 0),
    "banos": (1, 0, 1),
    "aseos": (1, 0, 1),
    "cocinas": (1, 2, 3),
    "galerias": (1, 1, 0),
    "terrazas": (1, 0, 0),
    "trasteros": (1, 1, 0),
}


def grado_recomendado(superficie_m2: float, calefaccion: bool, aire: bool) -> str:
    """Elevada si superficie > 160 m², calefacción eléctrica o aire acondicionado."""
    return "Elevada" if (superficie_m2 > 160 or calefaccion or aire) else "Básica"


def derivacion_individual(potencia_w: float, longitud_m: float,
                          aislamiento: str = "PVC (70 °C)", cos_phi: float = 1.0,
                          caida_max_pct: float = 1.5) -> dict:
    """Sección de la derivación individual (monofásica): máximo entre caída de tensión,
    intensidad admisible y el mínimo reglamentario de 6 mm²."""
    if potencia_w <= 0 or longitud_m <= 0:
        raise ValueError("Potencia y longitud deben ser mayores que 0.")
    gamma = CONDUCTIVIDAD_CU[aislamiento]
    intensidad = potencia_w / (TENSION_V * cos_phi)
    e_max = TENSION_V * caida_max_pct / 100
    s_caida = 2 * longitud_m * potencia_w / (gamma * e_max * TENSION_V)
    s_int = next((s for s in SECCIONES_MM2 if I_ADMISIBLE_A[s] >= intensidad), None)
    if s_int is None:
        raise ValueError("Intensidad fuera de tabla: calcular manualmente.")
    minimo = max(SECCION_MIN_DI_MM2, s_caida, s_int)
    s_final = next((s for s in SECCIONES_MM2 if s >= minimo), None)
    if s_final is None:
        raise ValueError("Sección > 50 mm²: revisar longitud/potencia o usar otra solución.")
    caida_pct = (2 * longitud_m * potencia_w / (gamma * s_final * TENSION_V)) / TENSION_V * 100
    return {"intensidad_a": intensidad, "s_caida": s_caida, "s_int": s_int,
            "seccion_mm2": s_final, "caida_pct": caida_pct}


def circuitos(estancias: dict, pasillo_m: float = 0.0, extras: dict | None = None):
    """Circuitos y puntos mínimos. Devuelve (filas_tabla, resumen_puntos)."""
    extras = extras or {}
    luz = c2 = c5 = 0
    for tipo, n in estancias.items():
        l, t2, t5 = MINIMOS_ESTANCIA[tipo]
        luz, c2, c5 = luz + l * n, c2 + t2 * n, c5 + t5 * n
    if pasillo_m > 0:  # 1 punto de luz y 1 toma por cada 5 m de pasillo
        luz += math.ceil(pasillo_m / 5)
        c2 += math.ceil(pasillo_m / 5)

    n_circ = {
        "C1": math.ceil(luz / MAX_PUNTOS["C1"]) if luz else 0,
        "C2": math.ceil(c2 / MAX_PUNTOS["C2"]) if c2 else 0,
        "C3": 1 if estancias.get("cocinas", 0) > 0 else 0,
        "C4": 1 if (estancias.get("cocinas", 0) > 0 or estancias.get("galerias", 0) > 0) else 0,
        "C5": math.ceil(c5 / MAX_PUNTOS["C5"]) if c5 else 0,
        "C8": 1 if extras.get("C8") else 0,
        "C9": 1 if extras.get("C9") else 0,
        "C10": 1 if extras.get("C10") else 0,
    }
    puntos = {"C1": luz, "C2": c2, "C5": c5}
    filas = []
    for cod, n in n_circ.items():
        if n:
            desc, pia, seccion, tubo = CIRCUITOS[cod]
            filas.append({"Circuito": cod, "Descripción": desc, "Nº circuitos": n,
                          "PIA (A)": pia, "Sección (mm²)": seccion, "Tubo (mm)": tubo,
                          "Puntos previstos": puntos.get(cod, "—")})
    return filas, {"puntos_luz": luz, "tomas_c2": c2, "tomas_c5": c5}


# ----------------------------------------------------------------------------
# FONTANERÍA (CTE DB-HS4)
# ----------------------------------------------------------------------------
# Caudal instantáneo mínimo por aparato (dm³/s): (agua fría, ACS). CTE DB-HS4, tabla 2.1.
APARATOS = {
    "lavabo": (0.10, 0.065), "ducha": (0.20, 0.10), "inodoro": (0.10, 0.0),
    "fregadero": (0.20, 0.10), "lavavajillas": (0.15, 0.10), "lavadora": (0.20, 0.15),
}


def hidraulica(n_banos: int, n_aseos: int, n_cocinas: int, n_galerias: int,
               velocidad_ms: float = 1.5) -> dict:
    """Caudal de diseño con coeficiente de simultaneidad 1/√(n−1) y diámetro interior mínimo."""
    ap = Counter()
    ap["lavabo"] = n_banos + n_aseos
    ap["ducha"] = n_banos
    ap["inodoro"] = n_banos + n_aseos
    ap["fregadero"] = n_cocinas
    ap["lavavajillas"] = n_cocinas
    ap["lavadora"] = n_galerias if n_galerias else min(n_cocinas, 1)
    n = sum(ap.values())
    q_fria = sum(c * APARATOS[a][0] for a, c in ap.items())
    q_acs = sum(c * APARATOS[a][1] for a, c in ap.items())
    kn = 1.0 if n <= 2 else 1 / math.sqrt(n - 1)
    q_diseno = q_fria * kn
    diametro = math.sqrt(4 * (q_diseno / 1000) / (math.pi * velocidad_ms)) * 1000 if q_diseno else 0.0
    return {"n_aparatos": n, "q_fria": q_fria, "q_acs": q_acs, "kn": kn,
            "q_diseno": q_diseno, "diametro_mm": diametro}


# ----------------------------------------------------------------------------
# CLIMATIZACIÓN (estimación por ratio; NO es un cálculo de cargas RITE)
# ----------------------------------------------------------------------------
RATIOS_W_M2 = {"Buena (80 W/m²)": 80, "Media (100 W/m²)": 100, "Deficiente (120 W/m²)": 120}


def climatizacion(superficie_m2: float, w_m2: float) -> dict:
    kw = superficie_m2 * w_m2 / 1000
    return {"kw": kw, "kcal_h": kw * 860}


# ----------------------------------------------------------------------------
# PRESUPUESTO
# ----------------------------------------------------------------------------
def partidas(d) -> list[dict]:
    """Partidas del presupuesto a partir de un mapeo (p. ej. st.session_state)."""
    sup = d["superficie"]
    out = []

    def add(cap, texto, ud, cant, precio):
        out.append({"Capítulo": cap, "Partida": texto, "Ud": ud, "Cantidad": cant,
                    "Precio unit. (€)": precio, "Importe (€)": cant * precio})

    if d["inc_elec"]:
        add("Electricidad", "Instalación eléctrica general", "m²", sup, d["pu_elec_m2"])
        add("Electricidad", "Cuadro general de mando y protección", "ud",
            1 if sup > 0 else 0, d["pu_elec_cgmp"])
    if d["inc_font"]:
        add("Fontanería", "Instalación de baño completo", "ud", d["n_banos"], d["pu_font_bano"])
        add("Fontanería", "Instalación de aseo", "ud", d["n_aseos"], d["pu_font_aseo"])
        add("Fontanería", "Instalación de cocina", "ud", d["n_cocinas"], d["pu_font_cocina"])
    if d["inc_clima"]:
        kw = climatizacion(sup, calc_w_m2(d))["kw"]
        add("Climatización", "Instalación de climatización", "kW", kw, d["pu_clima_kw"])
    if d["inc_teleco"]:
        tomas = d["n_dormitorios"] * d["tomas_datos_dorm"] + d["n_salones"] * d["tomas_datos_salon"]
        add("Telecomunicaciones", "Toma de datos RJ45 Cat6", "toma", tomas, d["pu_teleco_toma"])
    if d["inc_albanil"]:
        add("Albañilería", "Rozas, ayudas y remates", "m²", sup, d["pu_albanil_m2"])
    return out


def calc_w_m2(d) -> float:
    return RATIOS_W_M2[d["aislamiento_termico"]]


def totales(filas: list[dict], iva_pct: float) -> tuple[float, float, float]:
    base = sum(f["Importe (€)"] for f in filas)
    iva = base * iva_pct / 100
    return base, iva, base + iva


FUENTE = "Arial"
EUR = '#,##0.00 "€"'


def presupuesto_excel(filas: list[dict], cliente: str, obra: str,
                      superficie: float, iva_pct: float) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Presupuesto"

    ws["A1"] = "PRESUPUESTO DE REFORMA"
    ws["A1"].font = Font(name=FUENTE, size=14, bold=True, color="0F2C59")
    for fila, (etiqueta, valor) in enumerate(
        [("Cliente:", cliente or "Sin especificar"),
         ("Obra:", obra or "Sin especificar"),
         ("Superficie (m²):", superficie),
         ("Fecha:", date.today())], start=2):
        ws.cell(fila, 1, etiqueta).font = Font(name=FUENTE, bold=True)
        ws.cell(fila, 2, valor).font = Font(name=FUENTE)
        ws.cell(fila, 2).alignment = Alignment(horizontal="left")
    ws["B5"].number_format = "dd/mm/yyyy"

    cab = 7
    for col, titulo in enumerate(
            ["Capítulo", "Partida", "Ud", "Cantidad", "Precio unit. (€)", "Importe (€)"], start=1):
        c = ws.cell(cab, col, titulo)
        c.font = Font(name=FUENTE, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="0F2C59")
        c.alignment = Alignment(horizontal="center")

    primera = cab + 1
    for i, f in enumerate(filas):
        r = primera + i
        ws.cell(r, 1, f["Capítulo"])
        ws.cell(r, 2, f["Partida"])
        ws.cell(r, 3, f["Ud"])
        ws.cell(r, 4, round(f["Cantidad"], 2)).number_format = "#,##0.00"
        ws.cell(r, 5, f["Precio unit. (€)"]).number_format = EUR
        ws.cell(r, 6, f"=D{r}*E{r}").number_format = EUR  # fórmula, no valor fijo
        for col in range(1, 7):
            ws.cell(r, col).font = Font(name=FUENTE)
    ultima = primera + len(filas) - 1

    t = ultima + 2
    ws.cell(t, 5, "Base imponible")
    ws.cell(t, 6, f"=SUM(F{primera}:F{ultima})").number_format = EUR
    ws.cell(t + 1, 4, iva_pct).number_format = '0"% IVA"'
    ws.cell(t + 1, 5, "IVA")
    ws.cell(t + 1, 6, f"=F{t}*D{t + 1}/100").number_format = EUR
    ws.cell(t + 2, 5, "TOTAL")
    ws.cell(t + 2, 6, f"=F{t}+F{t + 1}").number_format = EUR
    for r in range(t, t + 3):
        for col in (4, 5, 6):
            ws.cell(r, col).font = Font(name=FUENTE, bold=(r == t + 2))

    ws.cell(t + 4, 1, "Las celdas de Cantidad, Precio y % de IVA son editables; "
                      "los importes se recalculan.").font = Font(name=FUENTE, italic=True)

    for col, ancho in zip("ABCDEF", (22, 46, 8, 12, 18, 16)):
        ws.column_dimensions[col].width = ancho

    salida = BytesIO()
    wb.save(salida)
    return salida.getvalue()


st.set_page_config(page_title="PRO-REFORMAS | Cálculo y presupuestos", page_icon="⚡", layout="wide")

# Estilo mínimo y estable: los colores viven en .streamlit/config.toml
st.markdown("""
<style>
.cabecera{background:#0F2C59;border-left:8px solid #FFC107;padding:1.4rem 2rem;
          border-radius:10px;margin-bottom:1rem}
.cabecera h1{color:#FFFFFF;font-size:2rem;margin:0;padding:0}
.cabecera p{color:#9CC7FF;margin:.3rem 0 0 0;font-size:1.05rem}
</style>
<div class="cabecera">
  <h1>⚡ PRO-REFORMAS</h1>
  <p>Cálculo técnico orientativo y presupuestos de electricidad, fontanería y climatización</p>
</div>
""", unsafe_allow_html=True)

# --- Estado: valores por defecto (las pestañas siempre se renderizan, así que no se pierden) ---
DEFAULTS = {
    "cliente_nombre": "", "cliente_obra": "", "superficie": 0.0, "tipo_iva": 21,
    "inc_elec": True, "inc_font": True, "inc_clima": False, "inc_teleco": False, "inc_albanil": False,
    "n_dormitorios": 0, "n_salones": 0, "n_banos": 0, "n_aseos": 0,
    "n_cocinas": 0, "n_galerias": 0, "n_terrazas": 0, "n_trasteros": 0,
    "pasillo_m": 0.0, "tomas_datos_dorm": 1, "tomas_datos_salon": 2,
    "grado": "Básica", "potencia_prevista": 5750, "longitud_di": 15.0,
    "aislamiento": "PVC (70 °C)", "calefaccion_elec": False, "aire_acond": False, "secadora": False,
    "velocidad_ms": 1.5, "aislamiento_termico": "Media (100 W/m²)",
    "pu_elec_m2": 0.0, "pu_elec_cgmp": 0.0, "pu_font_bano": 0.0, "pu_font_aseo": 0.0,
    "pu_font_cocina": 0.0, "pu_clima_kw": 0.0, "pu_teleco_toma": 0.0, "pu_albanil_m2": 0.0,
}
for clave, valor in DEFAULTS.items():
    st.session_state.setdefault(clave, valor)
s = st.session_state

# --- Barra lateral ---
with st.sidebar:
    st.header("👤 Cliente y obra")
    st.text_input("Nombre del cliente / empresa", key="cliente_nombre")
    st.text_input("Dirección de la obra", key="cliente_obra")
    st.number_input("Superficie útil afectada (m²)", min_value=0.0, step=5.0, key="superficie")
    st.divider()
    st.header("🔧 Especialidades")
    st.checkbox("⚡ Electricidad (REBT)", key="inc_elec")
    st.checkbox("🚰 Fontanería (CTE DB-HS)", key="inc_font")
    st.checkbox("❄️ Climatización (RITE)", key="inc_clima")
    st.checkbox("📡 Telecomunicaciones", key="inc_teleco")
    st.checkbox("🏗️ Albañilería auxiliar", key="inc_albanil")
    st.divider()
    st.selectbox("Tipo de IVA", [21, 10], key="tipo_iva",
                 format_func=lambda x: f"{x}% ({'General' if x == 21 else 'Reducido reforma'})")
    st.caption("El 10 % solo aplica a reformas en vivienda de particulares, con más de 2 años de "
               "antigüedad y con materiales aportados por el contratista ≤ 40 % de la base. "
               "Confírmalo con tu gestor. Canarias, Ceuta y Melilla tienen otros impuestos.")

t1, t2, t3, t4, t5 = st.tabs(["📋 1. Estancias", "🛠️ 2. Cálculos", "💶 3. Tarifas",
                              "📊 4. Presupuesto", "📚 5. Biblioteca"])

# --- PASO 1: ESTANCIAS ---
with t1:
    st.subheader("Estancias y geometría")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.number_input("🛌 Dormitorios", min_value=0, step=1, key="n_dormitorios")
        st.number_input("🛋️ Salones / comedores", min_value=0, step=1, key="n_salones")
    with c2:
        st.number_input("🛁 Baños (con ducha)", min_value=0, step=1, key="n_banos")
        st.number_input("🧻 Aseos (sin ducha)", min_value=0, step=1, key="n_aseos")
    with c3:
        st.number_input("🍳 Cocinas", min_value=0, step=1, key="n_cocinas")
        st.number_input("🧺 Galerías / lavaderos", min_value=0, step=1, key="n_galerias")
    with c4:
        st.number_input("🌿 Terrazas / balcones", min_value=0, step=1, key="n_terrazas")
        st.number_input("📦 Trasteros / garajes / otros", min_value=0, step=1, key="n_trasteros")
    p1, p2, p3 = st.columns(3)
    p1.number_input("Longitud total de pasillos (m)", min_value=0.0, step=1.0, key="pasillo_m")
    p2.number_input("Tomas de datos por dormitorio", min_value=0, step=1, key="tomas_datos_dorm")
    p3.number_input("Tomas de datos por salón", min_value=0, step=1, key="tomas_datos_salon")
    total = sum(s[k] for k in DEFAULTS if k.startswith("n_"))
    st.info(f"{total} estancias | {s.superficie:.1f} m² afectados")

# --- PASO 2: CÁLCULOS ---
with t2:
    st.subheader("Dimensionado técnico")
    st.warning("Resultados orientativos. No sustituyen la memoria técnica ni el proyecto de un "
               "instalador autorizado o técnico competente.")

    with st.expander("⚡ Electricidad (REBT)", expanded=True):
        if not s.inc_elec:
            st.caption("Capítulo no incluido en el presupuesto (el cálculo sigue disponible).")
        e1, e2 = st.columns(2)
        with e1:
            st.checkbox("Calefacción eléctrica (C8)", key="calefaccion_elec")
            st.checkbox("Aire acondicionado (C9)", key="aire_acond")
            st.checkbox("Secadora (C10)", key="secadora")
        recomendado = grado_recomendado(s.superficie, s.calefaccion_elec, s.aire_acond)
        with e2:
            st.selectbox("Grado de electrificación", list(POTENCIAS_PREVISTAS_W), key="grado")
            opciones = POTENCIAS_PREVISTAS_W[s.grado]
            if s.potencia_prevista not in opciones:
                s.potencia_prevista = opciones[0]
            st.selectbox("Potencia prevista (W)", opciones, key="potencia_prevista")
        if recomendado == "Elevada" and s.grado == "Básica":
            st.warning("Con más de 160 m², calefacción eléctrica o aire acondicionado corresponde "
                       "electrificación elevada.")
        d1, d2 = st.columns(2)
        d1.number_input("Longitud de la derivación individual (m)", min_value=1.0, step=1.0,
                        key="longitud_di")
        d2.selectbox("Aislamiento del cable", list(CONDUCTIVIDAD_CU), key="aislamiento")
        try:
            di = derivacion_individual(s.potencia_prevista, s.longitud_di, s.aislamiento)
            m1, m2, m3 = st.columns(3)
            m1.metric("Intensidad", f"{di['intensidad_a']:.1f} A")
            m2.metric("Sección DI (Cu)", f"{di['seccion_mm2']:g} mm²")
            m3.metric("Caída de tensión", f"{di['caida_pct']:.2f} %", help="Límite: 1,5 % en DI")
            st.caption(f"Por caída de tensión: {di['s_caida']:.2f} mm² · por intensidad: "
                       f"{di['s_int']:g} mm² · mínimo reglamentario: 6 mm².")
        except ValueError as err:
            st.error(str(err))

        estancias = {"dormitorios": s.n_dormitorios, "salones": s.n_salones, "banos": s.n_banos,
                     "aseos": s.n_aseos, "cocinas": s.n_cocinas, "galerias": s.n_galerias,
                     "terrazas": s.n_terrazas, "trasteros": s.n_trasteros}
        filas_circ, mec = circuitos(
            estancias, s.pasillo_m,
            {"C8": s.calefaccion_elec, "C9": s.aire_acond, "C10": s.secadora})
        st.markdown("**Circuitos y puntos mínimos (ITC-BT-25, simplificado)**")
        if filas_circ:
            st.dataframe(pd.DataFrame(filas_circ), hide_index=True)
            st.caption(f"Puntos de luz: {mec['puntos_luz']} · tomas C2: {mec['tomas_c2']} · "
                       f"tomas C5: {mec['tomas_c5']}. En salones y pasillos los mínimos suben con la "
                       "superficie: ajusta según la tabla 2 de la ITC-BT-25.")
        else:
            st.info("Añade estancias en el Paso 1 para ver los circuitos.")

    with st.expander("🚰 Fontanería (CTE DB-HS4)", expanded=True):
        if not s.inc_font:
            st.caption("Capítulo no incluido en el presupuesto (el cálculo sigue disponible).")
        st.slider("Velocidad de cálculo (m/s)", 0.5, 2.0, step=0.1, key="velocidad_ms")
        h = hidraulica(s.n_banos, s.n_aseos, s.n_cocinas, s.n_galerias, s.velocidad_ms)
        if h["n_aparatos"]:
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Aparatos", h["n_aparatos"])
            f2.metric("Caudal instalado (fría)", f"{h['q_fria']:.2f} L/s")
            f3.metric("Caudal de diseño", f"{h['q_diseno']:.2f} L/s",
                      help=f"Coeficiente de simultaneidad {h['kn']:.2f} = 1/√(n−1)")
            f4.metric("Ø interior mín. general", f"{h['diametro_mm']:.1f} mm")
            st.caption("Caudales por aparato según tabla 2.1 del DB-HS4. Falta dimensionar los "
                       "ramales y comprobar presión (mín. 100 kPa en grifos, 150 kPa en fluxores y "
                       "calentadores; máx. 500 kPa).")
        else:
            st.info("Configura baños, aseos o cocinas en el Paso 1.")

    with st.expander("❄️ Climatización (estimación por ratio)", expanded=True):
        if not s.inc_clima:
            st.caption("Capítulo no incluido en el presupuesto (el cálculo sigue disponible).")
        if s.superficie > 0:
            st.selectbox("Aislamiento térmico del inmueble", list(RATIOS_W_M2),
                         key="aislamiento_termico")
            cl = climatizacion(s.superficie, calc_w_m2(s))
            st.metric("Potencia térmica estimada", f"{cl['kw']:.2f} kW", f"{cl['kcal_h']:.0f} kcal/h")
            st.caption("Estimación orientativa por ratio: no es un cálculo de cargas según RITE.")
        else:
            st.info("Introduce la superficie en el menú lateral.")

# --- PASO 3: TARIFAS ---
with t3:
    st.subheader("Cuadro de precios unitarios")
    st.caption("Todos los precios parten de 0 €: define las tarifas acordadas (sin IVA).")
    a, b = st.columns(2)
    with a:
        st.markdown("#### ⚡ Electricidad")
        st.number_input("Instalación eléctrica general (€/m²)", min_value=0.0, step=5.0, key="pu_elec_m2")
        st.number_input("Cuadro general y protecciones (€/ud)", min_value=0.0, step=25.0, key="pu_elec_cgmp")
        st.markdown("#### 🚰 Fontanería")
        st.number_input("Baño completo (€/ud)", min_value=0.0, step=50.0, key="pu_font_bano")
        st.number_input("Aseo (€/ud)", min_value=0.0, step=50.0, key="pu_font_aseo")
        st.number_input("Cocina (€/ud)", min_value=0.0, step=50.0, key="pu_font_cocina")
    with b:
        st.markdown("#### ❄️ Climatización")
        st.number_input("Instalación (€/kW)", min_value=0.0, step=25.0, key="pu_clima_kw")
        st.markdown("#### 📡 Telecomunicaciones")
        st.number_input("Toma de datos RJ45 Cat6 (€/toma)", min_value=0.0, step=5.0, key="pu_teleco_toma")
        st.markdown("#### 🏗️ Albañilería")
        st.number_input("Rozas, ayudas y remates (€/m²)", min_value=0.0, step=5.0, key="pu_albanil_m2")

# --- PASO 4: PRESUPUESTO ---
with t4:
    st.subheader("Mediciones y presupuesto")
    filas = partidas(s)
    if filas:
        df = pd.DataFrame(filas)
        st.dataframe(df, hide_index=True, column_config={
            "Cantidad": st.column_config.NumberColumn(format="%.2f"),
            "Precio unit. (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Importe (€)": st.column_config.NumberColumn(format="%.2f €"),
        })
        base, iva, total_pres = totales(filas, s.tipo_iva)
        r1, r2, r3 = st.columns(3)
        r1.metric("Base imponible", f"{base:,.2f} €")
        r2.metric(f"IVA ({s.tipo_iva}%)", f"{iva:,.2f} €")
        r3.metric("TOTAL", f"{total_pres:,.2f} €")
        nombre = re.sub(r"[^\w\-]+", "_", s.cliente_nombre.strip()) or "Reforma"
        if HAY_OPENPYXL:
            st.download_button(
                "🟢 Descargar presupuesto en Excel (.xlsx)",
                data=presupuesto_excel(filas, s.cliente_nombre, s.cliente_obra, s.superficie, s.tipo_iva),
                file_name=f"Presupuesto_{nombre}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("Para descargar el Excel, añade la línea 'openpyxl' al archivo requirements.txt.")
    else:
        st.info("Selecciona al menos una especialidad en el menú lateral.")

# --- PASO 5: BIBLIOTECA ---
with t5:
    st.subheader("Referencias normativas")
    n1, n2, n3, n4 = st.tabs(["⚡ REBT", "🚰 CTE DB-HS", "❄️ RITE", "📡 Telecomunicaciones"])
    with n1:
        st.markdown("- **ITC-BT-25:** circuitos C1 (iluminación), C2 (tomas generales), C3 (cocina y "
                    "horno), C4 (lavadora, lavavajillas, termo), C5 (baños y auxiliares de cocina); "
                    "en electrificación elevada, C8 a C12.\n"
                    "- **ITC-BT-15:** derivación individual de 6 mm² como mínimo.\n"
                    "- **Caída de tensión:** 1,5 % en derivación individual; 3 % en la instalación "
                    "interior de viviendas.")
    with n2:
        st.markdown("- **DB-HS4, tabla 2.1:** lavabo 0,10 · ducha 0,20 · fregadero 0,20 · "
                    "lavavajillas 0,15 · lavadora 0,20 · inodoro con cisterna 0,10 (L/s, agua fría).\n"
                    "- **Presión:** mínimo 100 kPa en grifos y 150 kPa en fluxores y calentadores; "
                    "máximo 500 kPa.\n- **DB-HS5:** evacuación de aguas.")
    with n3:
        st.markdown("- **RITE (RD 1027/2007):** regulación por termostato, eficiencia energética y "
                    "mantenimiento de instalaciones térmicas.")
    with n4:
        st.markdown("- **Reglamento ICT (RD 346/2011):** infraestructuras comunes de telecomunicaciones. "
                    "La red interior de datos (Cat6) se presupuesta por tomas.")
