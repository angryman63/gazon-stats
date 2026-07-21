import streamlit as st
import pandas as pd
import numpy as np
from modele import nettoyer_note, calculer_clutch, compter_matchs, absences_consecutives, alerte_blessure
from utils.table_style import inject_style, pill, dash, name_cell, table_html, separateur

# ---------------------------------------------------------------------------
# Colonnes d'enchères disponibles selon la taille de ligue (fichier joueurs enrichi)
# ---------------------------------------------------------------------------
TAILLES_LIGUE = {
    "6 joueurs": {
        "enchere": "Enchere moy/L6",
        "achat_t1": "% achat T1/L6",
    },
    "8 joueurs": {
        "enchere": "Enchere moy/L8",
        "achat_t1": "% achat T1/L8",
    },
    "10 joueurs": {
        "enchere": "Enchere moy/L10",
        "achat_t1": "% achat T1/L10",
    },
    "Toutes tailles": {
        "enchere": "Enchere moy",
        "achat_t1": "% achat T1",
    },
}


def _colonnes_taille(df, taille_label):
    cfg = TAILLES_LIGUE[taille_label]
    col_enchere = cfg["enchere"] if cfg["enchere"] in df.columns else "Enchere moy"
    col_achat = "% achat T1" if "% achat T1" in df.columns else cfg["achat_t1"]
    return col_enchere, col_achat


def _tension(pct):
    if pd.isna(pct):
        return "?"
    if pct >= 80:
        return "🔥🔥 Très demandé"
    if pct >= 50:
        return "🔥 Demandé"
    if pct >= 20:
        return "Peu demandé"
    return "Indésirable"


def _pill_demande(val):
    val = str(val)
    if 'Très demandé' in val:
        return pill(val, 'info')
    if 'Demandé' in val:
        return pill(val, 'good')
    if 'Peu demandé' in val:
        return pill(val, 'warn')
    if 'Indésirable' in val:
        return pill(val, 'bad')
    return dash(val)


def _pill_alerte(val):
    val = '' if pd.isna(val) else str(val).strip()
    if not val:
        return dash()
    return pill(val, 'bad')


def _formater_cellule(col, val):
    if col == 'Demande':
        return _pill_demande(val)
    if col == 'Alerte':
        return _pill_alerte(val)
    if col == 'Joueur':
        return name_cell(val)
    if pd.isna(val):
        return dash()
    if col == 'Cote':
        return f"{val:.0f}"
    if col == 'Enchère moy.':
        return f"{val:.1f}"
    if col == 'Note':
        return f"{val:.2f}"
    if col == 'Buts':
        return f"{val:.0f}"
    if col == '%Titu':
        return f"{val:.0f}%"
    if col == 'Matchs joués':
        return f"{val:.0f}"
    return str(val)


def _table_html(df):
    return table_html(df, _formater_cellule)


