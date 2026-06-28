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
    page_title="Gazon Stats",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Gazon Stats — Conseiller MPG")
st.markdown("---")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
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
