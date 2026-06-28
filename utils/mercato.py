import streamlit as st
import pandas as pd
import numpy as np
from modele import nettoyer_note, calculer_clutch, compter_matchs, absences_consecutives, alerte_blessure

# ─── Identité visuelle Maestro Tactico ───────────────────────────────────────
MT_CSS = """
<style>
:root {
    --mt-bg:        #0d0d0d;
    --mt-card:      #1a1a1a;
    --mt-or:        #c8a84b;
    --mt-or-fonce:  #8a6f2e;
    --mt-blanc:     #ffffff;
    --mt-gris:      #555555;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--mt-bg) !important;
}
[data-testid="stHeader"] {
    background-color: #0d0d0d !important;
}
section[data-testid="stSidebar"] {
    background-color: #141414 !important;
}

h1, h2, h3 {
    color: var(--mt-blanc) !important;
    letter-spacing: 0.05em;
}

/* ── Radio ── */
[data-testid="stRadio"] label {
    color: #ffffff !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] div {
    border-color: #c8a84b !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #141414;
    border-bottom: 1px solid #2a2a2a;
    gap: 4px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #555555 !important;
    background-color: transparent !important;
    border-radius: 4px 4px 0 0;
    padding: 8px 16px;
    font-weight: 600;
    transition: color 0.2s;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #c8a84b !important;
    border-bottom: 2px solid #c8a84b !important;
    background-color: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #c8a84b !important;
}

/* ── Dataframe — dark mode complet ── */
[data-testid="stDataFrame"] > div {
    background-color: #1a1a1a !important;
    border-radius: 8px;
    border-left: 3px solid;
    border-image: linear-gradient(to bottom, #c8a84b, #8a6f2e) 1;
}
[data-testid="stDataFrame"] iframe {
    background-color: #1a1a1a !important;
}
[data-testid="stDataFrame"] [class*="dvn-scroller"] {
    background-color: #1a1a1a !important;
}
[data-testid="stDataFrame"] table {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
    border-collapse: collapse;
    width: 100%;
}
[data-testid="stDataFrame"] thead tr th {
    background-color: #0d0d0d !important;
    color: #c8a84b !important;
    font-weight: 700;
    letter-spacing: 0.04em;
    border-bottom: 1px solid #c8a84b !important;
    padding: 8px 12px;
}
[data-testid="stDataFrame"] tbody tr td {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
    border-bottom: 1px solid #333333 !important;
    padding: 6px 12px;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background-color: #222222 !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #2a2a2a !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    border-left: 3px solid #c8a84b !important;
}
[data-testid="stExpander"] summary {
    color: #c8a84b !important;
    font-weight: 600;
}
[data-testid="stExpander"] table {
    background-color: transparent !important;
    color: #ffffff !important;
}
[data-testid="stExpander"] table thead th {
    color: #c8a84b !important;
    border-bottom: 1px solid #c8a84b !important;
}

/* ── Info / Warning ── */
[data-testid="stWarning"], [data-testid="stInfo"] {
    background-color: #1a1a1a !important;
    border-left: 3px solid #c8a84b !important;
    color: #ffffff !important;
    border-radius: 0 6px 6px 0;
}

hr {
    border: none;
    border-top: 1px solid #2a2a2a !important;
    margin: 1.5rem 0;
}

p, li, span, label {
    color: #ffffff !important;
}
strong {
    color: #c8a84b !important;
}
</style>
"""

def _separateur(titre):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:1.5rem 0 1rem;">
        <div style="flex:1;height:1px;background:linear-gradient(to right,#c8a84b,transparent);"></div>
        <span style="color:#c8a84b;font-weight:700;letter-spacing:0.12em;font-size:0.82rem;white-space:nowrap;">
            {titre}
        </span>
        <div style="flex:1;height:1px;background:linear-gradient(to left,#c8a84b,transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────

