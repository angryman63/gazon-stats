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

@st.cache_data
def charger_donnees(fichier):
    df = pd.read_excel(fichier)
    return df

df = charger_donnees(fichier)
st.success(f"✅ {len(df)} joueurs chargés !")

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def nettoyer_note(valeur):
    if pd.isna(valeur):
        return 0
    valeur = str(valeur)
    valeur = valeur.replace('*', '').replace('(', '').replace(')', '').replace('J', '').strip()
    try:
        note = float(valeur)
        if 0 <= note <= 10:
            return note
        return 0
    except:
        return 0

cols_journees = [col for col in df.columns if str(col).startswith('D') and str(col)[1:].isdigit()]
cols_journees = sorted(cols_journees, key=lambda x: int(x[1:]), reverse=True)
nb_journees = len(cols_journees)

for col in cols_journees:
    df[col] = df[col].apply(nettoyer_note)

def calculer_clutch(row, seuil=7):
    notes = [row[col] for col in cols_journees if col in df.columns]
    notes_jouees = [n for n in notes if n > 0]
    if len(notes_jouees) == 0:
        return 0
    return len([n for n in notes_jouees if n >= seuil]) / len(notes_jouees)

def compter_matchs(row):
    return sum(1 for col in cols_journees if row[col] > 0)

def absences_consecutives(row):
    notes = [row[col] for col in cols_journees]
    count = 0
    for n in notes:
        if n == 0:
            count += 1
        else:
            break
    return count

def predire_note(row, j_actuelle=None):
    notes = [row[col] for col in cols_journees if row[col] > 0]
    if len(notes) < 3:
        return None
    poids = [0.30, 0.23, 0.18, 0.14, 0.10, 0.05]
    notes_6 = notes[:6]
    total_poids = sum(poids[:len(notes_6)])
    return round(sum(n * poids[i] for i, n in enumerate(notes_6)) / total_poids, 2)

def alerte_blessure(row):
    indispo = row.get('Indispo ?', False)
    absences = absences_consecutives(row)
    if indispo == True:
        if absences >= 8:
            return f"🚑 Blessé ({absences} matchs)"
        elif absences >= 1:
            return f"🩹 Blessé ({absences} matchs)"
    else:
        if absences >= 8:
            return f"🏥 Retour ({absences} matchs)"
        elif absences >= 4:
            return f"🐢 Retour ({absences} matchs)"
    return ""

# ============================================================
# PAGES PRINCIPALES
# ============================================================

page1, page2, page3 = st.tabs([
    "🏆 Conseiller hebdo",
    "🛒 Mercato",
    "⚔️ Analyser mon adversaire"
])

# ============================================================
# PAGE 1 — CONSEILLER HEBDO
# ============================================================

with page1:
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

    def etiquette_regularite(valeur, q25, q50, q75):
        if valeur >= q75:
            return "1 ✅ Valeur sûre"
        elif valeur >= q50:
            return "2 👌 Fiable"
        elif valeur >= q25:
            return "3 ⚠️ Capricieux"
        else:
            return "4 🐐 Rotaldo"

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

    st.header("🏆 Recommandations par poste")
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
            st.dataframe(top.reset_index(drop=True), use_container_width=True, height=500)
    else:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⚡ Attaquants", "🎯 Milieux Off.", "🛡️ Milieux Déf.",
            "🔒 Défenseurs C.", "↔️ Défenseurs L.", "🧤 Gardiens"
        ])

    postes_tabs = {tab1: 'A', tab2: 'MO', tab3: 'MD', tab4: 'DC', tab5: 'DL', tab6: 'G'}
    for tab, code in postes_tabs.items():
        with tab:
            top = df_scores[df_scores['Poste'] == code].sort_values('_score', ascending=False)[colonnes_affichage]
            if len(top) > 0:
                st.dataframe(top.reset_index(drop=True), use_container_width=True, height=500)

# ============================================================
# PAGE 2 — MERCATO
# ============================================================