def afficher_mercato(df, cols_journees):
    inject_style()
    separateur("TAILLE DE LA LIGUE")
    # --- Sélecteur de taille de ligue ---
    taille_choisie = st.radio(
        "Taille de la ligue :",
        list(TAILLES_LIGUE.keys()),
        horizontal=True,
        key="mercato_taille_ligue",
        label_visibility="collapsed"
    )
    col_enchere, col_achat = _colonnes_taille(df, taille_choisie)

    if col_enchere not in df.columns:
        st.warning(
            "Aucune donnée d'enchères trouvée dans le fichier joueurs chargé. "
            "Vérifie que le fichier joueurs enrichi (avec les colonnes d'enchères) est bien utilisé."
        )
        return

    if taille_choisie != "Toutes tailles" and TAILLES_LIGUE[taille_choisie]["enchere"] not in df.columns:
        st.caption(
            f"Pas de donnée détaillée pour les ligues à {taille_choisie.split()[0]} — "
            f"affichage de l'enchère moyenne toutes tailles confondues."
        )

    base_cols = ['Joueur', 'Poste', 'Cote', 'Var Cote', col_enchere, col_achat,
                 'Note', 'Variation', 'Buts', '%Titu', 'Indispo ?']
    df_mercato = df[base_cols].copy()
    df_mercato = df_mercato.rename(columns={
        col_enchere: 'Enchere',
        col_achat: 'AchatT1',
    })

    for col in ['Cote', 'Var Cote', 'Enchere', 'AchatT1', 'Note', 'Variation', 'Buts', '%Titu']:
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

    # --- Tension du marché (à partir du % achat T1) ---
    df_mercato['Tension'] = df_mercato['AchatT1'].apply(_tension)

    # À éviter — avant filtres
    df_eviter = df_mercato[
        ((df_mercato['Cote'] >= 20) & (df_mercato['Note'] < 5.2)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Note'] < 5.0)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Matchs_joues'] < seuil_matchs))
    ].copy()

    # Normalisation
    for col in ['Variation', 'Clutch', 'Popularite', 'Ratio']:
        col_min = df_mercato[col].min()
        col_max_norm = df_mercato[col].max()
        df_mercato[f'{col}_norm'] = (
            (df_mercato[col] - col_min) / (col_max_norm - col_min)
            if col_max_norm > col_min else 0
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

    separateur("STRATÉGIE MERCATO")
    # Sélection stratégie
    strategie_choisie = st.radio(
        "Stratégie mercato :",
        ["Stars", "Valeurs sûres", "Équilibre", "Pépites", "À éviter"],
        horizontal=True,
        key="mercato_strategie",
        label_visibility="collapsed"
    )

    with st.expander("🏥 Légende blessures"):
        st.markdown("""
|  | Statut |
|---|---|
| 🚑 | Blessé — 8+ matchs manqués |
| 🩹 | Blessé — moins de 8 matchs manqués |
| 🏥 | Retour de blessure — 8+ matchs d'absence |
| 🐢 | Retour de blessure — 4 à 7 matchs d'absence |
""")

    cols_affichage = ['Joueur', 'Poste', 'Cote', 'Enchere', 'Tension',
                       'Note', 'Buts', '%Titu', 'Matchs_joues', 'Alerte']

    strategie_map = {
        "Stars": ('stars', df_stars),
        "Valeurs sûres": ('valeurs_sures', df_valeurs),
        "Équilibre": ('equilibre', df_equilibre),
        "Pépites": ('pepites', df_pepites),
    }

    if strategie_choisie == "À éviter":
        st.subheader("Joueurs chers mais décevants")
        st.markdown(
            f'<p class="gs-caption">Enchères affichées pour : {taille_choisie}</p>',
            unsafe_allow_html=True
        )
        df_eviter['Raison'] = df_eviter.apply(lambda row:
            "Cher + peu de matchs" if row['Matchs_joues'] < seuil_matchs
            else "Cher + note décevante", axis=1
        )
        st.markdown(
            _table_html(
                df_eviter[['Joueur', 'Poste', 'Cote', 'Enchere', 'Tension',
                           'Note', 'Matchs_joues', '%Titu', 'Alerte', 'Raison']
                           ].rename(columns={'Enchere': 'Enchère moy.', 'Tension': 'Demande', 'Matchs_joues': 'Matchs joués'}).reset_index(drop=True)
            ),
            unsafe_allow_html=True
        )
    else:
        strategie_key, df_s = strategie_map[strategie_choisie]
        st.markdown(
            f'<p class="gs-caption">Enchères affichées pour : {taille_choisie}</p>',
            unsafe_allow_html=True
        )
        postes = {
            'A': 'Attaquants', 'MO': 'Milieux Off.',
            'MD': 'Milieux Déf.', 'DC': 'Défenseurs C.',
            'DL': 'Défenseurs L.', 'G': 'Gardiens'
        }
        tabs = st.tabs(list(postes.values()), key="mercato_postes")
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
                    st.markdown(
                        _table_html(
                            top[cols_affichage + ['Clutch']
                                ].rename(columns={'Enchere': 'Enchère moy.', 'Tension': 'Demande', 'Matchs_joues': 'Matchs joués'}).reset_index(drop=True)
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Aucun joueur disponible")
