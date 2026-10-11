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

# Estado de la normativa que usa la app. Actualízalo cada vez que revises el BOE.
NORMATIVA_FECHA = "octubre de 2026"
NORMATIVA_APLICADA = "REBT (RD 842/2002) · CTE DB-HS4 · RITE (RD 1027/2007)"


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

# Caída de tensión máxima en la derivación individual según el tipo de suministro (ITC-BT-15).
CAIDA_DI_PCT = {
    "Contadores totalmente concentrados (1 %)": 1.0,
    "Contadores en más de un lugar (0,5 %)": 0.5,
    "Usuario único, sin línea general (1,5 %)": 1.5,
}
SUMINISTRO_DI_DEFECTO = "Contadores totalmente concentrados (1 %)"

POTENCIAS_PREVISTAS_W = {"Básica": [5750], "Elevada": [9200, 11500, 14490]}
IGA_ESTANDAR_A = [10, 16, 20, 25, 32, 40, 50, 63]

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
# En salones (si se indica su superficie) y pasillos se ajustan por superficie/longitud
# (ITC-BT-25, tabla 2).
MINIMOS_ESTANCIA = {
    "vestibulos": (1, 1, 0),
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
                          caida_max_pct: float = 1.0) -> dict:
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
            "seccion_mm2": s_final, "caida_pct": caida_pct,
            "caida_max_pct": caida_max_pct, "cumple": caida_pct <= caida_max_pct + 1e-9}


def circuitos(estancias: dict, pasillo_m: float = 0.0, extras: dict | None = None,
              sup_salon_m2: float = 0.0, superficie_m2: float = 0.0, grado: str = "Básica"):
    """Circuitos y puntos mínimos. Devuelve (filas_tabla, resumen_puntos)."""
    extras = extras or {}
    luz = c2 = c5 = 0
    for tipo, n in estancias.items():
        if tipo == "salones" and sup_salon_m2 > 0:
            # Salón: 1 punto de luz (2 si > 10 m²); 1 toma por cada 6 m² (mínimo 3).
            luz += n * (1 if sup_salon_m2 <= 10 else 2)
            c2 += n * max(3, math.ceil(sup_salon_m2 / 6))
            continue
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
    # Electrificación elevada con más de 160 m²: circuito C2 adicional (C7).
    c7_por_superficie = False
    if grado == "Elevada" and superficie_m2 > 160 and 0 < n_circ["C2"] < 2:
        n_circ["C2"] = 2
        c7_por_superficie = True

    puntos = {"C1": luz, "C2": c2, "C5": c5}
    filas = []
    for cod, n in n_circ.items():
        if n:
            desc, pia, seccion, tubo = CIRCUITOS[cod]
            filas.append({"Circuito": cod, "Descripción": desc, "Nº circuitos": n,
                          "PIA (A)": pia, "Sección (mm²)": seccion, "Tubo (mm)": tubo,
                          "Puntos previstos": puntos.get(cod, "—")})
    return filas, {"puntos_luz": luz, "tomas_c2": c2, "tomas_c5": c5,
                   "c7_por_superficie": c7_por_superficie}