with page2:
    st.header("🛒 Conseiller Mercato")

    df_mercato = df[['Joueur', 'Poste', 'Cote', 'Note', 'Variation', 'Buts', '%Titu', 'Indispo ?']].copy()

    for col in ['Cote', 'Note', 'Variation', 'Buts', '%Titu']:
        df_mercato[col] = pd.to_numeric(df_mercato[col], errors='coerce')

    df_mercato = df_mercato.dropna(subset=['Cote', 'Note', 'Variation', '%Titu'])
    df_mercato = df_mercato[df_mercato['Cote'] > 0]

    df_mercato['Matchs_joues'] = df.apply(compter_matchs, axis=1)
    df_mercato['Absences_recentes'] = df.apply(absences_consecutives, axis=1)
    df_mercato['Alerte'] = df.apply(alerte_blessure, axis=1)
    df_mercato['Clutch'] = df.apply(lambda row: calculer_clutch(row, seuil=7), axis=1)
    df_mercato['Popularite'] = df_mercato['Cote'] * df_mercato['Note'] / 100
    df_mercato['Ratio'] = df_mercato['Note'] / df_mercato['Cote']

    seuil_matchs = int(nb_journees * 0.40)

    df_eviter = df_mercato[
        ((df_mercato['Cote'] >= 20) & (df_mercato['Note'] < 5.2)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Note'] < 5.0)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Matchs_joues'] < seuil_matchs))
    ].copy()

    for col in ['Variation', 'Clutch', 'Popularite', 'Ratio']:
        col_min = df_mercato[col].min()
        col_max = df_mercato[col].max()
        df_mercato[f'{col}_norm'] = (df_mercato[col] - col_min) / (col_max - col_min) if col_max > col_min else 0

    clutch_poids = {'G': 0.35, 'A': 0.30, 'MO': 0.20, 'DL': 0.15, 'MD': 0.10, 'DC': 0.10}

    def calculer_score_mercato(row, strategie):
        cp = clutch_poids.get(row['Poste'], 0.15)
        clutch = row['Clutch_norm'] * 10
        note = row['Note']
        variation = row['Variation_norm'] * 10
        ratio = row['Ratio_norm'] * 10
        titu = row['%Titu'] / 100 * 10
        pop = row['Popularite_norm'] * 10
        if strategie == 'stars':
            return note * 0.40 + clutch * cp + variation * 0.15 + titu * 0.10 + pop * 0.05
        elif strategie == 'valeurs_sures':
            return note * 0.35 + clutch * (cp * 0.8) + variation * 0.20 + ratio * 0.15 + titu * 0.10
        elif strategie == 'equilibre':
            return note * 0.30 + ratio * 0.25 + clutch * (cp * 0.7) + variation * 0.15 + titu * 0.10
        elif strategie == 'pepites':
            return ratio * 0.40 + note * 0.25 + clutch * (cp * 0.5) + variation * 0.15 + titu * 0.10

    for strategie in ['stars', 'valeurs_sures', 'equilibre', 'pepites']:
        df_mercato[f'Score_{strategie}'] = df_mercato.apply(
            lambda row: calculer_score_mercato(row, strategie), axis=1
        )

    df_stars = df_mercato[(df_mercato['Cote'] >= 25) & (df_mercato['Note'] >= 5.5) & (df_mercato['%Titu'] >= 60)].copy()
    df_valeurs = df_mercato[(df_mercato['Cote'] >= 12) & (df_mercato['Cote'] < 25) & (df_mercato['Note'] >= 5.2) & (df_mercato['%Titu'] >= 60)].copy()
    df_equilibre = df_mercato[(df_mercato['Cote'] >= 8) & (df_mercato['Note'] >= 5.0) & (df_mercato['%Titu'] >= 60)].copy()
    df_pepites = df_mercato[(df_mercato['Cote'] < 12) & (df_mercato['Note'] >= 5.0) & (df_mercato['%Titu'] >= 50)].copy()

    strategie_choisie = st.radio(
        "Choisissez votre stratégie mercato :",
        ["⭐⭐ Stars", "⭐ Valeurs sûres", "⚖️ Équilibre", "🌱 Pépites", "⚠️ À éviter"],
        horizontal=True
    )

    cols_affichage_mercato = ['Joueur', 'Cote', 'Note', 'Buts', '%Titu', 'Matchs_joues', 'Alerte']

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
            df_eviter[['Joueur', 'Poste', 'Cote', 'Note', 'Matchs_joues', '%Titu', 'Alerte', 'Raison']].reset_index(drop=True),
            use_container_width=True, height=400
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
                top = df_poste.sort_values(f'Score_{strategie_key}', ascending=False).head(10).copy()
                top['Clutch'] = top['Clutch'].apply(lambda x: f"{x*100:.0f}%")
                if len(top) > 0:
                    st.dataframe(top[cols_affichage_mercato + ['Clutch']].reset_index(drop=True),
                                use_container_width=True, height=400)
                else:
                    st.info("Aucun joueur disponible")

