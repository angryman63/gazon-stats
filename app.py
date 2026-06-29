import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modele import nettoyer_note
from pages.hebdo import afficher_hebdo
from pages.mercato import afficher_mercato
from pages.adversaire import afficher_adversaire

# ============================================================
# CONFIG PAGE
# ============================================================

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
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Inter:wght@400;500;600&display=swap');

/* Fond général */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #141414 !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] {
    background-color: #0d0d0d !important;
    border-right: 1px solid #c8a84b33;
}

/* Topbar */
[data-testid="stHeader"] {
    background-color: #0d0d0d !important;
    border-bottom: 1px solid #c8a84b44;
}

/* Onglets */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1a1a1a;
    border-radius: 8px;
    gap: 4px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #888888;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background-color: #c8a84b22;
    color: #c8a84b !important;
    border-bottom: 2px solid #c8a84b;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    background-color: #1a1a1a !important;
    border: 1px solid #333333 !important;
    border-radius: 8px;
}

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #c8a84b, #8a6f2e);
    color: #141414;
    font-weight: 700;
    border: none;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #d4b55c, #9a7f3e);
    color: #141414;
}

/* Métriques */
[data-testid="stMetricValue"] {
    color: #c8a84b !important;
    font-family: 'Oswald', sans-serif;
}

/* Selectbox / inputs */
[data-testid="stSelectbox"] > div,
[data-testid="stTextInput"] > div > div {
    background-color: #1a1a1a !important;
    border: 1px solid #333333 !important;
    color: #ffffff !important;
    border-radius: 6px;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 8px;
}

/* Dividers */
hr {
    border-color: #c8a84b44 !important;
}

/* ============================================================
   PAGE D'ACCUEIL
   ============================================================ */

.hero-section {
    text-align: center;
    padding: 48px 24px 32px 24px;
    max-width: 860px;
    margin: 0 auto;
}

.hero-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 3px solid #c8a84b;
    background-color: #141414;
    margin-bottom: 24px;
    flex-direction: column;
    gap: 0px;
}

.hero-logo-mt {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 28px;
    color: #c8a84b;
    letter-spacing: 2px;
    line-height: 1;
}

.hero-logo-sep {
    width: 64px;
    height: 1px;
    background-color: #c8a84b;
    opacity: 0.55;
    margin: 6px auto;
}

.hero-logo-tactico {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 10px;
    color: #c8a84b;
    letter-spacing: 4px;
    opacity: 0.85;
    line-height: 1;
}

.hero-title {
    font-family: 'Oswald', sans-serif;
    font-size: 42px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
    margin: 0 0 8px 0;
}

.hero-title span {
    color: #c8a84b;
}

.hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 17px;
    color: #aaaaaa;
    line-height: 1.6;
    margin: 0 auto 40px auto;
    max-width: 580px;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    max-width: 860px;
    margin: 0 auto 40px auto;
    padding: 0 8px;
}

.feature-card {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: left;
    transition: border-color 0.2s ease;
}

.feature-card:hover {
    border-color: #c8a84b55;
}

.feature-emoji {
    font-size: 28px;
    margin-bottom: 10px;
    display: block;
}

.feature-name {
    font-family: 'Oswald', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #c8a84b;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.feature-badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 20px;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.badge-free {
    background-color: #1e3a1e;
    color: #4ade80;
    border: 1px solid #4ade8044;
}

.badge-premium {
    background-color: #3a2a1a;
    color: #c8a84b;
    border: 1px solid #c8a84b44;
}

.feature-desc {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #888888;
    line-height: 1.5;
    margin: 0;
}

.loading-box {
    background-color: #1a1a1a;
    border: 1px solid #c8a84b33;
    border-radius: 12px;
    padding: 20px 28px;
    max-width: 420px;
    margin: 0 auto;
    text-align: center;
}

.loading-title {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #c8a84b;
    margin-bottom: 8px;
}

.loading-sub {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: #555555;
}

