import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modele import nettoyer_note
from pages.hebdo import afficher_hebdo
from pages.mercato import afficher_mercato
from pages.adversaire import afficher_adversaire

# ============================================================
# FAVICON SVG — cercle or plein #c8a84b avec MT en #141414
# ============================================================

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="50" fill="#c8a84b"/>
  <text x="50" y="67" font-family="Arial Black, sans-serif" font-size="38" font-weight="900"
        fill="#141414" text-anchor="middle" letter-spacing="2">MT</text>
</svg>"""

favicon_b64 = base64.b64encode(FAVICON_SVG.encode()).decode()
favicon_uri = f"data:image/svg+xml;base64,{favicon_b64}"

st.set_page_config(
    page_title="Maestro Tactico",
    page_icon=favicon_uri,
    layout="wide"
)

# ============================================================
# LOGO HTML — cercle #141414 / contour #c8a84b
# ============================================================

LOGO_CIRCLE_HTML = """
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap" rel="stylesheet">
<div style="
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: #141414;
    border: 3px solid #c8a84b;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
">
    <div style="
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 22px;
        color: #c8a84b;
        letter-spacing: 2px;
        text-indent: 2px;
        line-height: 1;
        margin-bottom: 2px;
    ">MT</div>
    <div style="
        width: 80%;
        height: 1px;
        background: #c8a84b;
        opacity: 0.55;
        margin: 4px auto;
    "></div>
    <div style="
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 8px;
        color: #c8a84b;
        letter-spacing: 4px;
        text-indent: 4px;
        opacity: 0.85;
        line-height: 1;
    ">TACTICO</div>
</div>
"""

# ============================================================
# TOPBAR — logo à gauche + titre à droite du cercle
# ============================================================

TOPBAR_HTML = f"""
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap" rel="stylesheet">
<div style="
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 10px 0 18px 0;
    border-bottom: 1px solid #c8a84b22;
    margin-bottom: 8px;
">
    <!-- Cercle logo -->
    <div style="
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: #141414;
        border: 3px solid #c8a84b;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    ">
        <div style="
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 22px;
            color: #c8a84b;
            letter-spacing: 2px;
            text-indent: 2px;
            line-height: 1;
            margin-bottom: 2px;
        ">MT</div>
        <div style="
            width: 80%;
            height: 1px;
            background: #c8a84b;
            opacity: 0.55;
            margin: 4px auto;
        "></div>
        <div style="
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 8px;
            color: #c8a84b;
            letter-spacing: 4px;
            text-indent: 4px;
            opacity: 0.85;
            line-height: 1;
        ">TACTICO</div>
    </div>
    <!-- Texte à droite -->
    <div style="display: flex; flex-direction: column; gap: 4px;">
        <div style="
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 26px;
            color: #ffffff;
            letter-spacing: 3px;
            text-transform: uppercase;
            line-height: 1;
        ">MAESTRO TACTICO</div>
        <div style="
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 14px;
            color: #c8a84b;
            letter-spacing: 2px;
            opacity: 0.90;
        ">L'app qui fait gagner</div>
    </div>
</div>
"""

# ============================================================
# SIDEBAR LOGO — centré en haut
# ============================================================

SIDEBAR_LOGO_HTML = f"""
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap" rel="stylesheet">
<div style="display: flex; flex-direction: column; align-items: center; padding: 16px 0 20px 0;">
    <div style="
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: #141414;
        border: 3px solid #c8a84b;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    ">
        <div style="
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 24px;
            color: #c8a84b;
            letter-spacing: 2px;
            text-indent: 2px;
            line-height: 1;
            margin-bottom: 2px;
        ">MT</div>
        <div style="
            width: 80%;
            height: 1px;
            background: #c8a84b;
            opacity: 0.55;
            margin: 5px auto;
        "></div>
        <div style="
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 9px;
            color: #c8a84b;
            letter-spacing: 4px;
            text-indent: 4px;
            opacity: 0.85;
            line-height: 1;
        ">TACTICO</div>
    </div>
    <div style="
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 13px;
        color: #c8a84b;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 10px;
        opacity: 0.85;
    ">MAESTRO TACTICO</div>
</div>
<hr style="border: none; border-top: 1px solid #c8a84b33; margin: 0 0 12px 0;">
"""

# ============================================================
# AFFICHAGE TOPBAR
# ============================================================

st.markdown(TOPBAR_HTML, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(SIDEBAR_LOGO_HTML, unsafe_allow_html=True)

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