# ============================================================
# PAGE 3 — ANALYSER MON ADVERSAIRE
# ============================================================

with page3:
    st.header("⚔️ Analyser mon adversaire")

    # Stratégie de jeu
    st.subheader("🎯 Votre stratégie")
    strategie_jeu = st.radio(
        "Choisissez votre stratégie :",
        ["🗡️ Offensive", "⚖️ Équilibrée", "🛡️ Défensive"],
        horizontal=True
    )

    mode_analyse = st.radio(
        "Mode d'analyse :",
        ["🔮 Analyse préventive (avant match)", "🎯 Analyse précise (compo connue)"],
        horizontal=True
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔵 Mon équipe")
        mes_titu = st.text_area(
            "Mes titulaires (un par ligne)",
            placeholder="Koffi\nBalerdi\nOkoh\nCoppola\nMoreira\nTolisso\nThomasson\nKebbal\nGreenwood\nBarcola\nThauvin",
            height=250,
            key="mes_titu"
        )
        mes_remplacants = st.text_area(
            "Mes remplaçants (un par ligne)",
            placeholder="Safonov\nGradit\nRongier\nFofana",
            height=150,
            key="mes_rempl"
        )

    with col2:
        st.subheader("🔴 Équipe adverse")
        if "précise" in mode_analyse:
            adv_titu = st.text_area(
                "Titulaires adverses (un par ligne)",
                placeholder="Descamps\nChardonnet\nDiomandé\nGaniou\nUdol\nThomasson\nGboho\nAndré\nDoumbia\nSinayoko\nPagis",
                height=250,
                key="adv_titu"
            )
            adv_remplacants = st.text_area(
                "Remplaçants adverses (un par ligne)",
                placeholder="Safonov\nGradit\nSangaré\nLepaul",
                height=150,
                key="adv_rempl"
            )
        else:
            adv_joueurs = st.text_area(
                "Joueurs adverses disponibles (un par ligne)",
                placeholder="Descamps\nChardonnet\nDiomandé\nGaniou\nUdol\nThomasson\nGboho\nAndré\nDoumbia\nSinayoko\nPagis\nSafonov\nGradit",
                height=400,
                key="adv_joueurs"
            )

    st.markdown("---")

    if st.button("🚀 Lancer la simulation", type="primary"):

        # Récupérer les notes prédites
        def get_joueur_info(nom_joueur):
            row = df[df['Joueur'].str.lower() == nom_joueur.strip().lower()]
            if len(row) == 0:
                return None
            row = row.iloc[0]
            note_pred = predire_note(row)
            buts_moy = pd.to_numeric(row.get('Buts', 0), errors='coerce')
            matchs = compter_matchs(row)
            buts_par_match = (buts_moy / matchs) if matchs > 0 and not pd.isna(buts_moy) else 0
            clutch_7 = calculer_clutch(row, seuil=7)
            clutch_8 = calculer_clutch(row, seuil=8)
            poste = row.get('Poste', 'MO')
            return {
                'nom': row['Joueur'],
                'poste': poste,
                'note_pred': note_pred,
                'buts': buts_par_match,
                'clutch_7': clutch_7,
                'clutch_8': clutch_8,
                'regularite': 1 / (1 + np.std([row[col] for col in cols_journees if row[col] > 0] or [0])),
                'alerte': alerte_blessure(row)
            }

        # Mapper postes vers lignes MPG
        def poste_vers_ligne(poste):
            mapping = {'G': 'GB', 'DC': 'DEF', 'DL': 'DEF', 'MD': 'MIL', 'MO': 'MIL', 'A': 'ATT'}
            return mapping.get(poste, 'MIL')

        def bonus_poste(poste, dispositif):
            if poste in ['DC', 'DL'] and dispositif.get('nb_def', 0) >= 4:
                return 0.5
            return 0

        # Construire équipe depuis liste de noms
        def construire_equipe_noms(noms_titu, noms_rempl, strategie):
            titu_info = []
            rempl_info = []

            for nom in [n.strip() for n in noms_titu.split('\n') if n.strip()]:
                info = get_joueur_info(nom)
                if info:
                    titu_info.append(info)

            for nom in [n.strip() for n in noms_rempl.split('\n') if n.strip()]:
                info = get_joueur_info(nom)
                if info:
                    rempl_info.append(info)

            return titu_info, rempl_info

        # Construire meilleure compo depuis liste de joueurs disponibles
        def meilleure_compo(noms_joueurs, strategie):
            joueurs_info = []
            for nom in [n.strip() for n in noms_joueurs.split('\n') if n.strip()]:
                info = get_joueur_info(nom)
                if info and info['note_pred'] is not None:
                    joueurs_info.append(info)

            # Trier selon stratégie
            if strategie == "🗡️ Offensive":
                joueurs_info.sort(key=lambda x: x['clutch_7'], reverse=True)
            elif strategie == "🛡️ Défensive":
                joueurs_info.sort(key=lambda x: x['regularite'], reverse=True)
            else:
                joueurs_info.sort(key=lambda x: x['note_pred'] or 0, reverse=True)

            # Répartir par poste
            equipe = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
            limites = {'GB': 1, 'DEF': 4, 'MIL': 4, 'ATT': 2}
            remplacants = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}

            for j in joueurs_info:
                ligne = poste_vers_ligne(j['poste'])
                if len(equipe[ligne]) < limites[ligne]:
                    equipe[ligne].append(j)
                elif len(remplacants[ligne]) < 2:
                    remplacants[ligne].append(j)

            return equipe, remplacants

        # Simulation buts MPG
        def simuler_buts_mpg_info(equipe_att, equipe_def, domicile=True):
            buts_mpg = []

            moy_att = np.mean([j['note_pred'] for j in equipe_def.get('ATT', []) if j['note_pred']] or [5])
            moy_mil = np.mean([j['note_pred'] for j in equipe_def.get('MIL', []) if j['note_pred']] or [5])
            moy_def = np.mean([j['note_pred'] for j in equipe_def.get('DEF', []) if j['note_pred']] or [5])
            note_gb = equipe_def['GB'][0]['note_pred'] if equipe_def.get('GB') and equipe_def['GB'][0]['note_pred'] else 5

            for ligne, joueurs in equipe_att.items():
                if ligne == 'GB':
                    continue
                for j in joueurs:
                    note = j['note_pred']
                    if note is None or note < 5.5 or j['buts'] > 0:
                        continue
                    note_courante = note
                    if ligne == 'ATT':
                        lignes = [(moy_def, -1.0), (note_gb, -0.5)]
                    elif ligne == 'MIL':
                        lignes = [(moy_mil, -1.0), (moy_def, -0.5), (note_gb, -0.5)]
                    elif ligne == 'DEF':
                        lignes = [(moy_att, -1.0), (moy_mil, -0.5), (moy_def, -0.5), (note_gb, -0.5)]

                    but = True
                    for moy, malus in lignes:
                        passe = note_courante >= moy if domicile else note_courante > moy
                        if not passe:
                            but = False
                            break
                        note_courante += malus
                    if but:
                        buts_mpg.append(j['nom'])

            return buts_mpg

        # ============================================================
        # LANCEMENT SIMULATION
        # ============================================================

        st.markdown("---")
        st.subheader("📊 Résultats de la simulation")

        # Mon équipe
        titu_moi, rempl_moi = construire_equipe_noms(mes_titu, mes_remplacants, strategie_jeu)

        equipe_moi = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
        for j in titu_moi:
            ligne = poste_vers_ligne(j['poste'])
            equipe_moi[ligne].append(j)

        # Équipe adverse
        if "précise" in mode_analyse:
            titu_adv, rempl_adv = construire_equipe_noms(adv_titu, adv_remplacants, strategie_jeu)
            equipe_adv = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
            for j in titu_adv:
                ligne = poste_vers_ligne(j['poste'])
                equipe_adv[ligne].append(j)
        else:
            equipe_adv, _ = meilleure_compo(adv_joueurs, strategie_jeu)

        # Simulation
        buts_mpg_moi = simuler_buts_mpg_info(equipe_moi, equipe_adv, domicile=True)
        buts_mpg_adv = simuler_buts_mpg_info(equipe_adv, equipe_moi, domicile=False)

        buts_reels_moi = sum(j['buts'] for ligne in equipe_moi.values() for j in ligne)
        buts_reels_adv = sum(j['buts'] for ligne in equipe_adv.values() for j in ligne)

        # Arrêt MPG gardien
        arret_moi = equipe_moi['GB'][0]['note_pred'] >= 8 if equipe_moi.get('GB') and equipe_moi['GB'][0]['note_pred'] else False
        arret_adv = equipe_adv['GB'][0]['note_pred'] >= 8 if equipe_adv.get('GB') and equipe_adv['GB'][0]['note_pred'] else False

        if arret_moi:
            buts_reels_adv = max(0, buts_reels_adv - 1)
        if arret_adv:
            buts_reels_moi = max(0, buts_reels_moi - 1)

        score_moi = buts_reels_moi + len(buts_mpg_moi)
        score_adv = buts_reels_adv + len(buts_mpg_adv)

        # Affichage scores
        col_score1, col_score2, col_score3 = st.columns([2, 1, 2])
        with col_score1:
            st.metric("🔵 Mon équipe", f"{round(score_moi, 1)} buts")
            if buts_mpg_moi:
                st.success(f"⚽ Buts MPG : {', '.join(buts_mpg_moi)}")
            if arret_moi:
                st.info(f"🧤 Arrêt MPG de {equipe_moi['GB'][0]['nom']} !")
        with col_score2:
            if score_moi > score_adv:
                st.markdown("### 🏆 Victoire probable")
            elif score_moi < score_adv:
                st.markdown("### 😢 Défaite probable")
            else:
                st.markdown("### 🤝 Match nul probable")
        with col_score3:
            st.metric("🔴 Adversaire", f"{round(score_adv, 1)} buts")
            if buts_mpg_adv:
                st.error(f"⚽ Buts MPG adverses : {', '.join(buts_mpg_adv)}")
            if arret_adv:
                st.warning(f"🧤 Arrêt MPG adverse possible !")

        st.markdown("---")

        # Recommandation capitaine
        st.subheader("🎖️ Recommandation capitaine")

        candidats_cap = []
        for ligne, joueurs in equipe_moi.items():
            if ligne == 'GB':
                continue
            for j in joueurs:
                if j['note_pred'] is not None:
                    if strategie_jeu == "🗡️ Offensive":
                        score_cap = j['clutch_7'] * 0.6 + (j['note_pred'] / 10) * 0.4
                    elif strategie_jeu == "🛡️ Défensive":
                        score_cap = j['regularite'] * 0.6 + (j['note_pred'] / 10) * 0.4
                    else:
                        score_cap = (j['note_pred'] / 10) * 0.5 + j['regularite'] * 0.3 + j['clutch_7'] * 0.2
                    candidats_cap.append((j['nom'], j['poste'], j['note_pred'], score_cap))

        # Vérifier gardien clutch
        if equipe_moi.get('GB') and equipe_moi['GB'][0]['clutch_8'] >= 0.10:
            gb = equipe_moi['GB'][0]
            if strategie_jeu == "🛡️ Défensive":
                candidats_cap.append((gb['nom'], 'G', gb['note_pred'], 999))

        if candidats_cap:
            meilleur = max(candidats_cap, key=lambda x: x[3])
            st.success(f"🎖️ Capitaine recommandé : **{meilleur[0]}** ({meilleur[1]}) — Note prédite : {meilleur[2]}")

        # ============================================================
