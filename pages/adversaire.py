import streamlit as st
import pandas as pd
import numpy as np
import copy
from modele import (nettoyer_note, calculer_clutch, compter_matchs,
                    absences_consecutives, predire_note, alerte_blessure,
                    get_joueur_info, poste_vers_ligne,
                    simuler_buts_mpg, appliquer_bonus)

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

    # ============================================================
    # STRATÉGIE ET MODE
    # ============================================================

    st.subheader("🎯 Votre stratégie")
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

    st.markdown("---")

    # ============================================================
    # SAISIE DES ÉQUIPES
    # ============================================================

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
                placeholder="Descamps\nChardonnet\nDiomandé\nUdol\nGboho\nAndré\nSinayoko\nLepaul",
                height=400,
                key="adv_joueurs"
            )

    st.markdown("---")

    # ============================================================
    # CONFIGURATION BONUS — AVANT SIMULATION
    # ============================================================

    st.subheader("🎯 Configuration des bonus")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("**Mes bonus encore disponibles**")
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
        st.markdown("**Bonus adverses**")
        bonus_adv_utilises = st.multiselect(
            "Bonus déjà utilisés par l'adversaire :",
            liste_bonus,
            key="bonus_adv_utilises"
        )
        bonus_adv_restant = st.selectbox(
            "Bonus adverse probable ce match :",
            ["Aucun"] + liste_bonus,
            key="bonus_adv_restant"
        )

    st.markdown("---")

    # ============================================================
    # BOUTON SIMULATION
    # ============================================================

    if st.button("🚀 Lancer la simulation", type="primary"):

        def construire_equipe_noms(noms_titu, noms_rempl=""):
            titu_info = []
            for nom in [n.strip() for n in noms_titu.split('\n') if n.strip()]:
                info = get_joueur_info(nom, df, cols_journees)
                if info:
                    titu_info.append(info)
            return titu_info

        # Mon équipe
        titu_moi = construire_equipe_noms(mes_titu, mes_remplacants)
        equipe_moi = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
        for j in titu_moi:
            equipe_moi[poste_vers_ligne(j['poste'])].append(j)

        # Équipe adverse
        if "précise" in mode_analyse:
            titu_adv = construire_equipe_noms(adv_titu)
            equipe_adv = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
            for j in titu_adv:
                equipe_adv[poste_vers_ligne(j['poste'])].append(j)
        else:
            equipe_adv, _ = meilleure_compo(
                adv_joueurs, df, cols_journees, strategie_jeu
            )

        # ============================================================
        # SIMULATION SANS BONUS
        # ============================================================

        buts_mpg_moi = simuler_buts_mpg(equipe_moi, equipe_adv, domicile=True)
        buts_mpg_adv = simuler_buts_mpg(equipe_adv, equipe_moi, domicile=False)
        buts_reels_moi = sum(j['buts'] for ligne in equipe_moi.values() for j in ligne)
        buts_reels_adv = sum(j['buts'] for ligne in equipe_adv.values() for j in ligne)

        arret_moi = (equipe_moi.get('GB') and equipe_moi['GB'] and
                     equipe_moi['GB'][0]['note_pred'] and
                     equipe_moi['GB'][0]['note_pred'] >= 8)
        arret_adv = (equipe_adv.get('GB') and equipe_adv['GB'] and
                     equipe_adv['GB'][0]['note_pred'] and
                     equipe_adv['GB'][0]['note_pred'] >= 8)

        if arret_moi:
            buts_reels_adv = max(0, buts_reels_adv - 1)
        if arret_adv:
            buts_reels_moi = max(0, buts_reels_moi - 1)

        score_moi = round(buts_reels_moi + len(buts_mpg_moi), 1)
        score_adv = round(buts_reels_adv + len(buts_mpg_adv), 1)
        diff_sb = round(score_moi - score_adv, 1)

        # ============================================================
        # TEST AUTOMATIQUE DE TOUS LES BONUS
        # ============================================================

        resultats_bonus = {}
        for bonus in mes_bonus_dispo:
            j_uber = joueur_uber if "Uber Eats" in bonus else None
            eq_m_b, eq_a_b, ann_a, ann_m = appliquer_bonus(
                equipe_moi, equipe_adv, bonus, bonus_adv_restant, j_uber
            )
            mpg_m = simuler_buts_mpg(eq_m_b, eq_a_b, domicile=True)
            mpg_a = simuler_buts_mpg(eq_a_b, eq_m_b, domicile=False)
            s_m = round(max(0, buts_reels_moi + len(mpg_m) - ann_m), 1)
            s_a = round(max(0, buts_reels_adv + len(mpg_a) - ann_a), 1)
            resultats_bonus[bonus] = {
                'score_moi': s_m,
                'score_adv': s_a,
                'diff': round(s_m - s_a, 1),
                'gain': round((s_m - s_a) - diff_sb, 1)
            }

        # ============================================================
        # AFFICHAGE RÉSULTAT SANS BONUS
        # ============================================================

        st.subheader("📊 Résultat simulé — Sans bonus")
        col_s1, col_s2, col_s3 = st.columns([2, 1, 2])

        with col_s1:
            st.metric("🔵 Mon équipe", f"{score_moi} buts")
            if buts_mpg_moi:
                st.success(f"⚽ Buts MPG : {', '.join(buts_mpg_moi)}")
            if arret_moi:
                st.info(f"🧤 Arrêt MPG de {equipe_moi['GB'][0]['nom']} !")

        with col_s2:
            if diff_sb > 0:
                st.markdown("### 🏆 Victoire")
            elif diff_sb < 0:
                st.markdown("### 😢 Défaite")
            else:
                st.markdown("### 🤝 Nul")

        with col_s3:
            st.metric("🔴 Adversaire", f"{score_adv} buts")
            if buts_mpg_adv:
                st.error(f"⚽ Buts MPG adverses : {', '.join(buts_mpg_adv)}")
            if arret_adv:
                st.warning("🧤 Arrêt MPG adverse possible !")

        # ============================================================
        # RECOMMANDATION CAPITAINE
        # ============================================================

        st.markdown("---")
        st.subheader("🎖️ Recommandation capitaine")
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
            meilleur = max(candidats_cap, key=lambda x: x[3])
            st.success(f"🎖️ **{meilleur[0]}** ({meilleur[1]}) — Note prédite : {meilleur[2]}")

        # ============================================================
        # RECOMMANDATION BONUS
        # ============================================================

        st.markdown("---")
        st.subheader("🎯 Recommandation Gazon Stats")

        if resultats_bonus:
            st.markdown("**Impact de chaque bonus disponible :**")
            for bonus, res in sorted(
                resultats_bonus.items(),
                key=lambda x: x[1]['diff'],
                reverse=True
            ):
                nom_bonus = bonus.split('—')[0].strip()
                s_m = res['score_moi']
                s_a = res['score_adv']
                gain = res['gain']
                diff = res['diff']

                if diff > 0:
                    emoji = "✅"
                    label = "Victoire"
                elif diff == 0:
                    emoji = "🤝"
                    label = "Nul"
                else:
                    emoji = "❌"
                    label = "Défaite"

                gain_str = f"+{gain}" if gain > 0 else str(gain)
                st.write(f"{emoji} **{nom_bonus}** → {s_m}-{s_a} {label} ({gain_str} but)")

            # Meilleur bonus
            meilleur_bonus = max(resultats_bonus.items(), key=lambda x: x[1]['diff'])
            nom_meilleur = meilleur_bonus[0].split('—')[0].strip()
            res_meilleur = meilleur_bonus[1]

            st.markdown("---")

            if diff_sb >= 1.5:
                st.success(
                    f"✅ **N'utilisez PAS de bonus** — Victoire confortable {score_moi}-{score_adv} "
                    f"sans bonus. Économisez-le pour un match plus serré !"
                )
            elif diff_sb >= 0.5:
                if importance_match == "🔥 Crucial":
                    st.success(
                        f"✅ **Utilisez {nom_meilleur}** — Match crucial, "
                        f"passe à {res_meilleur['score_moi']}-{res_meilleur['score_adv']} !"
                    )
                else:
                    st.success(
                        f"✅ **N'utilisez PAS de bonus** — Victoire probable {score_moi}-{score_adv}. "
                        f"Gardez votre bonus pour un match plus serré !"
                    )
            elif diff_sb >= 0:
                if res_meilleur['diff'] > 0:
                    st.warning(
                        f"⚠️ **Utilisez {nom_meilleur}** — Match nul prévu ({score_moi}-{score_adv}), "
                        f"le bonus fait passer à {res_meilleur['score_moi']}-{res_meilleur['score_adv']} !"
                    )
                else:
                    st.warning(
                        f"⚠️ **Match très serré {score_moi}-{score_adv}** — "
                        f"Aucun de vos bonus ne change le résultat. Économisez-les !"
                    )
            elif diff_sb >= -1:
                if res_meilleur['diff'] >= 0:
                    st.warning(
                        f"⚠️ **Utilisez {nom_meilleur}** — "
                        f"Peut renverser {score_moi}-{score_adv} "
                        f"en {res_meilleur['score_moi']}-{res_meilleur['score_adv']} !"
                    )
                else:
                    st.error(
                        f"❌ **Défaite probable {score_moi}-{score_adv}** — "
                        f"Aucun bonus ne suffit. Économisez-les !"
                    )
            else:
                st.error(
                    f"❌ **Défaite difficile {score_moi}-{score_adv}** — "
                    f"Économisez vos bonus pour des matchs plus abordables !"
                )

        else:
            # Pas de bonus disponibles
            if diff_sb >= 1.5:
                st.success(f"✅ Victoire confortable {score_moi}-{score_adv} — Pas besoin de bonus !")
            elif diff_sb >= 0.5:
                st.success(f"✅ Victoire probable {score_moi}-{score_adv} !")
            elif diff_sb >= 0:
                st.warning(f"⚠️ Match très serré {score_moi}-{score_adv} !")
            elif diff_sb >= -1:
                st.error(f"❌ Défaite probable {score_moi}-{score_adv} !")
            else:
                st.error(f"❌ Défaite difficile {score_moi}-{score_adv} !")

        # Alerte Miroir adverse
        if bonus_adv_restant != "Aucun":
            st.info(
                f"⚠️ L'adversaire a encore "
                f"{bonus_adv_restant.split('—')[0].strip()} — "
                f"Vérifiez sur MPGStats !"
            )
        if "Miroir" in bonus_adv_restant:
            st.warning(
                "🪞 **L'adversaire a le Miroir !** — "
                "Si vous utilisez un bonus, il peut le retourner contre vous !"
            )

        # ============================================================
        # DÉTAILS ÉQUIPES
        # ============================================================

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
