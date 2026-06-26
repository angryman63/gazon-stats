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

st.sidebar.header("📁 Importer vos données")
fichier = st.sidebar.file_uploader(
    "Téléchargez le fichier MPGStats (xlsx)",
    type=['xlsx']
)

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

for col in cols_journees:
    df[col] = df[col].apply(nettoyer_note)

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
        
        score = (moyenne_saison * 0.5 +
                 moyenne * 0.3 +
                 regularite_brute * 0.1 +
                 prob_jouer * 0.1)
        
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
        return "\u200b\u200b\u200b✅ Valeur sûre"
    elif valeur >= q50:
        return "\u200b\u200b\u200b\u200b👌 Fiable"
    elif valeur >= q25:
        return "\u200b⚠️ Capricieux"
    else:
        return "\u200b\u200b\🐐 Rotaldo"

for poste in df_scores['Poste'].unique():
    mask = df_scores['Poste'] == poste
    vals = df_scores.loc[mask, '_regularite_brute']
    q25, q50, q75 = vals.quantile([0.25, 0.5, 0.75])
    df_scores.loc[mask, 'Régularité'] = df_scores.loc[mask, '_regularite_brute'].apply(
        lambda x: etiquette_regularite(x, q25, q50, q75)
    )

st.header("🏆 Recommandations par poste")

postes = {
    'A': '⚡ Attaquants',
    'MO': '🎯 Milieux Offensifs',
    'MD': '🛡️ Milieux Défensifs',
    'DC': '🔒 Défenseurs Centraux',
    'DL': '↔️ Défenseurs Latéraux',
    'G': '🧤 Gardiens'
}

colonnes_affichage = ['Joueur', 'Club', 'Note saison', 'Forme 6J', 'Régularité', '% Titulaire']

for code, nom in postes.items():
    st.subheader(nom)
    top = df_scores[df_scores['Poste'] == code].sort_values('_score', ascending=False)[colonnes_affichage]
    if len(top) > 0:
        st.dataframe(
            top.reset_index(drop=True),
            use_container_width=True,
            height=400
        )
    st.markdown("---")