# GESTION DES BONUS
# ============================================================

st.markdown("---")
st.subheader("🎯 Gestion des bonus")

col_bonus1, col_bonus2 = st.columns(2)

liste_bonus = [
    "Aucun",
    "💼 Valise à Nanard — annule 1 but adverse",
    "🪞 Miroir — retourne le bonus adverse",
    "💃 Zahia — +1 à tous mes joueurs",
    "🦷 Suarez — -1 au gardien adverse",
    "👊 Tonton Pat' — annule remplacements adverses",
    "🟥 Chapron Rouge — retire 1 joueur adverse au hasard",
    "💻 Cheat Code — -0.5 à tous joueurs adverses",
    "🍔 Uber Eats — +1 à un joueur choisi",
]

with col_bonus1:
    st.markdown("**Mes bonus disponibles**")
    mon_bonus = st.selectbox("Bonus à utiliser ce match :", liste_bonus, key="mon_bonus")
    if mon_bonus == "🍔 Uber Eats — +1 à un joueur choisi":
        joueur_uber = st.selectbox(
            "Choisir le joueur :",
            [j['nom'] for ligne in equipe_moi.values() for j in ligne if j['nom'] != 'Rotaldo'],
            key="joueur_uber"
        )
    importance_match = st.radio(
        "Importance du match :",
        ["🔥 Crucial", "⚽ Normal", "😴 Sans enjeu"],
        horizontal=True,
        key="importance"
    )

