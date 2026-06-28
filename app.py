import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modele import nettoyer_note
from utils.hebdo import afficher_hebdo
from utils.mercato import afficher_mercato
from utils.adversaire import afficher_adversaire

st.set_page_config(
    page_title="Maestro Tactico",
    page_icon="⚽",
    layout="wide"
)

# ============================================================
# CSS GLOBAL — IDENTITÉ VISUELLE MAESTRO TACTICO
# ============================================================

st.markdown("""
<style>
/* ── Tokens ─────────────────────────────────────────────── */
:root {
    --bg-main:    #0d0d0d;
    --bg-card:    #1a1a1a;
    --gold:       #c8a84b;
    --gold-dark:  #8a6f2e;
    --white:      #ffffff;
    --grey-mid:   #555555;
    --grey-dim:   #444444;
    --radius:     8px;
}

/* ── Fond global ─────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg-main) !important;
    color: var(--white) !important;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* Bloc principal */
[data-testid="stMain"],
[data-testid="block-container"] {
    background-color: var(--bg-main) !important;
}

/* ── Topbar cachée (on la remplace par la nôtre) ─────────── */
header[data-testid="stHeader"] {
    background-color: var(--bg-main) !important;
    border-bottom: 1px solid var(--gold-dark);
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 1px solid #2a2a2a;
}
[data-testid="stSidebar"] * {
    color: var(--white) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 1.2rem;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: var(--bg-card) !important;
    border: 1px dashed var(--gold-dark) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stSidebar"] textarea {
    background-color: var(--bg-card) !important;
    color: var(--white) !important;
    border: 1px solid #2a2a2a !important;
    border-radius: var(--radius) !important;
}
[data-testid="stSidebar"] hr {
    border-color: #2a2a2a !important;
    margin: 1rem 0;
}

/* Checkbox sidebar */
[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
    color: var(--grey-mid) !important;
}
[data-testid="stSidebar"] [data-testid="stCheckbox"] input:checked + span {
    color: var(--gold) !important;
}

/* ── Boutons ─────────────────────────────────────────────── */
button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, var(--gold), var(--gold-dark)) !important;
    color: var(--bg-main) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em;
    transition: opacity 0.2s;
}
.stButton > button:hover {
    opacity: 0.85 !important;
}

/* ── Onglets de navigation ───────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #2a2a2a;
    gap: 0.5rem;
}
[data-testid="stTabs"] [role="tab"] {
    color: var(--grey-mid) !important;
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 4px 4px 0 0;
    transition: color 0.2s;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: var(--white) !important;
}

/* ── Cartes / conteneurs ─────────────────────────────────── */
[data-testid="stExpander"],
div.element-container > div[class*="stMetric"],
[data-testid="metric-container"] {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    border: 1px solid #2a2a2a;
}

/* Filet gauche or sur les métriques (style carte joueur) */
[data-testid="metric-container"] {
    border-left: 3px solid var(--gold) !important;
    padding-left: 0.75rem;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--grey-mid) !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Tableaux ────────────────────────────────────────────── */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    border: 1px solid #2a2a2a !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] th {
    background-color: #111111 !important;
    color: var(--gold) !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stDataFrame"] td {
    color: var(--white) !important;
    border-color: #2a2a2a !important;
}

/* ── Inputs & selects ────────────────────────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div,
[data-testid="stTextInput"] > div {
    background-color: var(--bg-card) !important;
    border-color: #2a2a2a !important;
    color: var(--white) !important;
    border-radius: var(--radius) !important;
}

/* ── Messages système ────────────────────────────────────── */
[data-testid="stAlert"][data-baseweb="notification"] {
    background-color: var(--bg-card) !important;
    border-left: 3px solid var(--gold) !important;
    color: var(--white) !important;
    border-radius: var(--radius) !important;
}

/* Séparateurs */
hr {
    border-color: #2a2a2a !important;
}

/* ── Texte global ────────────────────────────────────────── */
h1, h2, h3, h4 {
    color: var(--white) !important;
}
p, li, label {
    color: var(--white) !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dark); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# TOPBAR — LOGO MAESTRO TACTICO
# ============================================================

st.markdown("""
<div style="
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 0 14px 0;
    border-bottom: 1px solid #c8a84b33;
    margin-bottom: 24px;
">
    <!-- Icône ballon dans cercle doré -->
    <div style="
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 2px solid #c8a84b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
        background: #1a1a1a;
        box-shadow: 0 0 12px #c8a84b33;
    ">⚽</div>
    <!-- Texte logo -->
    <div>
        <div style="
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            color: #ffffff;
            line-height: 1.1;
            text-transform: uppercase;
        ">MAESTRO TACTICO</div>
        <div style="
            font-size: 0.72rem;
            color: #c8a84b;
            letter-spacing: 0.06em;
            margin-top: 2px;
        ">L'app qui fait gagner</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style="
        text-align: center;
        padding: 16px 0 8px 0;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 8px;
    ">
        <span style="font-size: 28px;">⚽</span><br>
        <span style="
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: #c8a84b;
            text-transform: uppercase;
        ">MAESTRO TACTICO</span>
    </div>
    """, unsafe_allow_html=True)

    st.header("📁 Importer vos données")
    fichier = st.file_uploader(
        "Téléchargez le fichier MPGStats (xlsx)",
        type=['xlsx']
    )
    st.markdown("---")
    st.header("📋 Mes joueurs")
    mes_joueurs_input = st.text_area(
        "Entrez vos joueurs (un par ligne)",
        placeholder="Greenwood\nBarcola\nTolisso",
        height=150
    )
    filtrer = st.checkbox("Afficher uniquement mes joueurs", value=False)

if fichier is None:
    st.info("👈 Commencez par importer votre fichier MPGStats dans le panneau gauche")
    st.stop()

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def charger_donnees(fichier):
    df = pd.read_excel(fichier)
    return df

df = charger_donnees(fichier)
st.success(f"✅ {len(df)} joueurs chargés !")

# Colonnes journées
cols_journees = [col for col in df.columns if str(col).startswith('D') and str(col)[1:].isdigit()]
cols_journees = sorted(cols_journees, key=lambda x: int(x[1:]), reverse=True)

# Nettoyage des notes
for col in cols_journees:
    df[col] = df[col].apply(nettoyer_note)

# ============================================================
# NAVIGATION
# ============================================================

page1, page2, page3 = st.tabs([
    "🏆 Conseiller hebdo",
    "🛒 Mercato",
    "⚔️ Analyser mon adversaire"
])

with page1:
    afficher_hebdo(df, cols_journees, mes_joueurs_input, filtrer)

with page2:
    afficher_mercato(df, cols_journees)

with page3:
    afficher_adversaire(df, cols_journees)
