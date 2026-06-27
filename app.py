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

# ============================================================
# PAGE PRINCIPALE — 2 onglets
# ============================================================

page1, page2 = st.tabs(["🏆 Conseiller hebdo", "🛒 Mercato"])

# ============================================================
# PAGE 1 — CONSEILLER HEBDO
# ============================================================

with page1:
    scores = []
    for idx, row in df.iterrows():
        notes = [row[col] for col in cols_journees]
        notes_jouees = [n for n in notes if n > 0]
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
            top = df_mes_joueurs.sort_values('_score', ascending=False)[['Joueur', 'Club', 'Poste', 'Note saison', 'Forme 6J', 'Régularité', '% Titulaire']]
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

    # Matchs joués et absences
    def compter_matchs(row):
        notes = [row[col] for col in cols_journees if col in df.columns]
        return len([n for n in notes if n > 0])

    def absences_consecutives(row):
        notes = [row[col] for col in cols_journees if col in df.columns]
        count = 0
        for n in notes:
            if n == 0:
                count += 1
            else:
                break
        return count

    df_mercato['Matchs_joues'] = df.apply(compter_matchs, axis=1)
    df_mercato['Absences_recentes'] = df.apply(absences_consecutives, axis=1)

    def alerte_blessure(row):
        indispo = row['Indispo ?']
        absences = row['Absences_recentes']
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

    df_mercato['Alerte'] = df_mercato.apply(alerte_blessure, axis=1)

    seuil_matchs = int(nb_journees * 0.40)
    df_eviter = df_mercato[
        ((df_mercato['Cote'] >= 20) & (df_mercato['Note'] < 5.2)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Note'] < 5.0)) |
        ((df_mercato['Cote'] >= 15) & (df_mercato['Matchs_joues'] < seuil_matchs))
    ].copy()

    def compter_clutch(row):
        notes = [row[col] for col in cols_journees if col in df.columns]
        notes_jouees = [n for n in notes if n > 0]
        if len(notes_jouees) == 0:
            return 0
        return len([n for n in notes_jouees if n >= 7]) / len(notes_jouees)

    df_mercato['Clutch'] = df.apply(compter_clutch, axis=1)
    df_mercato['Popularite'] = df_mercato['Cote'] * df_mercato['Note'] / 100

    for col in ['Variation', 'Clutch', 'Popularite']:
        col_min = df_mercato[col].min()
        col_max = df_mercato[col].max()
        df_mercato[f'{col}_norm'] = (df_mercato[col] - col_min) / (col_max - col_min)

    df_mercato['Ratio'] = df_mercato['Note'] / df_mercato['Cote']
    ratio_min = df_mercato['Ratio'].min()
    ratio_max = df_mercato['Ratio'].max()
    df_mercato['Ratio_norm'] = (df_mercato['Ratio'] - ratio_min) / (ratio_max - ratio_min)

    clutch_poids = {'G': 0.35, 'A': 0.30, 'MO': 0.20, 'DL': 0.15, 'MD': 0.10, 'DC': 0.10}

    def calculer_score(row, strategie):
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
            lambda row: calculer_score(row, strategie), axis=1
        )

    df_stars = df_mercato[(df_mercato['Cote'] >= 25) & (df_mercato['Note'] >= 5.5) & (df_mercato['%Titu'] >= 60)].copy()
    df_valeurs = df_mercato[(df_mercato['Cote'] >= 12) & (df_mercato['Cote'] < 25) & (df_mercato['Note'] >= 5.2) & (df_mercato['%Titu'] >= 60)].copy()
    df_equilibre = df_mercato[(df_mercato['Cote'] >= 8) & (df_mercato['Note'] >= 5.0) & (df_mercato['%Titu'] >= 60)].copy()
    df_pepites = df_mercato[(df_mercato['Cote'] < 12) & (df_mercato['Note'] >= 5.0) & (df_mercato['%Titu'] >= 50)].copy()

    # Sélection stratégie
    strategie_choisie = st.radio(
        "Choisissez votre stratégie mercato :",
        ["⭐⭐ Stars", "⭐ Valeurs sûres", "⚖️ Équilibre", "🌱 Pépites", "⚠️ À éviter"],
        horizontal=True
    )

    cols_affichage = ['Joueur', 'Cote', 'Note', 'Clutch', 'Buts', '%Titu', 'Matchs_joues', 'Alerte']

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
            use_container_width=True,
            height=400
        )
    else:
        strategie_key, df_s = strategie_map[strategie_choisie]
        postes = {'A': '⚡ Attaquants', 'MO': '🎯 Milieux Off.', 'MD': '🛡️ Milieux Déf.',
                  'DC': '🔒 Défenseurs C.', 'DL': '↔️ Défenseurs L.', 'G': '🧤 Gardiens'}

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
                    st.dataframe(top[cols_affichage].reset_index(drop=True), use_container_width=True, height=400)
                else:
                    st.info("Aucun joueur disponible")