with col_bonus2:
    st.markdown("**Bonus adverses déjà utilisés**")
    bonus_adv_utilises = st.multiselect(
        "Cochez les bonus déjà utilisés par l'adversaire :",
        [b for b in liste_bonus if b != "Aucun"],
        key="bonus_adv_utilises"
    )
    bonus_adv_restant = st.selectbox(
        "Bonus adverse probable ce match :",
        liste_bonus,
        key="bonus_adv_restant"
    )

# ============================================================
# SIMULATION AVEC BONUS
# ============================================================

# Copie des notes pour simulation avec bonus
import copy

def appliquer_bonus(equipe_moi, equipe_adv, mon_bonus, bonus_adv, joueur_uber=None):
    # Deep copy pour ne pas modifier les originaux
    eq_moi_bonus = copy.deepcopy(equipe_moi)
    eq_adv_bonus = copy.deepcopy(equipe_adv)

    buts_annules_adv = 0
    buts_annules_moi = 0

    # MON BONUS
    if "Zahia" in mon_bonus:
        for ligne, joueurs in eq_moi_bonus.items():
            for j in joueurs:
                if j['note_pred'] and ligne != 'GB':
                    j['note_pred'] = min(10, j['note_pred'] + 1)

    elif "Suarez" in mon_bonus:
        if eq_adv_bonus.get('GB') and eq_adv_bonus['GB'][0]['note_pred']:
            eq_adv_bonus['GB'][0]['note_pred'] = max(0, eq_adv_bonus['GB'][0]['note_pred'] - 1)

    elif "Cheat Code" in mon_bonus:
        for ligne, joueurs in eq_adv_bonus.items():
            if ligne == 'GB':
                continue
            for j in joueurs:
                if j['note_pred']:
                    j['note_pred'] = max(0, j['note_pred'] - 0.5)

    elif "Valise" in mon_bonus:
        buts_annules_adv = 1

    elif "Uber Eats" in mon_bonus and joueur_uber:
        for ligne, joueurs in eq_moi_bonus.items():
            for j in joueurs:
                if j['nom'] == joueur_uber and j['note_pred']:
                    j['note_pred'] = min(10, j['note_pred'] + 1)

    elif "Tonton" in mon_bonus:
        pass  # Annule remplacements tactiques adverses — pas de simulation possible

    elif "Chapron" in mon_bonus:
        # Retire le joueur adverse avec la note la plus haute
        meilleur_score = 0
        meilleure_ligne = None
        meilleur_idx = None
        for ligne, joueurs in eq_adv_bonus.items():
            if ligne == 'GB':
                continue
            for idx, j in enumerate(joueurs):
                if j['note_pred'] and j['note_pred'] > meilleur_score:
                    meilleur_score = j['note_pred']
                    meilleure_ligne = ligne
                    meilleur_idx = idx
        if meilleure_ligne and meilleur_idx is not None:
            eq_adv_bonus[meilleure_ligne][meilleur_idx] = {
                'nom': 'Rotaldo', 'note_pred': 2.5, 'buts': 0,
                'clutch_7': 0, 'clutch_8': 0, 'regularite': 0, 'alerte': ''
            }

    # BONUS ADVERSE
    if "Zahia" in bonus_adv:
        for ligne, joueurs in eq_adv_bonus.items():
            if ligne != 'GB':
                for j in joueurs:
                    if j['note_pred']:
                        j['note_pred'] = min(10, j['note_pred'] + 1)

    elif "Suarez" in bonus_adv:
        if eq_moi_bonus.get('GB') and eq_moi_bonus['GB'][0]['note_pred']:
            eq_moi_bonus['GB'][0]['note_pred'] = max(0, eq_moi_bonus['GB'][0]['note_pred'] - 1)

    elif "Cheat Code" in bonus_adv:
        for ligne, joueurs in eq_moi_bonus.items():
            if ligne == 'GB':
                continue
            for j in joueurs:
                if j['note_pred']:
                    j['note_pred'] = max(0, j['note_pred'] - 0.5)

    elif "Valise" in bonus_adv:
        buts_annules_moi = 1

    elif "Chapron" in bonus_adv:
        meilleur_score = 0
        meilleure_ligne = None
        meilleur_idx = None
        for ligne, joueurs in eq_moi_bonus.items():
            if ligne == 'GB':
                continue
            for idx, j in enumerate(joueurs):
                if j['note_pred'] and j['note_pred'] > meilleur_score:
                    meilleur_score = j['note_pred']
                    meilleure_ligne = ligne
                    meilleur_idx = idx
        if meilleure_ligne and meilleur_idx is not None:
            eq_moi_bonus[meilleure_ligne][meilleur_idx] = {
                'nom': 'Rotaldo', 'note_pred': 2.5, 'buts': 0,
                'clutch_7': 0, 'clutch_8': 0, 'regularite': 0, 'alerte': ''
            }

    return eq_moi_bonus, eq_adv_bonus, buts_annules_adv, buts_annules_moi

