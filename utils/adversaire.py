import streamlit as st
import pandas as pd
import numpy as np
from modele import (get_joueur_info, poste_vers_ligne,
                    monte_carlo_match, get_stats_joueur_mc)

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

/* ── Titres ── */
h1, h2, h3 {
    color: var(--mt-blanc) !important;
    letter-spacing: 0.05em;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label {
    color: var(--mt-blanc) !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] div {
    border-color: var(--mt-or) !important;
}

/* ── Text areas ── */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background-color: var(--mt-card) !important;
    color: var(--mt-blanc) !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: var(--mt-or) !important;
    box-shadow: 0 0 0 1px var(--mt-or) !important;
}

/* ── Labels ── */
label, [data-testid="stWidgetLabel"] {
    color: var(--mt-blanc) !important;
}

/* ── Multiselect ── */
[data-baseweb="select"] {
    background-color: var(--mt-card) !important;
    border-color: #2a2a2a !important;
}
[data-baseweb="select"] [data-baseweb="tag"] {
    background-color: var(--mt-or-fonce) !important;
    color: var(--mt-blanc) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: var(--mt-card) !important;
    color: var(--mt-blanc) !important;
    border-color: #2a2a2a !important;
}

/* ── Bouton principal ── */
[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--mt-or), var(--mt-or-fonce)) !important;
    color: #0d0d0d !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.6rem !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    opacity: 0.88 !important;
}

/* ── Colonnes équipe (cards) ── */
[data-testid="column"] {
    background-color: var(--mt-card);
    border-radius: 8px;
    border-left: 3px solid;
    border-image: linear-gradient(to bottom, var(--mt-or), var(--mt-or-fonce)) 1;
    padding: 12px 16px;
}

