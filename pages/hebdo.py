import streamlit as st
import pandas as pd
import numpy as np
from modele import nettoyer_note, calculer_clutch, predire_note, alerte_blessure, etiquette_regularite, absences_consecutives

def afficher_hebdo(df, cols_journees, mes_joueurs_input, filtrer):

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
                'Forme récente': round(float(moyenne), 2),
                '_regularite_brute': regularite_brute,
                '% Titulaire': f"{int(prob_jouer*100)}%",
                '_score': round(float(score), 2)
            })

    df_scores = pd.DataFrame(scores)

    for poste in df_scores['Poste'].unique():
        mask = df_scores['Poste'] == poste
        vals = df_scores.loc[mask, '_regularite_brute']
        q10, q50, q80 = vals.quantile([0.10, 0.50, 0.80])
        df_scores.loc[mask, 'Fiabilité'] = df_scores.loc[mask, '_regularite_brute'].apply(
            lambda x: etiquette_regularite(x, q10, q50, q80)
        )

    df_mes_joueurs = df_scores.copy()
    if filtrer and mes_joueurs_input.strip():
        mes_joueurs = [j.strip().lower() for j in mes_joueurs_input.split('\n') if j.strip()]
        df_mes_joueurs = df_scores[df_scores['Joueur'].str.lower().isin(mes_joueurs)]

    st.header("🏆 Recommandations par poste")
    colonnes_affichage = ['Joueur', 'Club', 'Note saison', 'Forme récente', 'Fiabilité', '% Titulaire']

    if filtrer and mes_joueurs_input.strip():
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⭐ Mes joueurs", "⚡ Attaquants", "🎯 Milieux Off.",
            "🛡️ Milieux Déf.", "🔒 Défenseurs C.", "↔️ Défenseurs L.", "🧤 Gardiens"
        ])
        with tab0:
            top = df_mes_joueurs.sort_values('_score', ascending=False)[
                ['Joueur', 'Club', 'Poste', 'Note saison', 'Forme récente', 'Fiabilité', '% Titulaire']
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