# Simulation sans bonus
buts_mpg_moi_sb = simuler_buts_mpg_info(equipe_moi, equipe_adv, domicile=True)
buts_mpg_adv_sb = simuler_buts_mpg_info(equipe_adv, equipe_moi, domicile=False)
score_moi_sb = buts_reels_moi + len(buts_mpg_moi_sb)
score_adv_sb = buts_reels_adv + len(buts_mpg_adv_sb)

# Simulation avec mon bonus
joueur_uber_sel = joueur_uber if "Uber Eats" in mon_bonus else None
eq_moi_b, eq_adv_b, ann_adv, ann_moi = appliquer_bonus(
    equipe_moi, equipe_adv, mon_bonus, bonus_adv_restant, joueur_uber_sel
)

buts_mpg_moi_ab = simuler_buts_mpg_info(eq_moi_b, eq_adv_b, domicile=True)
buts_mpg_adv_ab = simuler_buts_mpg_info(eq_adv_b, eq_moi_b, domicile=False)
score_moi_ab = max(0, buts_reels_moi + len(buts_mpg_moi_ab) - ann_moi)
score_adv_ab = max(0, buts_reels_adv + len(buts_mpg_adv_ab) - ann_adv)

# Miroir
if "Miroir" in mon_bonus and bonus_adv_restant != "Aucun":
    eq_moi_miroir, eq_adv_miroir, ann_adv_m, ann_moi_m = appliquer_bonus(
        equipe_moi, equipe_adv, bonus_adv_restant, "Aucun"
    )
    buts_mpg_moi_m = simuler_buts_mpg_info(eq_moi_miroir, eq_adv_miroir, domicile=True)
    buts_mpg_adv_m = simuler_buts_mpg_info(eq_adv_miroir, eq_moi_miroir, domicile=False)
    score_moi_ab = max(0, buts_reels_moi + len(buts_mpg_moi_m) - ann_moi_m)
    score_adv_ab = max(0, buts_reels_adv + len(buts_mpg_adv_m) - ann_adv_m)

