"""Visor Streamlit 
Instalación y uso:
    pip install streamlit
    streamlit run src/app_streamlit.py

"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

import streamlit as st

try:
    from src.scanner import Lexer
except ImportError:
    from scanner import Lexer


def listar_pl():
    base = os.path.join(ROOT, "tests")
    sal = []
    for sub in ("validos", "invalidos", "completos"):
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".pl"):
                    sal.append(os.path.join(sub, f))
    return sal


st.set_page_config(page_title="Lexer Prolog — Streamlit", layout="wide")
st.title("Analizador Léxico Prolog — visor Streamlit")

con_archivo = st.sidebar.header("Entrada")
archivos = listar_pl()
sel = st.sidebar.selectbox("Corpus del repo", ["(editar texto)"] + archivos)
up = st.sidebar.file_uploader("…o sube un .pl", type=["pl", "txt"])

if "src_txt" not in st.session_state:
    st.session_state.src_txt = "% Hechos\npadre(juan, ana).\n?- abuelo(juan, Quien).\n"
if "last_sel" not in st.session_state:
    st.session_state.last_sel = "(editar texto)"
if "last_up" not in st.session_state:
    st.session_state.last_up = None

if up is not None:
    nombre = up.name
    if st.session_state.last_up != up.name:
        st.session_state.src_txt = up.read().decode("utf-8", errors="replace")
        st.session_state.last_up = up.name
elif sel != "(editar texto)":
    nombre = sel
    if st.session_state.last_sel != sel:
        with open(os.path.join(ROOT, "tests", sel), encoding="utf-8") as f:
            st.session_state.src_txt = f.read()
        st.session_state.last_sel = sel
        st.session_state.last_up = None
else:
    nombre = "(texto editado)"
    st.session_state.last_sel = sel
    st.session_state.last_up = None

texto = st.text_area("Fuente Prolog", height=220, key="src_txt")
st.button("Analizar", type="primary")

if True:  
    lx = Lexer(st.session_state.src_txt)
    toks, errs, tab = lx.lex()
    d = tab.dump()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tokens", len(toks))
    c2.metric("Errores", len(errs))
    c3.metric("Átomos", len(d["atomos"]))
    c4.metric("Variables", len(d["variables"]))
    c5.metric("Literales", len(d["literales"]))
    st.caption(f"{nombre}: {'OK sin errores' if not errs else f'{len(errs)} error(es), sigue emitiendo tokens (recuperación)'}")

    col_t, col_e = st.columns([3, 2])
    with col_t:
        st.subheader("Tokens  <TIPO, 'lexema', línea, col>")
        st.dataframe(
            [{"tipo": t.tipo, "lexema": t.lexema, "línea": t.linea,
              "col": t.col, "attr": "—" if t.attr is None else str(t.attr)}
             for t in toks],
            width="stretch", height=420,
        )
    with col_e:
        st.subheader("Errores léxicos")
        if errs:
            for e in errs:
                st.error(str(e))
        else:
            st.success("Sin errores léxicos.")
        st.subheader("Tabla de lexemas")
        t1, t2, t3 = st.tabs(["atomos", "variables", "literales"])
        with t1:
            st.table([{"idx": i, "lexema": x} for i, x in enumerate(d["atomos"])])
        with t2:
            st.table([{"idx": i, "lexema": x} for i, x in enumerate(d["variables"])])
        with t3:
            st.table([{"idx": i, "lexema": x} for i, x in enumerate(d["literales"])])