def protecciones(potencia_w: float, n_circuitos: int, con_spd: bool) -> list[dict]:
    """Protecciones orientativas del cuadro: IGA, diferenciales, PIA y sobretensiones."""
    intensidad = potencia_w / TENSION_V
    iga = next((a for a in IGA_ESTANDAR_A if a >= intensidad - 1e-6), None)
    n_dif = math.ceil(n_circuitos / 5) if n_circuitos else 0
    return [
        {"Elemento": "IGA (magnetotérmico general)",
         "Valor": f"{iga} A" if iga else "Revisar (fuera de tabla)",
         "Observaciones": f"Para {potencia_w:.0f} W a 230 V ({intensidad:.1f} A)"},
        {"Elemento": "Diferenciales 30 mA", "Valor": f"{n_dif} ud",
         "Observaciones": "Máximo 5 circuitos por diferencial; intensidad ≥ 25 A; tipo A "
                          "recomendado (el tipo AC dejaría de ser válido con el nuevo REBT, "
                          "aún sin publicar)"},
        {"Elemento": "PIA por circuito", "Valor": f"{n_circuitos} ud",
         "Observaciones": "Calibres en la tabla de circuitos"},
        {"Elemento": "Protector contra sobretensiones",
         "Valor": "Incluido" if con_spd else "No incluido",
         "Observaciones": "Hoy depende del tipo de instalación y del riesgo (ITC-BT-23); el "
                          "borrador del nuevo REBT lo haría obligatorio"},
    ]


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
        if d["incluir_spd"]:
            add("Electricidad", "Protector contra sobretensiones", "ud", 1, d["pu_elec_spd"])
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
    ws["A1"].font = Font(name=FUENTE, size=14, bold=True, color="0B2545")
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
        c.fill = PatternFill("solid", fgColor="0B2545")
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
    for col in (5, 6):
        ws.cell(t + 2, col).fill = PatternFill("solid", fgColor="FFC400")

    ws.cell(t + 4, 1, "Las celdas de Cantidad, Precio y % de IVA son editables; "
                      "los importes se recalculan.").font = Font(name=FUENTE, italic=True)
    ws.cell(t + 5, 1, f"Estimación orientativa con la normativa a {NORMATIVA_FECHA}; no sustituye "
                      "proyecto ni memoria técnica.").font = Font(name=FUENTE, italic=True)

    for col, ancho in zip("ABCDEF", (22, 46, 8, 12, 18, 16)):
        ws.column_dimensions[col].width = ancho

    salida = BytesIO()
    wb.save(salida)
    return salida.getvalue()


st.set_page_config(page_title="PRO-REFORMAS | Electro·Hidro", page_icon="⚡", layout="wide")