# ============================================================
# AFFICHAGE COMPARAISON ET RECOMMANDATION
# ============================================================

st.markdown("---")
st.subheader("📊 Analyse des bonus")

col_sb, col_ab = st.columns(2)

with col_sb:
    st.markdown("**Sans bonus**")
    diff_sb = score_moi_sb - score_adv_sb
    if diff_sb > 0:
        st.success(f"🔵 {round(score_moi_sb,1)} - {round(score_adv_sb,1)} 🔴 — Victoire probable")
    elif diff_sb < 0:
        st.error(f"🔵 {round(score_moi_sb,1)} - {round(score_adv_sb,1)} 🔴 — Défaite probable")
    else:
        st.warning(f"🔵 {round(score_moi_sb,1)} - {round(score_adv_sb,1)} 🔴 — Match nul probable")

with col_ab:
    if mon_bonus != "Aucun":
        st.markdown(f"**Avec {mon_bonus.split('—')[0].strip()}**")
        diff_ab = score_moi_ab - score_adv_ab
        if diff_ab > 0:
            st.success(f"🔵 {round(score_moi_ab,1)} - {round(score_adv_ab,1)} 🔴 — Victoire probable")
        elif diff_ab < 0:
            st.error(f"🔵 {round(score_moi_ab,1)} - {round(score_adv_ab,1)} 🔴 — Défaite probable")
        else:
            st.warning(f"🔵 {round(score_moi_ab,1)} - {round(score_adv_ab,1)} 🔴 — Match nul probable")