def afficher_mercato(df, cols_journees):

    st.markdown(MT_CSS, unsafe_allow_html=True)

    st.markdown("""
    <h1 style="color:#ffffff;letter-spacing:0.08em;margin-bottom:0.2rem;">
        🛒 Conseiller Mercato
    </h1>
    """, unsafe_allow_html=True)

    df_mercato = df[['Joueur', 'Poste', 'Cote', 'Note', 'Variation', 'Buts', '%Titu', 'Indispo ?']].copy()

    for col in ['Cote', 'Note', 'Variation', 'Buts', '%Titu']:
        df_mercato[col] = pd.to_numeric(df_mercato[col], errors='coerce')

    df_mercato = df_mercato.dropna(subset=['Cote', 'Note', 'Variation', '%Titu'])
    df_mercato = df_mercato[df_mercato['Cote'] > 0]

    nb_journees = len(cols_journees)
    seuil_matchs = int(nb_journees * 0.40)

    df_mercato['Matchs_joues'] = df.apply(
        lambda row: compter_matchs(row, cols_journees), axis=1)
    df_mercato['Absences_recentes'] = df.apply(
        lambda row: absences_consecutives(row, cols_journees), axis=1)
    df_mercato['Alerte'] = df.apply(
        lambda row: alerte_blessure(row, cols_journees), axis=1)
    df_mercato['Clutch'] = df.apply(
        lambda row: calculer_clutch(row, cols_journees, seuil=7), axis=1)
    df_mercato['Popularite'] = df_mercato['Cote'] * df_mercato['Note'] / 100
    df_mercato['Ratio'] = df_mercato['Note'] / df_mercato['Cote']

    # À éviter — avant filtres
    df_eviter = df_mercato[
        ((df_mercato['Cote'] >= 20) & (df_mercato['Note'] < 5.2)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Note'] < 5.0)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Matchs_joues'] < seuil_matchs))
    ].copy()

    # Normalisation
    for col in ['Variation', 'Clutch', 'Popularite', 'Ratio']:
        col_min = df_mercato[col].min()
        col_max = df_mercato[col].max()
        df_mercato[f'{col}_norm'] = (
            (df_mercato[col] - col_min) / (col_max - col_min)
            if col_max > col_min else 0
        )

    clutch_poids = {
        'G': 0.35, 'A': 0.30, 'MO': 0.20,
        'DL': 0.15, 'MD': 0.10, 'DC': 0.10
    }

    def calculer_score_mercato(row, strategie):
        cp = clutch_poids.get(row['Poste'], 0.15)
        clutch = row['Clutch_norm'] * 10
        note = row['Note']
        variation = row['Variation_norm'] * 10
        ratio = row['Ratio_norm'] * 10
        titu = row['%Titu'] / 100 * 10
        pop = row['Popularite_norm'] * 10
        if strategie == 'stars':
            return note*0.40 + clutch*cp + variation*0.15 + titu*0.10 + pop*0.05
        elif strategie == 'valeurs_sures':
            return note*0.35 + clutch*(cp*0.8) + variation*0.20 + ratio*0.15 + titu*0.10
        elif strategie == 'equilibre':
            return note*0.30 + ratio*0.25 + clutch*(cp*0.7) + variation*0.15 + titu*0.10
        elif strategie == 'pepites':
            return ratio*0.40 + note*0.25 + clutch*(cp*0.5) + variation*0.15 + titu*0.10

    for strategie in ['stars', 'valeurs_sures', 'equilibre', 'pepites']:
        df_mercato[f'Score_{strategie}'] = df_mercato.apply(
            lambda row: calculer_score_mercato(row, strategie), axis=1
        )

    df_stars = df_mercato[
        (df_mercato['Cote'] >= 25) &
        (df_mercato['Note'] >= 5.5) &
        (df_mercato['%Titu'] >= 60)
    ].copy()

    df_valeurs = df_mercato[
        (df_mercato['Cote'] >= 12) &
        (df_mercato['Cote'] < 25) &
        (df_mercato['Note'] >= 5.2) &
        (df_mercato['%Titu'] >= 60)
    ].copy()

    df_equilibre = df_mercato[
        (df_mercato['Cote'] >= 8) &
        (df_mercato['Note'] >= 5.0) &
        (df_mercato['%Titu'] >= 60)
    ].copy()

    df_pepites = df_mercato[
        (df_mercato['Cote'] < 12) &
        (df_mercato['Note'] >= 5.0) &
        (df_mercato['%Titu'] >= 50)
    ].copy()

    _separateur("STRATÉGIE MERCATO")

    strategie_choisie = st.radio(
        "Choisissez votre stratégie mercato :",
        ["⭐⭐ Stars", "⭐ Valeurs sûres", "⚖️ Équilibre", "🌱 Pépites", "⚠️ À éviter"],
        horizontal=True
    )

    with st.expander("🏥 Légende blessures"):
        st.markdown("""
| Emoji | Statut |
|---|---|
| 🚑 | Blessé — 8+ matchs manqués |
| 🩹 | Blessé — moins de 8 matchs manqués |
| 🏥 | Retour de blessure — 8+ matchs d'absence |
| 🐢 | Retour de blessure — 4 à 7 matchs d'absence |
""")

    cols_affichage = ['Joueur', 'Cote', 'Note', 'Buts', '%Titu', 'Matchs_joues', 'Alerte']

    strategie_map = {
        "⭐⭐ Stars": ('stars', df_stars),
        "⭐ Valeurs sûres": ('valeurs_sures', df_valeurs),
        "⚖️ Équilibre": ('equilibre', df_equilibre),
        "🌱 Pépites": ('pepites', df_pepites),
    }

    _separateur("JOUEURS PAR POSTE")

    if strategie_choisie == "⚠️ À éviter":
        st.markdown("""
        <p style="color:#c8a84b;font-weight:700;letter-spacing:0.06em;">
            ⚠️ JOUEURS CHERS MAIS DÉCEVANTS
        </p>
        """, unsafe_allow_html=True)
        df_eviter['Raison'] = df_eviter.apply(lambda row:
            "💸 Cher + peu de matchs" if row['Matchs_joues'] < seuil_matchs
            else "📉 Cher + note décevante", axis=1
        )
        st.dataframe(
            df_eviter[['Joueur', 'Poste', 'Cote', 'Note', 'Matchs_joues', '%Titu', 'Alerte', 'Raison']
            ].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
    else:
        strategie_key, df_s = strategie_map[strategie_choisie]
        postes = {
            'A': '⚡ Attaquants', 'MO': '🎯 Milieux Off.',
            'MD': '🛡️ Milieux Déf.', 'DC': '🔒 Défenseurs C.',
            'DL': '↔️ Défenseurs L.', 'G': '🧤 Gardiens'
        }
        tabs = st.tabs(list(postes.values()))
        for tab, (code, nom) in zip(tabs, postes.items()):
            with tab:
                if strategie_key == 'stars' and code == 'DC':
                    df_poste = df_mercato[
                        (df_mercato['Poste'] == 'DC') &
                        (df_mercato['Cote'] >= 20) &
                        (df_mercato['Note'] >= 5.3) &
                        (df_mercato['%Titu'] >= 60)
                    ]
                else:
                    df_poste = df_s[df_s['Poste'] == code]

                top = df_poste.sort_values(
                    f'Score_{strategie_key}', ascending=False
                ).head(10).copy()
                top['Clutch'] = top['Clutch'].apply(lambda x: f"{x*100:.0f}%")

                if len(top) > 0:
                    st.dataframe(
                        top[cols_affichage + ['Clutch']].reset_index(drop=True),
                        use_container_width=True,
                        height=400
                    )
                else:
                    st.info("Aucun joueur disponible")
