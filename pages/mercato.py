import streamlit as st
import pandas as pd
import numpy as np
from modele import nettoyer_note, calculer_clutch, compter_matchs, absences_consecutives, alerte_blessure

def afficher_mercato(df, cols_journees):

    st.header("🛒 Conseiller Mercato")

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

    # Sélection stratégie
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

    if strategie_choisie == "⚠️ À éviter":
        st.subheader("⚠️ Joueurs chers mais décevants")
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