# Paleta electro-hidro: amarillo eléctrico (#FFC400) + azul agua (#0096C7) sobre azul marino (#0B2545)
ESTILO = """
<style>
.stApp{background:#F3F8FC;}
[data-testid="stMainBlockContainer"],.block-container{padding-top:4.5rem !important;max-width:1250px;}
header[data-testid="stHeader"]{background:#0B2545 !important;}
header[data-testid="stHeader"] :is(button,a,span,p){color:#EAF4FB !important;}
header[data-testid="stHeader"] svg{fill:#EAF4FB !important;}
[data-testid="stMain"] :is(p,li,h1,h2,h3,h4,label){color:#10243E;}
[data-testid="stAlert"] *{color:#10243E !important;}

/* Cabecera */
.cabecera{background:linear-gradient(90deg,#0B2545 0%,#0B5E7E 65%,#0096C7 100%);
  border-bottom:6px solid #FFC400;border-radius:12px;padding:1.2rem 1.8rem;margin-bottom:1rem;}
.cabecera .t{color:#FFFFFF !important;font-size:2rem;font-weight:800;line-height:1.2;}
.cabecera .s{color:#CDEBFA !important;font-size:1.02rem;margin-top:.3rem;}

/* Bandas de sección por capítulo */
.banda{border-radius:10px;padding:.5rem 1rem;font-weight:800;font-size:1.08rem;margin:.5rem 0 .6rem 0;
  display:flex;justify-content:space-between;align-items:center;}
.banda .etq{font-size:.76rem;font-weight:700;padding:.15rem .65rem;border-radius:20px;background:rgba(255,255,255,.28);}
.b-elec{background:#FFC400;color:#0B2545 !important;}
.b-hidro{background:#0096C7;color:#FFFFFF !important;}
.b-clima{background:#2EC4B6;color:#06312E !important;}
.b-teleco{background:#5B5BD6;color:#FFFFFF !important;}
.b-alba{background:#6B7A8F;color:#FFFFFF !important;}
.b-marino{background:#0B2545;color:#FFFFFF !important;}

/* Tarjetas de resultado */
.kpi{background:#FFFFFF;border-radius:10px;padding:.65rem 1rem;border-left:7px solid var(--c);
  box-shadow:0 1px 4px rgba(11,37,69,.14);margin:.3rem 0;}
.kpi .l{font-size:.78rem;font-weight:700;color:#5B7088 !important;text-transform:uppercase;letter-spacing:.03em;}
.kpi .v{font-size:1.65rem;font-weight:800;color:#0B2545 !important;line-height:1.25;}
.kpi .n{font-size:.82rem;color:#5B7088 !important;}
.k-elec{--c:#FFC400;} .k-hidro{--c:#0096C7;} .k-clima{--c:#2EC4B6;} .k-marino{--c:#0B2545;}
.kpi.total{background:#FFC400;}
.kpi.total .l,.kpi.total .v,.kpi.total .n{color:#0B2545 !important;}

/* Pestañas */
button[role="tab"] p{font-weight:700;font-size:1.02rem;}
button[role="tab"][aria-selected="true"]{border-bottom:4px solid #FFC400 !important;}
button[role="tab"][aria-selected="true"] p{color:#0B5E7E !important;}
div[data-baseweb="tab-highlight"]{background:#FFC400 !important;height:4px !important;}

/* Botones */
.stButton>button,.stDownloadButton>button{background:#FFC400;color:#0B2545 !important;border:none;
  font-weight:800;border-radius:10px;width:100% !important;}
.stButton>button:hover,.stDownloadButton>button:hover{background:#E6AF00;color:#000 !important;}

/* Campos */
.stApp :is(input,textarea){background:#FFFFFF !important;color:#10243E !important;
  -webkit-text-fill-color:#10243E !important;caret-color:#10243E;}
.stApp div:has(> input:not([type="checkbox"]):not([type="radio"])),
.stApp div:has(> div > input:not([type="checkbox"]):not([type="radio"])),
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{background:#FFFFFF !important;}
[data-testid="stNumberInputContainer"],[data-testid="stTextInputRootElement"],[data-baseweb="select"]>div{
  border:2px solid #9BC4DA !important;border-radius:8px !important;}
[data-baseweb="select"] *{color:#10243E !important;}
[data-testid="stNumberInputStepUp"],[data-testid="stNumberInputStepDown"]{background:#EAF4FB !important;color:#10243E !important;}
[data-testid="stNumberInputStepUp"] svg,[data-testid="stNumberInputStepDown"] svg{fill:#10243E !important;color:#10243E !important;}
[data-baseweb="popover"] :is(ul,li,[role="option"],[role="listbox"]){background:#FFFFFF !important;color:#10243E !important;}
[data-baseweb="popover"] li:hover{background:#EAF4FB !important;}

/* Tablas propias (siempre claras) */
.tabla-wrap{overflow-x:auto;margin:.4rem 0 .9rem 0;}
.tabla{width:100%;border-collapse:collapse;background:#FFFFFF;box-shadow:0 1px 4px rgba(11,37,69,.14);}
.tabla th{background:#0B2545;color:#FFFFFF !important;padding:.5rem .7rem;text-align:left;font-size:.85rem;}
.tabla td{background:#FFFFFF;color:#10243E !important;padding:.45rem .7rem;border-bottom:1px solid #E1ECF4;}
.tabla tr:nth-child(even) td{background:#F3F8FC;}

/* Barra lateral */
section[data-testid="stSidebar"]{background:#0B2545 !important;}
section[data-testid="stSidebar"] :is(p,span,label,h1,h2,h3,h4,li,div){color:#EAF4FB;}
section[data-testid="stSidebar"] :is([data-testid="stNumberInputContainer"],[data-testid="stTextInputRootElement"],[data-baseweb="select"]>div){border:2px solid #FFC400 !important;}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] *{color:#10243E !important;}
.logo{font-size:1.45rem;font-weight:800;color:#FFC400 !important;margin-bottom:.4rem;}
.barra{background:rgba(255,255,255,.22);border-radius:20px;height:10px;margin:.2rem 0 .5rem 0;}
.barra>div{background:#FFC400;height:10px;border-radius:20px;}
</style>
<div class="cabecera">
  <div class="t">⚡ PRO-REFORMAS 💧</div>
  <div class="s">Electricidad y fontanería: cálculo técnico orientativo y presupuestos en 4 pasos</div>
</div>
"""
st.markdown(ESTILO, unsafe_allow_html=True)


def banda(clase, titulo, etiqueta=""):
    etq = f'<span class="etq">{etiqueta}</span>' if etiqueta else ""
    st.markdown(f'<div class="banda b-{clase}"><span>{titulo}</span>{etq}</div>', unsafe_allow_html=True)


def tabla(df, formatos=None):
    html = df.to_html(index=False, escape=True, border=0, classes="tabla", formatters=formatos or {})
    st.markdown(f'<div class="tabla-wrap">{html.replace(chr(10), "")}</div>', unsafe_allow_html=True)


