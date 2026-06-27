import streamlit as st
import pandas as pd
import numpy as np
import copy
from modele import (nettoyer_note, calculer_clutch, compter_matchs,
                    absences_consecutives, predire_note, alerte_blessure,
                    get_joueur_info, poste_vers_ligne,
                    simuler_buts_mpg, appliquer_bonus)

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

    st.header("⚔️ Analyser mon adversaire")

    # Stratégie
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

        # Construire équipe depuis noms
        def construire_equipe_noms(noms_titu, noms_rempl):
            titu_info = []
            rempl_info = []
            for nom in [n.strip() for n in noms_titu.split('\n') if n.strip()]:
                info = get_joueur_info(nom, df, cols_journees)
                if info:
                    titu_info.append(info)
            for nom in [n.strip() for n in noms_rempl.split('\n') if n.strip()]:
                info = get_joueur_info(nom, df, cols_journees)
                if info:
                    rempl_info.append(info)
            return titu_info, rempl_info

        # Mon équipe
        titu_moi, rempl_moi = construire_equipe_noms(mes_titu, mes_remplacants)
        equipe_moi = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
        for j in titu_moi:
            ligne = poste_vers_ligne(j['poste'])
            equipe_moi[ligne].append(j)

        # Équipe adverse
        if "précise" in mode_analyse:
            titu_adv, rempl_adv = construire_equipe_noms(adv_titu, adv_remplacants)
            equipe_adv = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
            for j in titu_adv:
                ligne = poste_vers_ligne(j['poste'])
                equipe_adv[ligne].append(j)
        else:
            equipe_adv, _ = meilleure_compo(adv_joueurs, df, cols_journees, strategie_jeu)

        # Simulation de base
        buts_mpg_moi = simuler_buts_mpg(equipe_moi, equipe_adv, domicile=True)
        buts_mpg_adv = simuler_buts_mpg(equipe_adv, equipe_moi, domicile=False)

        buts_reels_moi = sum(j['buts'] for ligne in equipe_moi.values() for j in ligne)
        buts_reels_adv = sum(j['buts'] for ligne in equipe_adv.values() for j in ligne)

        arret_moi = (equipe_moi.get('GB') and
                     equipe_moi['GB'][0]['note_pred'] and
                     equipe_moi['GB'][0]['note_pred'] >= 8)
        arret_adv = (equipe_adv.get('GB') and
                     equipe_adv['GB'][0]['note_pred'] and
                     equipe_adv['GB'][0]['note_pred'] >= 8)

        if arret_moi:
            buts_reels_adv = max(0, buts_reels_adv - 1)
        if arret_adv:
            buts_reels_moi = max(0, buts_reels_moi - 1)

        score_moi = buts_reels_moi + len(buts_mpg_moi)
        score_adv = buts_reels_adv + len(buts_mpg_adv)

        # Affichage résultat
        st.subheader("📊 Résultat simulé")
        col_s1, col_s2, col_s3 = st.columns([2, 1, 2])

        with col_s1:
            st.metric("🔵 Mon équipe", f"{round(score_moi, 1)} buts")
            if buts_mpg_moi:
                st.success(f"⚽ Buts MPG : {', '.join(buts_mpg_moi)}")
            if arret_moi:
                st.info(f"🧤 Arrêt MPG de {equipe_moi['GB'][0]['nom']} !")

        with col_s2:
            diff = score_moi - score_adv
            if diff > 0:
                st.markdown("### 🏆 Victoire")
            elif diff < 0:
                st.markdown("### 😢 Défaite")
            else:
                st.markdown("### 🤝 Nul")

        with col_s3:
            st.metric("🔴 Adversaire", f"{round(score_adv, 1)} buts")
            if buts_mpg_adv:
                st.error(f"⚽ Buts MPG adverses : {', '.join(buts_mpg_adv)}")
            if arret_adv:
                st.warning("🧤 Arrêt MPG adverse possible !")

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
                        score_cap = (j['note_pred']/10)*0.5 + j['regularite']*0.3 + j['clutch_7']*0.2
                    candidats_cap.append((j['nom'], j['poste'], j['note_pred'], score_cap))

        if equipe_moi.get('GB') and equipe_moi['GB'][0]['clutch_8'] >= 0.10:
            gb = equipe_moi['GB'][0]
            if strategie_jeu == "🛡️ Défensive":
                candidats_cap.append((gb['nom'], 'G', gb['note_pred'], 999))

        if candidats_cap:
            meilleur = max(candidats_cap, key=lambda x: x[3])
            st.success(f"🎖️ **{meilleur[0]}** ({meilleur[1]}) — Note prédite : {meilleur[2]}")

        st.markdown("---")

        # ============================================================
        # GESTION DES BONUS
        # ============================================================

        st.subheader("🎯 Gestion des bonus")

        col_b1, col_b2 = st.columns(2)

        with col_b1:
            st.markdown("**Mes bonus disponibles**")
            mon_bonus = st.selectbox(
                "Bonus à utiliser ce match :",
                liste_bonus,
                key="mon_bonus"
            )
            joueur_uber = None
            if "Uber Eats" in mon_bonus:
                joueur_uber = st.selectbox(
                    "Choisir le joueur :",
                    [j['nom'] for ligne in equipe_moi.values()
                     for j in ligne if j['nom'] != 'Rotaldo'],
                    key="joueur_uber"
                )
            importance_match = st.radio(
                "Importance du match :",
                ["🔥 Crucial", "⚽ Normal", "😴 Sans enjeu"],
                horizontal=True,
                key="importance"
            )

        with col_b2:
            st.markdown("**Bonus adverses**")
            bonus_adv_utilises = st.multiselect(
                "Bonus déjà utilisés par l'adversaire :",
                [b for b in liste_bonus if b != "Aucun"],
                key="bonus_adv_utilises"
            )
            bonus_adv_restant = st.selectbox(
                "Bonus adverse probable ce match :",
                liste_bonus,
                key="bonus_adv_restant"
            )

        # Simulation sans bonus
        score_moi_sb = score_moi
        score_adv_sb = score_adv

        # Simulation avec mon bonus
        eq_moi_b, eq_adv_b, ann_adv, ann_moi = appliquer_bonus(
            equipe_moi, equipe_adv, mon_bonus, bonus_adv_restant, joueur_uber
        )
        buts_mpg_moi_ab = simuler_buts_mpg(eq_moi_b, eq_adv_b, domicile=True)
        buts_mpg_adv_ab = simuler_buts_mpg(eq_adv_b, eq_moi_b, domicile=False)
        score_moi_ab = max(0, buts_reels_moi + len(buts_mpg_moi_ab) - ann_moi)
        score_adv_ab = max(0, buts_reels_adv + len(buts_mpg_adv_ab) - ann_adv)

        st.markdown("---")
        st.subheader("📊 Analyse des bonus")

        col_sb, col_ab = st.columns(2)

        with col_sb:
            st.markdown("**Sans bonus**")
            diff_sb = score_moi_sb - score_adv_sb
            if diff_sb > 0:
                st.success(f"🔵 {round(score_moi_sb,1)} - {round(score_adv_sb,1)} 🔴 — Victoire")
            elif diff_sb < 0:
                st.error(f"🔵 {round(score_moi_sb,1)} - {round(score_adv_sb,1)} 🔴 — Défaite")
            else:
                st.warning(f"🔵 {round(score_moi_sb,1)} - {round(score_adv_sb,1)} 🔴 — Nul")

        with col_ab:
            if mon_bonus != "Aucun":
                st.markdown(f"**Avec {mon_bonus.split('—')[0].strip()}**")
                diff_ab = score_moi_ab - score_adv_ab
                if diff_ab > 0:
                    st.success(f"🔵 {round(score_moi_ab,1)} - {round(score_adv_ab,1)} 🔴 — Victoire")
                elif diff_ab < 0:
                    st.error(f"🔵 {round(score_moi_ab,1)} - {round(score_adv_ab,1)} 🔴 — Défaite")
                else:
                    st.warning(f"🔵 {round(score_moi_ab,1)} - {round(score_adv_ab,1)} 🔴 — Nul")

        # Recommandation finale
        st.markdown("---")
        st.subheader("🎯 Recommandation Gazon Stats")

        diff_sb = score_moi_sb - score_adv_sb
        diff_ab = score_moi_ab - score_adv_ab if mon_bonus != "Aucun" else diff_sb
        gain_bonus = diff_ab - diff_sb

        if diff_sb >= 2:
            st.success("✅ **N'utilisez PAS de bonus** — Victoire confortable. Économisez-le !")
        elif diff_sb >= 1:
            if importance_match == "🔥 Crucial":
                if mon_bonus != "Aucun" and gain_bonus > 0:
                    st.success(f"✅ **Utilisez {mon_bonus.split('—')[0].strip()}** — Match crucial !")
                else:
                    st.info("💡 **Victoire probable** — Bonus non indispensable")
            else:
                st.success("✅ **N'utilisez PAS de bonus** — Gardez-le pour un match serré !")
        elif diff_sb == 0:
            if mon_bonus != "Aucun" and gain_bonus > 0:
                st.warning(f"⚠️ **Utilisez {mon_bonus.split('—')[0].strip()}** — Peut faire la différence !")
            else:
                st.warning("⚠️ **Match serré** — Envisagez Zahia ou Cheat Code")
        elif diff_sb == -1:
            if mon_bonus != "Aucun" and gain_bonus >= 1:
                st.warning(f"⚠️ **Utilisez {mon_bonus.split('—')[0].strip()}** — Peut renverser la situation !")
            else:
                st.error("❌ **Défaite probable** — Utilisez votre meilleur bonus offensif")
        else:
            st.error("❌ **Défaite probable** — Utilisez un bonus ou économisez pour plus tard")

        if bonus_adv_restant != "Aucun":
            st.info(f"🪞 **Attention** — L'adversaire a encore {bonus_adv_restant.split('—')[0].strip()} disponible !")
        if any("Miroir" in b for b in [bonus_adv_restant]):
            st.warning("🪞 **L'adversaire a le Miroir !** — Prudence si vous utilisez un bonus !")

        # Détails équipes
        st.markdown("---")
        col_eq1, col_eq2 = st.columns(2)

        with col_eq1:
            st.subheader("🔵 Mon équipe")
            for ligne in ['GB', 'DEF', 'MIL', 'ATT']:
                for j in equipe_moi.get(ligne, []):
                    note = f"{j['note_pred']:.2f}" if j['note_pred'] else "?"
                    alerte = f" {j['alerte']}" if j['alerte'] else ""
                    clutch = f" | Clutch: {j['clutch_7']*100:.0f}%"
                    st.write(f"**{ligne}** | {j['nom']} — {note}{clutch}{alerte}")

        with col_eq2:
            st.subheader("🔴 Équipe adverse")
            for ligne in ['GB', 'DEF', 'MIL', 'ATT']:
                for j in equipe_adv.get(ligne, []):
                    note = f"{j['note_pred']:.2f}" if j['note_pred'] else "?"
                    alerte = f" {j['alerte']}" if j['alerte'] else ""
                    rotaldo = " ⚠️ Rotaldo probable !" if not j['note_pred'] or j['note_pred'] < 3 else ""
                    st.write(f"**{ligne}** | {j['nom']} — {note}{alerte}{rotaldo}")
