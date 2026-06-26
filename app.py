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

# Sidebar
st.sidebar.header("📁 Importer vos données")
fichier = st.sidebar.file_uploader(
    "Téléchargez le fichier MPGStats (xlsx)",
    type=['xlsx']
)

if fichier is None:
    st.info("👈 Commencez par importer votre fichier MPGStats dans le panneau gauche")
    st.stop()

# Chargement
@st.cache_data
def charger_donnees(fichier):
    df = pd.read_excel(fichier)
    return df

df = charger_donnees(fichier)
st.success(f"✅ {len(df)} joueurs chargés !")

# Nettoyage des notes
def nettoyer_note(valeur):
    if pd.isna(valeur):
        return 0
    valeur = str(valeur)
    valeur = valeur.replace('*', '').replace('(', '').replace(')', '').replace('J', '').strip()
    try:
        note = float(valeur.replace('.', ',') if ',' not in valeur else valeur)
        note = float(str(note).replace(',', '.'))
        if 0 <= note <= 10:
            return note
        return 0
    except:
        return 0

# Colonnes journées
cols_journees = [col for col in df.columns if str(col).startswith('D') and str(col)[1:].isdigit()]
cols_journees = sorted(cols_journees, key=lambda x: int(x[1:]), reverse=True)

for col in cols_journees:
    df[col] = df[col].apply(nettoyer_note)

# Poids 6J
poids_6j = [0.30, 0.23, 0.18, 0.14, 0.10, 0.05]

def predire(notes, poids):
    notes_jouees = [n for n in notes if n > 0]
    if len(notes_jouees) < len(poids):
        return None
    dernieres = notes_jouees[:len(poids)]
    return sum(note * poids[i] for i, note in enumerate(dernieres))

# Calcul des scores
scores = []
for idx, row in df.iterrows():
    notes = [row[col] for col in cols_journees]
    notes_jouees = [n for n in notes if n > 0]
    
    if len(notes_jouees) >= 6:
        six_derniers = notes_jouees[:6]
        moyenne = np.mean(six_derniers)
        ecart_type = np.std(six_derniers)
        regularite = 1 / (1 + ecart_type)
        prob_jouer = row['%Titu'] / 100 if '%Titu' in df.columns else 0.8
        moyenne_saison = row['Note'] if 'Note' in df.columns else moyenne
        
        score = (moyenne_saison * 0.5 +
                 moyenne * 0.3 +
                 regularite * 0.1 +
                 prob_jouer * 0.1)
        
        scores.append({
            'Joueur': row['Joueur'],
            'Poste': row['Poste'],
            'Club': row['Club'],
            'Note saison': round(float(moyenne_saison), 2),
            'Forme 6J': round(float(moyenne), 2),
            'Régularité': round(float(regularite), 2),
            '% Titulaire': f"{int(prob_jouer*100)}%",
            'Score': round(float(score), 2)
        })

df_scores = pd.DataFrame(scores)

# Affichage par poste
st.header("🏆 Recommandations par poste")

postes = {
    'A': '⚡ Attaquants',
    'MO': '🎯 Milieux Offensifs',
    'MD': '🛡️ Milieux Défensifs',
    'DC': '🔒 Défenseurs Centraux',
    'DL': '↔️ Défenseurs Latéraux',
    'G': '🧤 Gardiens'
}

for code, nom in postes.items():
    st.subheader(nom)
    top = df_scores[df_scores['Poste'] == code].sort_values('Score', ascending=False).head(10)
    if len(top) > 0:
        st.dataframe(top.reset_index(drop=True), use_container_width=True)
    st.markdown("---")