def kpi(clase, etiqueta, valor, nota="", extra=""):
    st.markdown(f'<div class="kpi k-{clase} {extra}"><div class="l">{etiqueta}</div>'
                f'<div class="v">{valor}</div><div class="n">{nota}</div></div>', unsafe_allow_html=True)


# --- Estado: valores por defecto (las pestañas siempre se renderizan, así que no se pierden) ---
DEFAULTS = {
    "cliente_nombre": "", "cliente_obra": "", "superficie": 0.0, "tipo_iva": 21,
    "inc_elec": True, "inc_font": True, "inc_clima": False, "inc_teleco": False, "inc_albanil": False,
    "n_vestibulos": 0, "n_dormitorios": 0, "n_salones": 0, "n_banos": 0, "n_aseos": 0,
    "n_cocinas": 0, "n_galerias": 0, "n_terrazas": 0, "n_trasteros": 0,
    "pasillo_m": 0.0, "sup_salon_m2": 0.0, "tomas_datos_dorm": 1, "tomas_datos_salon": 2,
    "grado": "Básica", "potencia_prevista": 5750, "longitud_di": 15.0,
    "aislamiento": "PVC (70 °C)", "suministro_di": SUMINISTRO_DI_DEFECTO,
    "calefaccion_elec": False, "aire_acond": False, "secadora": False, "incluir_spd": False,
    "velocidad_ms": 1.5, "aislamiento_termico": "Media (100 W/m²)",
    "pu_elec_m2": 0.0, "pu_elec_cgmp": 0.0, "pu_elec_spd": 0.0, "pu_font_bano": 0.0,
    "pu_font_aseo": 0.0, "pu_font_cocina": 0.0, "pu_clima_kw": 0.0, "pu_teleco_toma": 0.0,
    "pu_albanil_m2": 0.0,
}
for clave, valor in DEFAULTS.items():
    st.session_state.setdefault(clave, valor)
s = st.session_state

CLAVES_ESTANCIAS = ["n_vestibulos", "n_dormitorios", "n_salones", "n_banos", "n_aseos",
                    "n_cocinas", "n_galerias", "n_terrazas", "n_trasteros", "pasillo_m"]
PLANTILLAS = {
    "🏢 Piso 2 hab.": dict(superficie=70.0, n_vestibulos=1, n_dormitorios=2, n_salones=1, n_banos=1,
                          n_aseos=0, n_cocinas=1, n_galerias=0, n_terrazas=1, n_trasteros=0,
                          pasillo_m=5.0),
    "🏢 Piso 3 hab.": dict(superficie=90.0, n_vestibulos=1, n_dormitorios=3, n_salones=1, n_banos=1,
                          n_aseos=1, n_cocinas=1, n_galerias=1, n_terrazas=1, n_trasteros=0,
                          pasillo_m=8.0),
    "🏡 Casa 4 hab.": dict(superficie=160.0, n_vestibulos=1, n_dormitorios=4, n_salones=1, n_banos=2,
                          n_aseos=1, n_cocinas=1, n_galerias=1, n_terrazas=2, n_trasteros=1,
                          pasillo_m=12.0),
    "🧹 Limpiar": dict(superficie=0.0, n_vestibulos=0, n_dormitorios=0, n_salones=0, n_banos=0,
                      n_aseos=0, n_cocinas=0, n_galerias=0, n_terrazas=0, n_trasteros=0,
                      pasillo_m=0.0, sup_salon_m2=0.0),
}


def aplicar_plantilla(nombre):
    for clave, valor in PLANTILLAS[nombre].items():
        st.session_state[clave] = valor


n_estancias = sum(s[k] for k in CLAVES_ESTANCIAS if k.startswith("n_"))
hay_precios = any(s[k] > 0 for k in DEFAULTS if k.startswith("pu_"))
filas = partidas(s)
importe_base = sum(f["Importe (€)"] for f in filas)