# ============================================================
# RECOMMANDATION FINALE
# ============================================================

st.markdown("---")
st.subheader("🎯 Recommandation Gazon Stats")

diff_sb = score_moi_sb - score_adv_sb
diff_ab = score_moi_ab - score_adv_ab if mon_bonus != "Aucun" else diff_sb
gain_bonus = diff_ab - diff_sb

# Logique de recommandation
if diff_sb >= 2:
    st.success("✅ **N'utilisez PAS de bonus ce match** — Victoire confortable sans bonus. Économisez-le pour un match plus serré !")
elif diff_sb >= 1:
    if importance_match == "🔥 Crucial":
        if mon_bonus != "Aucun" and gain_bonus > 0:
            st.success(f"✅ **Utilisez {mon_bonus.split('—')[0].strip()}** — Match crucial et bonus améliore le résultat de +{round(gain_bonus,1)} but(s)")
        else:
            st.info("💡 **Victoire probable sans bonus** — Match crucial : utilisez un bonus uniquement si vous avez Valise ou Zahia")
    else:
        st.success("✅ **N'utilisez PAS de bonus** — Victoire probable sans prendre de risque. Gardez votre bonus !")
elif diff_sb == 0:
    if mon_bonus != "Aucun" and gain_bonus > 0:
        st.warning(f"⚠️ **Utilisez {mon_bonus.split('—')[0].strip()}** — Match nul prévu, le bonus peut faire la différence !")
    else:
        st.warning("⚠️ **Match serré** — Envisagez Zahia ou Cheat Code si disponible")
elif diff_sb == -1:
    if mon_bonus != "Aucun" and gain_bonus >= 1:
        st.warning(f"⚠️ **Utilisez {mon_bonus.split('—')[0].strip()}** — Peut renverser la situation !")
    else:
        st.error("❌ **Situation difficile** — Utilisez votre meilleur bonus offensif")
else:
    st.error("❌ **Défaite probable** — Utilisez un bonus ou acceptez la défaite et économisez pour plus tard")

# Alerte Miroir
if "Miroir" not in [b for b in bonus_adv_utilises] and bonus_adv_restant != "Aucun":
    st.info(f"🪞 **Attention** — L'adversaire a encore son bonus {bonus_adv_restant.split('—')[0].strip()} disponible !")

# Alerte si adversaire a Miroir
if any("Miroir" in b for b in [bonus_adv_restant]):
    st.warning("🪞 **L'adversaire a le Miroir !** — Si vous utilisez un bonus, il peut le retourner contre vous. Soyez prudent !")
        
        # Détails équipes
        st.markdown("---")
        col_eq1, col_eq2 = st.columns(2)

        with col_eq1:
            st.subheader("🔵 Mon équipe — Détails")
            for ligne in ['GB', 'DEF', 'MIL', 'ATT']:
                for j in equipe_moi.get(ligne, []):
                    note = f"{j['note_pred']:.2f}" if j['note_pred'] else "?"
                    alerte = f" {j['alerte']}" if j['alerte'] else ""
                    clutch = f" | Clutch: {j['clutch_7']*100:.0f}%"
                    st.write(f"**{ligne}** | {j['nom']} — Note prédite: {note}{clutch}{alerte}")

        with col_eq2:
            st.subheader("🔴 Équipe adverse — Détails")
            for ligne in ['GB', 'DEF', 'MIL', 'ATT']:
                for j in equipe_adv.get(ligne, []):
                    note = f"{j['note_pred']:.2f}" if j['note_pred'] else "?"
                    alerte = f" {j['alerte']}" if j['alerte'] else ""
                    # Détection Rotaldo probable
                    rotaldo = " ⚠️ Rotaldo probable !" if j['note_pred'] is None or j['note_pred'] < 3 else ""
                    st.write(f"**{ligne}** | {j['nom']} — Note prédite: {note}{alerte}{rotaldo}")
