import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Gazon Stats",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Gazon Stats — Conseiller MPG")
st.markdown("---")

# Upload du fichier
st.sidebar.header("📁 Importer vos données")
fichier = st.sidebar.file_uploader(
    "Téléchargez le fichier MPGStats (xlsx)",
    type=['xlsx']
)

if fichier is None:
    st.info("👈 Commencez par importer votre fichier MPGStats dans le panneau gauche")
    st.stop()

# Chargement des données
@st.cache_data
def charger_donnees(fichier):
    df = pd.read_excel(fichier)
    return df

df = charger_donnees(fichier)
st.success(f"✅ {len(df)} joueurs chargés !")
