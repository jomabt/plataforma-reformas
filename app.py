import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import calculos as c


def test_di_basica_15m():
    r = c.derivacion_individual(5750, 15)
    assert r["seccion_mm2"] == 6
    assert r["caida_pct"] <= 1.5


def test_di_larga_sube_seccion():
    r = c.derivacion_individual(9200, 40)
    assert r["seccion_mm2"] >= 25
    assert r["caida_pct"] <= 1.5


def test_di_valores_invalidos():
    try:
        c.derivacion_individual(0, 10)
        assert False
    except ValueError:
        pass


def test_hidraulica_un_bano_una_cocina():
    h = c.hidraulica(1, 0, 1, 0)
    assert h["n_aparatos"] == 6
    assert math.isclose(h["q_fria"], 0.95)
    assert math.isclose(h["q_diseno"], 0.95 / math.sqrt(5))


def test_circuitos_vivienda_tipo():
    filas, mec = c.circuitos({"dormitorios": 2, "salones": 1, "banos": 1, "aseos": 0,
                              "cocinas": 1, "galerias": 0, "terrazas": 0, "trasteros": 0})
    codigos = {f["Circuito"] for f in filas}
    assert {"C1", "C2", "C3", "C4", "C5"} <= codigos
    assert mec["puntos_luz"] == 5


def test_grado_recomendado():
    assert c.grado_recomendado(170, False, False) == "Elevada"
    assert c.grado_recomendado(90, True, False) == "Elevada"
    assert c.grado_recomendado(90, False, False) == "Básica"


def test_presupuesto_y_totales():
    d = {"superficie": 80, "inc_elec": True, "inc_font": True, "inc_clima": False,
         "inc_teleco": False, "inc_albanil": False, "pu_elec_m2": 10, "pu_elec_cgmp": 100,
         "n_banos": 1, "n_aseos": 1, "n_cocinas": 1, "pu_font_bano": 500, "pu_font_aseo": 200,
         "pu_font_cocina": 300}
    filas = c.partidas(d)
    base, iva, total = c.totales(filas, 10)
    assert base == 80 * 10 + 100 + 500 + 200 + 300
    assert math.isclose(total, base * 1.10)