/* ── Métriques ── */
[data-testid="stMetric"] {
    background-color: var(--mt-card) !important;
    border-radius: 8px;
    padding: 12px 16px;
    border-left: 3px solid var(--mt-or);
}
[data-testid="stMetricLabel"] {
    color: var(--mt-gris) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: var(--mt-or) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ── Success / Warning / Error / Info ── */
[data-testid="stSuccess"] {
    background-color: #0d1f0d !important;
    border-left: 3px solid #4caf50 !important;
    color: var(--mt-blanc) !important;
    border-radius: 0 6px 6px 0;
}
[data-testid="stWarning"] {
    background-color: var(--mt-card) !important;
    border-left: 3px solid var(--mt-or) !important;
    color: var(--mt-blanc) !important;
    border-radius: 0 6px 6px 0;
}
[data-testid="stError"] {
    background-color: #1f0d0d !important;
    border-left: 3px solid #e53935 !important;
    color: var(--mt-blanc) !important;
    border-radius: 0 6px 6px 0;
}
[data-testid="stInfo"] {
    background-color: var(--mt-card) !important;
    border-left: 3px solid var(--mt-or) !important;
    color: var(--mt-blanc) !important;
    border-radius: 0 6px 6px 0;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p {
    color: var(--mt-or) !important;
}

/* ── Séparateur ── */
hr {
    border: none;
    border-top: 1px solid #2a2a2a !important;
    margin: 1.5rem 0;
}

/* ── Texte général ── */
p, li, span {
    color: var(--mt-blanc) !important;
}
strong {
    color: var(--mt-or) !important;
}
</style>
"""

def _separateur(titre):
    """Filet fin avec titre centré en or — signature Maestro Tactico."""
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

liste_bonus = [
    "💼 Valise à Nanard — annule 1 but adverse",
    "🪞 Miroir — retourne le bonus adverse",
    "💃 Zahia — +1 à tous mes joueurs",
    "🦷 Suarez — -1 au gardien adverse",
    "👊 Tonton Pat' — annule remplacements adverses",
    "🟥 Chapron Rouge — retire 1 joueur adverse au hasard",
    "💻 Cheat Code — -0.5 à tous joueurs adverses",
    "🍔 Uber Eats — +1 à un joueur choisi",
]

bonus_key_map = {
    "💼 Valise à Nanard — annule 1 but adverse": "valise",
    "🪞 Miroir — retourne le bonus adverse": "miroir",
    "💃 Zahia — +1 à tous mes joueurs": "zahia",
    "🦷 Suarez — -1 au gardien adverse": "suarez",
    "👊 Tonton Pat' — annule remplacements adverses": "tonton",
    "🟥 Chapron Rouge — retire 1 joueur adverse au hasard": "chapron",
    "💻 Cheat Code — -0.5 à tous joueurs adverses": "cheat_code",
    "🍔 Uber Eats — +1 à un joueur choisi": "uber_eats",
    "Aucun": None,
}

def meilleure_compo(noms_joueurs, df, cols_journees, strategie):
    joueurs_info = []
    for nom in [n.strip() for n in noms_joueurs.split('\n') if n.strip()]:
        info = get_joueur_info(nom, df, cols_journees)
        if info and info['note_pred'] is not None:
            joueurs_info.append(info)

    if strategie == "🗡️ Offensive":
        joueurs_info.sort(key=lambda x: x['clutch_7'], reverse=True)
    elif strategie == "🛡️ Défensive":
        joueurs_info.sort(key=lambda x: x['regularite'], reverse=True)
    else:
        joueurs_info.sort(key=lambda x: x['note_pred'] or 0, reverse=True)

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

def afficher_adversaire(df, cols_journees):

    # Injection CSS identité visuelle
    st.markdown(MT_CSS, unsafe_allow_html=True)

    # ── Titre principal ───────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="color:#ffffff;letter-spacing:0.08em;margin-bottom:0.2rem;">
        ⚔️ Analyser mon adversaire
    </h1>
    """, unsafe_allow_html=True)

    _separateur("STRATÉGIE")

    strategie_jeu = st.radio(
        "Choisissez votre stratégie :",
        ["🗡️ Offensive", "⚖️ Équilibrée", "🛡️ Défensive"],
        horizontal=True,
        key="strategie_jeu"
    )

    mode_analyse = st.radio(
        "Mode d'analyse :",
        ["🔮 Analyse préventive (avant match)", "🎯 Analyse précise (compo connue)"],
        horizontal=True,
        key="mode_analyse"
    )

    _separateur("COMPOSITIONS")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p style="color:#c8a84b;font-weight:700;letter-spacing:0.06em;">🔵 MON ÉQUIPE</p>', unsafe_allow_html=True)
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
        st.markdown('<p style="color:#c8a84b;font-weight:700;letter-spacing:0.06em;">🔴 ÉQUIPE ADVERSE</p>', unsafe_allow_html=True)
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
                placeholder="Descamps\nChardonnet\nDiomandé\nUdol\nGboho\nAndré\nSinayoko\nLepaul",
                height=400,
                key="adv_joueurs"
            )

    _separateur("CONFIGURATION DES BONUS")

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown('<p style="color:#c8a84b;font-weight:600;">Mes bonus encore disponibles</p>', unsafe_allow_html=True)
        mes_bonus_dispo = st.multiselect(
            "Cochez vos bonus disponibles :",
            liste_bonus,
            key="mes_bonus_dispo"
        )
        joueur_uber = None
        if any("Uber Eats" in b for b in mes_bonus_dispo):
            joueur_uber = st.text_input(
                "Joueur boosté par Uber Eats :",
                key="joueur_uber"
            )
        importance_match = st.radio(
            "Importance du match :",
            ["🔥 Crucial", "⚽ Normal", "😴 Sans enjeu"],
            horizontal=True,
            key="importance"
        )

    with col_b2:
        st.markdown('<p style="color:#c8a84b;font-weight:600;">Bonus adverses</p>', unsafe_allow_html=True)
        bonus_adv_utilises = st.multiselect(
            "Bonus encore disponibles chez l'adversaire :",
            liste_bonus,
            key="bonus_adv_utilises"
        )
        bonus_adv_restant = st.selectbox(
            "Bonus adverse que vous craignez ce match :",
            ["Aucun"] + liste_bonus,
            key="bonus_adv_restant"
        )

    _separateur("TERRAIN")

    domicile = st.radio(
        "Vous jouez :",
        ["🏠 À domicile", "✈️ À l'extérieur"],
        horizontal=True,
        key="domicile"
    ) == "🏠 À domicile"

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Lancer la simulation", type="primary"):

        def construire_equipe_noms(noms_titu):
            titu_info = []
            non_trouves = []
            for nom in [n.strip() for n in noms_titu.split('\n') if n.strip()]:
                info = get_joueur_info(nom, df, cols_journees)
                if info:
                    titu_info.append(info)
                else:
                    non_trouves.append(nom)
            return titu_info, non_trouves

        # Mon équipe
        titu_moi, non_trouves_moi = construire_equipe_noms(mes_titu)
        equipe_moi = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
        for j in titu_moi:
            equipe_moi[poste_vers_ligne(j['poste'])].append(j)

        # Équipe adverse
        non_trouves_adv = []
        if "précise" in mode_analyse:
            titu_adv, non_trouves_adv = construire_equipe_noms(adv_titu)
            equipe_adv = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
            for j in titu_adv:
                equipe_adv[poste_vers_ligne(j['poste'])].append(j)
        else:
            equipe_adv, _ = meilleure_compo(
                adv_joueurs, df, cols_journees, strategie_jeu
            )

        # Alertes joueurs non trouvés
        if non_trouves_moi:
            st.warning(f"⚠️ Joueurs non trouvés (mon équipe) : {', '.join(non_trouves_moi)}")
        if non_trouves_adv:
            st.warning(f"⚠️ Joueurs non trouvés (adversaire) : {', '.join(non_trouves_adv)}")

        # Convertir en format simulation
        def equipe_vers_mc(equipe):
            joueurs_mc = []
            for ligne, joueurs in equipe.items():
                for j in joueurs:
                    row = df[df['Joueur'].str.lower() == j['nom'].lower()]
                    if len(row) > 0:
                        row = row.iloc[0]
                        notes = [row[col] for col in cols_journees if row[col] > 0]
                        if len(notes) >= 3:
                            buts = pd.to_numeric(row.get('Buts', 0), errors='coerce')
                            matchs = len(notes)
                            buts_par_match = buts / matchs if matchs > 0 and not pd.isna(buts) else 0
                            joueurs_mc.append({
                                'nom': j['nom'],
                                'ligne': ligne,
                                'moyenne': float(np.mean(notes)),
                                'ecart_type': float(np.std(notes)),
                                'buts': float(buts_par_match)
                            })
                            continue
                    joueurs_mc.append({
                        'nom': j['nom'],
                        'ligne': ligne,
                        'moyenne': j['note_pred'] or 5.0,
                        'ecart_type': 1.0,
                        'buts': j['buts']
                    })
            return joueurs_mc

        joueurs_moi_mc = equipe_vers_mc(equipe_moi)
        joueurs_adv_mc = equipe_vers_mc(equipe_adv)

        bonus_adv_key = bonus_key_map.get(bonus_adv_restant, None)

        # Simulation
        with st.spinner("🔄 Simulation en cours (500 scénarios)..."):
            res_sb = monte_carlo_match(
                joueurs_moi_mc, joueurs_adv_mc,
                n_simulations=500,
                domicile=domicile
            )

        _separateur("📊 RÉSULTAT — 500 SCÉNARIOS")

        col_s1, col_s2, col_s3 = st.columns([2, 1, 2])

        with col_s1:
            st.metric("🏆 Victoire", f"{res_sb['victoires']}%")
            st.metric("🤝 Nul", f"{res_sb['nuls']}%")
            st.metric("😢 Défaite", f"{res_sb['defaites']}%")

        with col_s2:
            if res_sb['victoires'] > 50:
                st.markdown('<p style="color:#c8a84b;font-size:1.4rem;font-weight:700;">🏆 Favori</p>', unsafe_allow_html=True)
            elif res_sb['victoires'] > 40:
                st.markdown('<p style="color:#c8a84b;font-size:1.4rem;font-weight:700;">⚖️ Serré</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#555555;font-size:1.4rem;font-weight:700;">😢 Outsider</p>', unsafe_allow_html=True)

        with col_s3:
            st.metric("Score moyen prévu",
                     f"{res_sb['score_moy_moi']} - {res_sb['score_moy_adv']}")

        _separateur("🎖️ RECOMMANDATION CAPITAINE")

        candidats_cap = []
        for ligne, joueurs in equipe_moi.items():
            if ligne == 'GB':
                continue
            for j in joueurs:
                if j['note_pred'] is not None:
                    if strategie_jeu == "🗡️ Offensive":
                        score_cap = j['clutch_7']*0.6 + (j['note_pred']/10)*0.4
                    elif strategie_jeu == "🛡️ Défensive":
                        score_cap = j['regularite']*0.6 + (j['note_pred']/10)*0.4
                    else:
                        score_cap = (j['note_pred']/10)*0.5 + j['regularite']*0.3 + j['clutch_7']*0.2
                    candidats_cap.append((j['nom'], j['poste'], j['note_pred'], score_cap))

        if equipe_moi.get('GB') and equipe_moi['GB']:
            gb = equipe_moi['GB'][0]
            if gb.get('clutch_8', 0) >= 0.10 and strategie_jeu == "🛡️ Défensive":
                candidats_cap.append((gb['nom'], 'G', gb['note_pred'], 999))

        if candidats_cap:
            meilleur_cap = max(candidats_cap, key=lambda x: x[3])
            st.success(f"🎖️ **{meilleur_cap[0]}** ({meilleur_cap[1]}) — Note prédite : {meilleur_cap[2]}")

        _separateur("🎯 RECOMMANDATION MAESTRO TACTICO")

        if mes_bonus_dispo:
            st.markdown('<p style="color:#c8a84b;font-weight:600;">Impact de chaque bonus disponible :</p>', unsafe_allow_html=True)

            resultats_bonus = {}
            with st.spinner("🔄 Test des bonus en cours..."):
                for bonus in mes_bonus_dispo:
                    bonus_key = bonus_key_map.get(bonus, None)
                    res_b = monte_carlo_match(
                        joueurs_moi_mc, joueurs_adv_mc,
                        n_simulations=200,
                        bonus_moi=bonus_key,
                        bonus_adv=bonus_adv_key,
                        domicile=domicile,
                        joueur_uber=joueur_uber
                    )
                    resultats_bonus[bonus] = res_b

            for bonus, res in sorted(
                resultats_bonus.items(),
                key=lambda x: x[1]['victoires'],
                reverse=True
            ):
                nom_bonus = bonus.split('—')[0].strip()
                gain = round(res['victoires'] - res_sb['victoires'], 1)
                gain_str = f"+{gain}%" if gain > 0 else f"{gain}%"
                if res['victoires'] > 50:
                    emoji = "✅"
                elif res['victoires'] > 40:
                    emoji = "⚖️"
                else:
                    emoji = "❌"
                st.write(
                    f"{emoji} **{nom_bonus}** → "
                    f"🏆 {res['victoires']}% victoire ({gain_str}) | "
                    f"Score: {res['score_moy_moi']}-{res['score_moy_adv']}"
                )

            meilleur = max(resultats_bonus.items(), key=lambda x: x[1]['victoires'])
            nom_meilleur = meilleur[0].split('—')[0].strip()
            res_meilleur = meilleur[1]

            st.markdown("---")

            vic = res_sb['victoires']

            if vic >= 65:
                st.success(f"✅ **Gardez vos bonus** — Vous êtes largement favori ({vic}%). Économisez pour un match plus serré !")
            elif vic >= 50:
                if importance_match == "🔥 Crucial":
                    st.success(f"✅ **Utilisez {nom_meilleur}** — Match crucial, passe à {res_meilleur['victoires']}% de victoire !")
                else:
                    st.success(f"✅ **Gardez vos bonus** — Favori à {vic}%, bonus non indispensable !")
            elif vic >= 40:
                if round(res_meilleur['victoires'] - vic, 1) >= 10:
                    st.warning(f"⚠️ **Utilisez {nom_meilleur}** — Match serré ({vic}%), le bonus fait passer à {res_meilleur['victoires']}% !")
                else:
                    st.warning(f"⚠️ **Match très serré ({vic}%)** — Aucun bonus ne change significativement le résultat")
            elif vic >= 30:
                if res_meilleur['victoires'] >= 50:
                    st.warning(f"⚠️ **Utilisez {nom_meilleur}** — Peut renverser la situation ({vic}% → {res_meilleur['victoires']}%) !")
                else:
                    st.error(f"❌ **Défaite probable ({vic}%)** — Aucun bonus ne suffit. Économisez-les !")
            else:
                st.error(f"❌ **Défaite très probable ({vic}%)** — N'utilisez aucun bonus, gardez-les pour un match gagnable !")

        else:
            vic = res_sb['victoires']
            if vic >= 65:
                st.success(f"✅ Largement favori ({vic}%) — Pas besoin de bonus !")
            elif vic >= 50:
                st.success(f"✅ Favori ({vic}%) — Victoire probable !")
            elif vic >= 40:
                st.warning(f"⚠️ Match serré ({vic}%) — Envisagez d'utiliser un bonus !")
            elif vic >= 30:
                st.error(f"❌ Outsider ({vic}%) — Utilisez un bonus si disponible !")
            else:
                st.error(f"❌ Très outsider ({vic}%) — Économisez vos bonus !")

        if bonus_adv_restant != "Aucun":
            st.info(f"⚠️ L'adversaire a encore {bonus_adv_restant.split('—')[0].strip()} — Vérifiez sur MPGStats !")
        if "Miroir" in bonus_adv_restant:
            st.warning("🪞 **L'adversaire a le Miroir !** — Si vous utilisez un bonus, il peut le retourner contre vous !")

        _separateur("DÉTAILS DES ÉQUIPES")

        col_eq1, col_eq2 = st.columns(2)

        with col_eq1:
            st.markdown('<p style="color:#c8a84b;font-weight:700;letter-spacing:0.06em;">🔵 MON ÉQUIPE</p>', unsafe_allow_html=True)
            for ligne in ['GB', 'DEF', 'MIL', 'ATT']:
                for j in equipe_moi.get(ligne, []):
                    note = f"{j['note_pred']:.2f}" if j['note_pred'] else "?"
                    alerte = f" {j['alerte']}" if j['alerte'] else ""
                    clutch = f" | Clutch: {j['clutch_7']*100:.0f}%"
                    st.write(f"**{ligne}** | {j['nom']} — {note}{clutch}{alerte}")

        with col_eq2:
            st.markdown('<p style="color:#c8a84b;font-weight:700;letter-spacing:0.06em;">🔴 ÉQUIPE ADVERSE</p>', unsafe_allow_html=True)
            for ligne in ['GB', 'DEF', 'MIL', 'ATT']:
                for j in equipe_adv.get(ligne, []):
                    note = f"{j['note_pred']:.2f}" if j['note_pred'] else "?"
                    alerte = f" {j['alerte']}" if j['alerte'] else ""
                    rotaldo = " ⚠️ Rotaldo probable !" if not j['note_pred'] or j['note_pred'] < 3 else ""
                    st.write(f"**{ligne}** | {j['nom']} — {note}{alerte}{rotaldo}")