# --- Barra lateral ---
with st.sidebar:
    st.markdown('<div class="logo">⚡ PRO-REFORMAS 💧</div>', unsafe_allow_html=True)
    st.markdown("### 👤 Cliente y obra")
    st.text_input("Nombre del cliente / empresa", key="cliente_nombre")
    st.text_input("Dirección de la obra", key="cliente_obra")
    st.number_input("Superficie útil afectada (m²)", min_value=0.0, step=5.0, key="superficie")
    st.markdown("### 🔧 Qué incluye el presupuesto")
    st.checkbox("⚡ Electricidad", key="inc_elec")
    st.checkbox("💧 Fontanería", key="inc_font")
    st.checkbox("❄️ Climatización", key="inc_clima")
    st.checkbox("📡 Telecomunicaciones", key="inc_teleco")
    st.checkbox("🏗️ Albañilería auxiliar", key="inc_albanil")
    st.markdown("### 🏷️ IVA")
    st.selectbox("Tipo de IVA", [21, 10], key="tipo_iva", label_visibility="collapsed",
                 format_func=lambda x: f"{x}% ({'General' if x == 21 else 'Reducido reforma'})")
    st.caption("El 10 % solo aplica a reformas en vivienda de particulares, con más de 2 años de "
               "antigüedad y con materiales aportados por el contratista ≤ 40 % de la base. "
               "Confírmalo con tu gestor. Canarias, Ceuta y Melilla tienen otros impuestos.")
    pasos = [("Datos de la obra", bool(s.cliente_nombre.strip()) and s.superficie > 0),
             ("Estancias", n_estancias > 0),
             ("Tarifas", hay_precios),
             ("Presupuesto con importe", importe_base > 0)]
    hechos = sum(ok for _, ok in pasos)
    st.markdown("### ✅ Progreso")
    st.markdown(f'<div class="barra"><div style="width:{hechos * 25}%"></div></div>', unsafe_allow_html=True)
    for nombre, ok in pasos:
        st.markdown(f"{'✅' if ok else '⬜'} {nombre}")

t1, t2, t3, t4, t5 = st.tabs(["📋 1. Estancias", "🛠️ 2. Cálculos", "💶 3. Tarifas",
                              "📊 4. Presupuesto", "📚 Biblioteca"])

# --- PASO 1: ESTANCIAS ---
with t1:
    st.markdown("#### Empieza con una plantilla o rellena las estancias a mano")
    cols = st.columns(len(PLANTILLAS))
    for col, nombre in zip(cols, PLANTILLAS):
        col.button(nombre, on_click=aplicar_plantilla, args=(nombre,), key=f"plantilla_{nombre}")

    seca, humeda = st.columns(2)
    with seca:
        banda("elec", "⚡ ZONAS SECAS", "luz y enchufes")
        a, b = st.columns(2)
        a.number_input("🛌 Dormitorios", min_value=0, step=1, key="n_dormitorios")
        b.number_input("🛋️ Salones / comedores", min_value=0, step=1, key="n_salones")
        a.number_input("🚪 Vestíbulos / accesos", min_value=0, step=1, key="n_vestibulos")
        b.number_input("Superficie por salón (m²)", min_value=0.0, step=1.0, key="sup_salon_m2",
                       help="Opcional. Si la indicas, se ajustan los puntos de luz y tomas del salón.")
        a.number_input("🌿 Terrazas / balcones", min_value=0, step=1, key="n_terrazas")
        b.number_input("📦 Trasteros / garajes", min_value=0, step=1, key="n_trasteros")
        st.number_input("Longitud total de pasillos (m)", min_value=0.0, step=1.0, key="pasillo_m")
    with humeda:
        banda("hidro", "💧 ZONAS HÚMEDAS", "agua y desagües")
        a, b = st.columns(2)
        a.number_input("🛁 Baños (con ducha)", min_value=0, step=1, key="n_banos")
        b.number_input("🧻 Aseos (sin ducha)", min_value=0, step=1, key="n_aseos")
        a.number_input("🍳 Cocinas", min_value=0, step=1, key="n_cocinas")
        b.number_input("🧺 Galerías / lavaderos", min_value=0, step=1, key="n_galerias")

    banda("teleco", "📡 RED DE DATOS", "opcional")
    a, b, _ = st.columns(3)
    a.number_input("Tomas de datos por dormitorio", min_value=0, step=1, key="tomas_datos_dorm")
    b.number_input("Tomas de datos por salón", min_value=0, step=1, key="tomas_datos_salon")

    st.info(f"**{n_estancias} estancias** · **{s.superficie:.0f} m²** afectados. "
            "Recuerda indicar la superficie en la barra lateral.")
    st.caption("👉 Siguiente: pestaña **2. Cálculos**")