/* Responsive */
@media (max-width: 700px) {
    .features-grid {
        grid-template-columns: 1fr;
    }
    .hero-title {
        font-size: 28px;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# TOPBAR / SIDEBAR LOGO
# ============================================================

LOGO_HTML = """
<div style="display:flex; align-items:center; gap:14px; padding:8px 4px;">
  <div style="
      width:48px; height:48px; border-radius:50%;
      border:2px solid #c8a84b;
      background:#141414;
      display:flex; flex-direction:column;
      align-items:center; justify-content:center;
      flex-shrink:0;">
    <span style="font-family:'Oswald',sans-serif; font-weight:700; font-size:13px; color:#c8a84b; letter-spacing:2px;">MT</span>
    <div style="width:28px; height:1px; background:#c8a84b; opacity:0.55; margin:3px 0;"></div>
    <span style="font-family:'Oswald',sans-serif; font-weight:700; font-size:5px; color:#c8a84b; letter-spacing:3px; opacity:0.85;">TACTICO</span>
  </div>
  <div>
    <div style="font-family:'Oswald',sans-serif; font-weight:700; font-size:16px; color:#ffffff; letter-spacing:1px;">MAESTRO TACTICO</div>
    <div style="font-family:'Inter',sans-serif; font-size:11px; color:#c8a84b; margin-top:1px;">L'app qui fait gagner</div>
  </div>
</div>
"""

with st.sidebar:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.markdown("---")

# ============================================================
# URL GITHUB — BASE JOUEURS
# ============================================================

GITHUB_URL = "https://raw.githubusercontent.com/angryman63/gazon-stats/main/L1Joueurs25-26.xlsx"

# ============================================================
# CHARGEMENT AUTOMATIQUE DEPUIS GITHUB
# ============================================================

@st.cache_data(show_spinner=False, ttl=3600)
def charger_depuis_github(url: str):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    df = pd.read_excel(io.BytesIO(response.content))
    return df

# ============================================================
# PAGE D'ACCUEIL — affichée pendant le chargement
# ============================================================

def afficher_accueil(chargement_en_cours: bool = False):
    st.markdown("""
    <div class="hero-section">

      <!-- Logo -->
      <div class="hero-logo">
        <div class="hero-logo-mt">MT</div>
        <div class="hero-logo-sep"></div>
        <div class="hero-logo-tactico">TACTICO</div>
      </div>

      <!-- Titre -->
      <h1 class="hero-title">Devenez le meilleur manager<br><span>de votre ligue</span></h1>

      <!-- Sous-titre -->
      <p class="hero-subtitle">
        Vos rivaux font des choix au feeling. Vous, vous avez Maestro Tactico.<br>
        Chaque journée, chaque mercato, chaque match — prenez les décisions qui font la différence.
      </p>

      <!-- Fonctionnalités -->
      <div class="features-grid">

        <div class="feature-card">
          <span class="feature-emoji">🏆</span>
          <div class="feature-name">Conseiller Hebdo</div>
          <span class="feature-badge badge-free">Gratuit</span>
          <p class="feature-desc">Qui titulariser cette semaine ? Score de fiabilité, régularité, alertes — votre compo du dimanche ne sera plus jamais hasardeuse.</p>
        </div>

        <div class="feature-card">
          <span class="feature-emoji">🛒</span>
          <div class="feature-name">Conseiller Mercato</div>
          <span class="feature-badge badge-premium">Premium</span>
          <p class="feature-desc">Stars, valeurs sûres, pépites planquées : trouvez les joueurs qui feront exploser votre budget dans le bon sens.</p>
        </div>

        <div class="feature-card">
          <span class="feature-emoji">⚔️</span>
          <div class="feature-name">Analyser l'Adversaire</div>
          <span class="feature-badge badge-premium">Premium</span>
          <p class="feature-desc">% de victoire, stratégie optimale, choix du capitaine — affrontez votre prochain adversaire avec les cartes en main.</p>
        </div>

      </div>

    </div>
    """, unsafe_allow_html=True)

    # Bloc chargement
    if chargement_en_cours:
        st.markdown("""
        <div class="loading-box">
          <div class="loading-title">⚡ Chargement de la base joueurs…</div>
          <div class="loading-sub">Connexion aux données en cours — ça prend quelques secondes</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="loading-box">
          <div class="loading-title">🔄 Mise à jour de la base joueurs…</div>
          <div class="loading-sub">Récupération des dernières statistiques</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# LOGIQUE PRINCIPALE
# ============================================================

# Placeholder pour afficher la page d'accueil pendant le chargement
placeholder = st.empty()

# Vérifier si les données sont déjà en cache (première fois = False)
donnees_chargees = "df_joueurs" in st.session_state

if not donnees_chargees:
    # Afficher la page d'accueil avec indicateur de chargement
    with placeholder.container():
        afficher_accueil(chargement_en_cours=True)
        barre = st.progress(0, text="Connexion à la base joueurs…")
        for i in range(0, 60, 5):
            time.sleep(0.08)
            barre.progress(i, text="Connexion à la base joueurs…")

    try:
        df_raw = charger_depuis_github(GITHUB_URL)
        st.session_state["df_joueurs"] = df_raw
    except Exception as e:
        placeholder.empty()
        st.error(f"⚠️ Impossible de charger la base joueurs depuis GitHub. Vérifiez votre connexion ou contactez le support.")
        st.stop()

    placeholder.empty()

# Charger depuis session_state
df = st.session_state["df_joueurs"]

# ============================================================
# TRAITEMENT DES DONNÉES
# ============================================================

cols_journees = [col for col in df.columns if str(col).startswith('D') and str(col)[1:].isdigit()]
cols_journees = sorted(cols_journees, key=lambda x: int(x[1:]), reverse=True)

for col in cols_journees:
    df[col] = df[col].apply(nettoyer_note)

# ============================================================
# SIDEBAR — MES JOUEURS
# ============================================================

with st.sidebar:
    st.markdown("### 📋 Mes joueurs")
    mes_joueurs_input = st.text_area(
        "Entrez vos joueurs (un par ligne)",
        placeholder="Greenwood\nBarcola\nTolisso",
        height=150
    )
    filtrer = st.checkbox("Afficher uniquement mes joueurs", value=False)
    st.markdown("---")
    st.markdown(
        "<div style='font-family:Inter,sans-serif; font-size:11px; color:#444444; text-align:center;'>"
        "maestrotactico.fr<br>contact@maestrotactico.fr"
        "</div>",
        unsafe_allow_html=True
    )

# ============================================================
# NAVIGATION — ONGLETS
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
