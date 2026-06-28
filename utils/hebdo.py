import streamlit as st
import pandas as pd
import numpy as np
from modele import nettoyer_note, calculer_clutch, predire_note, alerte_blessure, etiquette_regularite, absences_consecutives

# ─── Identité visuelle Maestro Tactico ───────────────────────────────────────
MT_CSS = """
<style>
/* ── Palette ── */
:root {
    --mt-bg:        #0d0d0d;
    --mt-card:      #1a1a1a;
    --mt-or:        #c8a84b;
    --mt-or-fonce:  #8a6f2e;
    --mt-blanc:     #ffffff;
    --mt-gris:      #555555;
}

/* ── Base ── */
[data-testid="stAppViewContainer"] {
    background-color: var(--mt-bg) !important;
}
[data-testid="stHeader"] {
    background-color: #0d0d0d !important;
}
section[data-testid="stSidebar"] {
    background-color: #141414 !important;
}

/* ── Header h1/h2/h3 ── */
h1, h2, h3 {
    color: var(--mt-blanc) !important;
    letter-spacing: 0.05em;
}

/* ── Section separator  (filet fin + titre or centré) ── */
hr {
    border: none;
    border-top: 1px solid var(--mt-or) !important;
    margin: 1.5rem 0;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #141414;
    border-bottom: 1px solid #2a2a2a;
    gap: 4px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: var(--mt-gris) !important;
    background-color: transparent !important;
    border-radius: 4px 4px 0 0;
    padding: 8px 16px;
    font-weight: 600;
    transition: color 0.2s;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--mt-or) !important;
    border-bottom: 2px solid var(--mt-or) !important;
    background-color: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--mt-or) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    border-left: 3px solid;
    border-image: linear-gradient(to bottom, var(--mt-or), var(--mt-or-fonce)) 1;
}
[data-testid="stDataFrame"] table {
    background-color: var(--mt-card) !important;
    color: var(--mt-blanc) !important;
}
[data-testid="stDataFrame"] thead tr th {
    background-color: #0d0d0d !important;
    color: var(--mt-or) !important;
    font-weight: 700;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--mt-or) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #222222 !important;
}

/* ── Warning / Info ── */
[data-testid="stWarning"], [data-testid="stInfo"] {
    background-color: var(--mt-card) !important;
    border-left: 3px solid var(--mt-or) !important;
    color: var(--mt-blanc) !important;
    border-radius: 0 6px 6px 0;
}

/* ── Expander (légende blessures) ── */
[data-testid="stExpander"] {
    background-color: var(--mt-card) !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    border-left: 3px solid var(--mt-or) !important;
}
[data-testid="stExpander"] summary {
    color: var(--mt-or) !important;
    font-weight: 600;
}

/* ── Table interne (légende) ── */
[data-testid="stExpander"] table {
    background-color: transparent !important;
    color: var(--mt-blanc) !important;
}
[data-testid="stExpander"] table thead th {
    color: var(--mt-or) !important;
    border-bottom: 1px solid var(--mt-or) !important;
}

/* ── Texte général ── */
p, li, span, label {
    color: var(--mt-blanc) !important;
}
</style>
"""

def afficher_hebdo(df, cols_journees, mes_joueurs_input, filtrer):

    # Injection CSS identité visuelle
    st.markdown(MT_CSS, unsafe_allow_html=True)

    scores = []
    for idx, row in df.iterrows():
        notes_jouees = [row[col] for col in cols_journees if row[col] > 0]
        if len(notes_jouees) >= 6:
            six_derniers = notes_jouees[:6]
            moyenne = np.mean(six_derniers)
            ecart_type = np.std(six_derniers)
            regularite_brute = 1 / (1 + ecart_type)
            prob_jouer = row['%Titu'] / 100 if '%Titu' in df.columns else 0.8
            moyenne_saison = float(row['Note']) if 'Note' in df.columns else moyenne
            score = (moyenne_saison * 0.5 + moyenne * 0.3 +
                     regularite_brute * 0.1 + prob_jouer * 0.1)
            scores.append({
                'Joueur': row['Joueur'],
                'Poste': row['Poste'],
                'Club': row['Club'],
                'Note saison': round(moyenne_saison, 2),
                'Forme 6J': round(float(moyenne), 2),
                '_regularite_brute': regularite_brute,
                '% Titulaire': f"{int(prob_jouer*100)}%",
                '_score': round(float(score), 2)
            })

    df_scores = pd.DataFrame(scores)

    for poste in df_scores['Poste'].unique():
        mask = df_scores['Poste'] == poste
        vals = df_scores.loc[mask, '_regularite_brute']
        q25, q50, q75 = vals.quantile([0.25, 0.5, 0.75])
        df_scores.loc[mask, 'Régularité'] = df_scores.loc[mask, '_regularite_brute'].apply(
            lambda x: etiquette_regularite(x, q25, q50, q75)
        )

    df_mes_joueurs = df_scores.copy()
    if filtrer and mes_joueurs_input.strip():
        mes_joueurs = [j.strip().lower() for j in mes_joueurs_input.split('\n') if j.strip()]
        df_mes_joueurs = df_scores[df_scores['Joueur'].str.lower().isin(mes_joueurs)]

    # ── Titre section avec séparateur or ─────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 1rem;">
        <div style="flex:1;height:1px;background:linear-gradient(to right,#c8a84b,transparent);"></div>
        <span style="color:#c8a84b;font-weight:700;letter-spacing:0.12em;font-size:0.85rem;white-space:nowrap;">
            🏆 RECOMMANDATIONS PAR POSTE
        </span>
        <div style="flex:1;height:1px;background:linear-gradient(to left,#c8a84b,transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🏥 Légende blessures"):
        st.markdown("""
| Emoji | Statut |
|---|---|
| 🚑 | Blessé — 8+ matchs manqués |
| 🩹 | Blessé — moins de 8 matchs manqués |
| 🏥 | Retour de blessure — 8+ matchs d'absence |
| 🐢 | Retour de blessure — 4 à 7 matchs d'absence |
""")

    colonnes_affichage = ['Joueur', 'Club', 'Note saison', 'Forme 6J', 'Régularité', '% Titulaire']

    if filtrer and mes_joueurs_input.strip():
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⭐ Mes joueurs", "⚡ Attaquants", "🎯 Milieux Off.",
            "🛡️ Milieux Déf.", "🔒 Défenseurs C.", "↔️ Défenseurs L.", "🧤 Gardiens"
        ])
        with tab0:
            top = df_mes_joueurs.sort_values('_score', ascending=False)[
                ['Joueur', 'Club', 'Poste', 'Note saison', 'Forme 6J', 'Régularité', '% Titulaire']
            ]
            if len(top) > 0:
                st.dataframe(top.reset_index(drop=True), use_container_width=True, height=500)
            else:
                st.warning("⚠️ Aucun joueur trouvé — vérifiez l'orthographe")
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⚡ Attaquants", "🎯 Milieux Off.", "🛡️ Milieux Déf.",
            "🔒 Défenseurs C.", "↔️ Défenseurs L.", "🧤 Gardiens"
        ])

    postes_tabs = {
        tab1: 'A', tab2: 'MO', tab3: 'MD',
        tab4: 'DC', tab5: 'DL', tab6: 'G'
    }
    for tab, code in postes_tabs.items():
        with tab:
            top = df_scores[df_scores['Poste'] == code].sort_values(
                '_score', ascending=False
            )[colonnes_affichage]
            if len(top) > 0:
                st.dataframe(top.reset_index(drop=True), use_container_width=True, height=500)
            else:
                st.info("Aucun joueur disponible pour ce poste")