# --- PASO 2: CÁLCULOS ---
with t2:
    st.warning("Resultados orientativos. No sustituyen la memoria técnica ni el proyecto de un "
               "instalador autorizado o técnico competente.")
    st.caption(f"Normativa de referencia (estado a {NORMATIVA_FECHA}): {NORMATIVA_APLICADA}. "
               "La revisión del REBT no estaba publicada en el BOE a esa fecha y hay "
               "modificaciones del RITE y del CTE anunciadas: comprueba el BOE antes de cada proyecto.")

    # ELECTRICIDAD
    banda("elec", "⚡ ELECTRICIDAD · REBT", "En el presupuesto" if s.inc_elec else "No incluida")
    e1, e2 = st.columns(2)
    with e1:
        st.checkbox("Calefacción eléctrica (C8)", key="calefaccion_elec")
        st.checkbox("Aire acondicionado (C9)", key="aire_acond")
        st.checkbox("Secadora (C10)", key="secadora")
        st.checkbox("Protector contra sobretensiones en el cuadro", key="incluir_spd")
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
    if not s.incluir_spd:
        st.info("El borrador del nuevo REBT (sin publicar a " + NORMATIVA_FECHA + ") haría "
                "obligatoria la protección contra sobretensiones; hoy depende de la instalación "
                "(ITC-BT-23).")
    d1, d2, d3 = st.columns(3)
    d1.number_input("Longitud de la derivación individual (m)", min_value=1.0, step=1.0, key="longitud_di")
    d2.selectbox("Aislamiento del cable", list(CONDUCTIVIDAD_CU), key="aislamiento")
    d3.selectbox("Suministro (límite de caída de tensión)", list(CAIDA_DI_PCT), key="suministro_di")
    st.caption("En una reforma la derivación individual suele estar ya instalada: usa este cálculo "
               "para comprobar si la existente es suficiente.")
    limite_caida = CAIDA_DI_PCT[s.suministro_di]
    try:
        di = derivacion_individual(s.potencia_prevista, s.longitud_di, s.aislamiento,
                                   caida_max_pct=limite_caida)
        k1, k2, k3 = st.columns(3)
        with k1:
            kpi("elec", "Intensidad", f"{di['intensidad_a']:.1f} A")
        with k2:
            kpi("elec", "Sección derivación (Cu)", f"{di['seccion_mm2']:g} mm²",
                f"Caída {di['s_caida']:.2f} · intensidad {di['s_int']:g} · mínimo 6")
        with k3:
            limite_txt = f"{limite_caida:g}".replace(".", ",")
            kpi("elec", "Caída de tensión", f"{di['caida_pct']:.2f} %",
                f"Límite {limite_txt} % {'✔' if di['cumple'] else '✘'}")
    except ValueError as err:
        st.error(str(err))

    estancias = {"vestibulos": s.n_vestibulos, "dormitorios": s.n_dormitorios,
                 "salones": s.n_salones, "banos": s.n_banos, "aseos": s.n_aseos,
                 "cocinas": s.n_cocinas, "galerias": s.n_galerias,
                 "terrazas": s.n_terrazas, "trasteros": s.n_trasteros}
    filas_circ, mec = circuitos(
        estancias, s.pasillo_m, {"C8": s.calefaccion_elec, "C9": s.aire_acond, "C10": s.secadora},
        sup_salon_m2=s.sup_salon_m2, superficie_m2=s.superficie, grado=s.grado)
    st.markdown("**Circuitos y puntos mínimos** (ITC-BT-25, simplificado)")
    if filas_circ:
        tabla(pd.DataFrame(filas_circ))
        st.caption(f"Puntos de luz: {mec['puntos_luz']} · tomas C2: {mec['tomas_c2']} · "
                   f"tomas C5: {mec['tomas_c5']}. Si indicas la superficie del salón, sus mínimos "
                   "se ajustan; en pasillos se calculan por longitud. Revisa el resto con la tabla 2 "
                   "de la ITC-BT-25.")
        if mec["c7_por_superficie"]:
            st.caption("Con electrificación elevada y más de 160 m² se prevé un circuito C2 "
                       "adicional (C7).")
        st.markdown("**Protecciones del cuadro** (orientativo)")
        n_circuitos_total = sum(f["Nº circuitos"] for f in filas_circ)
        tabla(pd.DataFrame(protecciones(s.potencia_prevista, n_circuitos_total, s.incluir_spd)))
        st.caption("Confirma calibres y número de diferenciales con la ITC-BT-25 y el esquema "
                   "real del cuadro.")
    else:
        st.info("Añade estancias en el Paso 1 para ver los circuitos.")

    # FONTANERÍA
    banda("hidro", "💧 FONTANERÍA · CTE DB-HS4", "En el presupuesto" if s.inc_font else "No incluida")
    st.number_input("Velocidad de cálculo del agua (m/s)", min_value=0.5, max_value=2.0, step=0.1,
                    key="velocidad_ms")
    h = hidraulica(s.n_banos, s.n_aseos, s.n_cocinas, s.n_galerias, s.velocidad_ms)
    if h["n_aparatos"]:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("hidro", "Aparatos", h["n_aparatos"])
        with k2:
            kpi("hidro", "Caudal instalado", f"{h['q_fria']:.2f} L/s", "Agua fría")
        with k3:
            kpi("hidro", "Caudal de diseño", f"{h['q_diseno']:.2f} L/s", f"Simultaneidad {h['kn']:.2f}")
        with k4:
            kpi("hidro", "Ø interior mínimo", f"{h['diametro_mm']:.1f} mm", "Tubería general")
        st.caption("Caudales por aparato según tabla 2.1 del DB-HS4. Falta dimensionar los ramales y "
                   "comprobar presión (mín. 100 kPa en grifos, 150 kPa en fluxores y calentadores; "
                   "máx. 500 kPa).")
    else:
        st.info("Añade baños, aseos o cocinas en el Paso 1.")

    # CLIMATIZACIÓN
    banda("clima", "❄️ CLIMATIZACIÓN · estimación", "En el presupuesto" if s.inc_clima else "No incluida")
    if s.superficie > 0:
        st.selectbox("Aislamiento térmico del inmueble", list(RATIOS_W_M2), key="aislamiento_termico")
        cl = climatizacion(s.superficie, calc_w_m2(s))
        k1, k2, _ = st.columns(3)
        with k1:
            kpi("clima", "Potencia térmica", f"{cl['kw']:.2f} kW")
        with k2:
            kpi("clima", "Equivalente", f"{cl['kcal_h']:.0f} kcal/h")
        st.caption("Estimación por ratio: no es un cálculo de cargas según RITE.")
    else:
        st.info("Introduce la superficie en la barra lateral.")
    st.caption("👉 Siguiente: pestaña **3. Tarifas**")

# --- PASO 3: TARIFAS ---
with t3:
    st.markdown("#### Pon tus precios (sin IVA). Todos parten de 0 €")
    a, b = st.columns(2)
    with a:
        banda("elec", "⚡ ELECTRICIDAD")
        st.number_input("Instalación eléctrica general (€/m²)", min_value=0.0, step=5.0, key="pu_elec_m2")
        st.number_input("Cuadro general y protecciones (€/ud)", min_value=0.0, step=25.0, key="pu_elec_cgmp")
        st.number_input("Protector contra sobretensiones (€/ud)", min_value=0.0, step=10.0, key="pu_elec_spd")
        banda("hidro", "💧 FONTANERÍA")
        st.number_input("Baño completo (€/ud)", min_value=0.0, step=50.0, key="pu_font_bano")
        st.number_input("Aseo (€/ud)", min_value=0.0, step=50.0, key="pu_font_aseo")
        st.number_input("Cocina (€/ud)", min_value=0.0, step=50.0, key="pu_font_cocina")
    with b:
        banda("clima", "❄️ CLIMATIZACIÓN")
        st.number_input("Instalación (€/kW)", min_value=0.0, step=25.0, key="pu_clima_kw")
        banda("teleco", "📡 TELECOMUNICACIONES")
        st.number_input("Toma de datos RJ45 Cat6 (€/toma)", min_value=0.0, step=5.0, key="pu_teleco_toma")
        banda("alba", "🏗️ ALBAÑILERÍA")
        st.number_input("Rozas, ayudas y remates (€/m²)", min_value=0.0, step=5.0, key="pu_albanil_m2")
    st.caption("👉 Siguiente: pestaña **4. Presupuesto**")

# --- PASO 4: PRESUPUESTO ---
with t4:
    if not filas:
        st.info("Marca al menos una especialidad en la barra lateral.")
    else:
        if not hay_precios:
            st.warning("Aún no has puesto precios. Ve a la pestaña **3. Tarifas**.")
        if s.superficie <= 0 and n_estancias == 0:
            st.warning("Faltan la superficie y las estancias. Empieza en la pestaña **1. Estancias**.")
        tabla(pd.DataFrame(filas), {"Cantidad": lambda v: f"{v:,.2f}",
                                    "Precio unit. (€)": lambda v: f"{v:,.2f} €",
                                    "Importe (€)": lambda v: f"{v:,.2f} €"})
        base, iva, total_pres = totales(filas, s.tipo_iva)
        r1, r2, r3 = st.columns(3)
        with r1:
            kpi("marino", "Base imponible", f"{base:,.2f} €")
        with r2:
            kpi("hidro", f"IVA ({s.tipo_iva} %)", f"{iva:,.2f} €")
        with r3:
            kpi("elec", "TOTAL", f"{total_pres:,.2f} €", extra="total")
        nombre = re.sub(r"[^\w\-]+", "_", s.cliente_nombre.strip()) or "Reforma"
        if HAY_OPENPYXL:
            st.download_button(
                "🟢 Descargar presupuesto en Excel (.xlsx)",
                data=presupuesto_excel(filas, s.cliente_nombre, s.cliente_obra, s.superficie, s.tipo_iva),
                file_name=f"Presupuesto_{nombre}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("Para descargar el Excel, añade la línea 'openpyxl' al archivo requirements.txt.")

# --- BIBLIOTECA ---
with t5:
    n1, n2, n3, n4 = st.tabs(["⚡ REBT", "💧 CTE DB-HS", "❄️ RITE", "📡 Telecomunicaciones"])
    with n1:
        st.markdown("- **ITC-BT-25:** circuitos C1 (iluminación), C2 (tomas generales), C3 (cocina y "
                    "horno), C4 (lavadora, lavavajillas, termo), C5 (baños y auxiliares de cocina); "
                    "en electrificación elevada, C8 a C12, y un C2 adicional (C7) con más de 160 m².\n"
                    "- **ITC-BT-15:** derivación individual de 6 mm² como mínimo.\n"
                    "- **Caída de tensión en la derivación individual (ITC-BT-15):** 0,5 % con "
                    "contadores en más de un lugar, 1 % con contadores totalmente concentrados y "
                    "1,5 % para un único usuario sin línea general de alimentación. En la "
                    "instalación interior de viviendas, 3 % (ITC-BT-19).\n"
                    f"- **Estado a {NORMATIVA_FECHA}:** vigente el RD 842/2002. La revisión del "
                    "REBT (diferenciales tipo AC, sobretensiones, ITC-BT-53) no estaba publicada "
                    "en el BOE.")
    with n2:
        st.markdown("- **DB-HS4, tabla 2.1:** lavabo 0,10 · ducha 0,20 · fregadero 0,20 · "
                    "lavavajillas 0,15 · lavadora 0,20 · inodoro con cisterna 0,10 (L/s, agua fría).\n"
                    "- **Presión:** mínimo 100 kPa en grifos y 150 kPa en fluxores y calentadores; "
                    "máximo 500 kPa.\n- **DB-HS5:** evacuación de aguas.")
    with n3:
        st.markdown("- **RITE (RD 1027/2007):** regulación por termostato, eficiencia energética y "
                    "mantenimiento de instalaciones térmicas.\n"
                    f"- **Estado a {NORMATIVA_FECHA}:** modificaciones del RITE y del CTE anunciadas; "
                    "comprueba el BOE antes de cada proyecto.")
    with n4:
        st.markdown("- **Reglamento ICT (RD 346/2011):** infraestructuras comunes de telecomunicaciones. "
                    "La red interior de datos (Cat6) se presupuesta por tomas.")
