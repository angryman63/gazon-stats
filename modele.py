# ============================================================
# GAZON STATS — MODÈLE COMPLET
# ============================================================

import pandas as pd
import numpy as np

# ============================================================
# 1. NETTOYAGE DES NOTES
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

# ============================================================
# 2. MODÈLE PRÉDICTIF 6J
# ============================================================

poids_6j = [0.30, 0.23, 0.18, 0.14, 0.10, 0.05]

def predire(notes, poids):
    notes_jouees = [n for n in notes if n > 0]
    if len(notes_jouees) < len(poids):
        return None
    dernieres = notes_jouees[:len(poids)]
    return sum(note * poids[i] for i, note in enumerate(dernieres))

def predire_note_j(id_joueur, col_cible, df_l1):
    nom = nom_depuis_id(id_joueur)
    club = club_depuis_id(id_joueur)
    row = df_l1[
        (df_l1['Joueur'].str.lower() == nom.lower()) &
        (df_l1['Club'].str.lower() == club.lower())
    ]
    if len(row) == 0:
        return None
    j_num = int(col_cible[1:])
    cols_prec = [f'D{j_num - i}' for i in range(1, 7) if f'D{j_num - i}' in df_l1.columns]
    notes = []
    for col in cols_prec:
        note = nettoyer_note(row[col].values[0])
        if note > 0:
            notes.append(note)
    if len(notes) < 3:
        return None
    total_poids = sum(poids_6j[:len(notes)])
    return round(sum(n * poids_6j[i] for i, n in enumerate(notes)) / total_poids, 2)

# ============================================================
# 3. BACKTESTING
# ============================================================

def backtesting_championnat(nom, fichier):
    print(f"\n=== {nom} ===")
    df_champ = pd.read_excel(fichier)
    cols_j = [col for col in df_champ.columns if str(col).startswith('D') and str(col)[1:].isdigit()]
    cols_j = sorted(cols_j, key=lambda x: int(x[1:]), reverse=True)
    for col in cols_j:
        df_champ[col] = df_champ[col].apply(nettoyer_note)
    print(f"Joueurs : {len(df_champ)} | Journées : {len(cols_j)}")
    resultats = []
    for idx, row in df_champ.iterrows():
        notes = [row[col] for col in cols_j]
        notes_jouees = [n for n in notes if n > 0]
        for i in range(6, len(notes_jouees)):
            note_reelle = notes_jouees[i]
            pred_6j = predire(notes_jouees[i-6:i][::-1], poids_6j)
            if pred_6j is not None:
                resultats.append({
                    'Note_reelle': note_reelle,
                    'Pred_6J': pred_6j
                })
    df_res = pd.DataFrame(resultats)
    erreur = (df_res['Note_reelle'] - df_res['Pred_6J']).abs().mean()
    erreur_moyenne = df_res['Note_reelle'].apply(
        lambda x: abs(x - df_res['Note_reelle'].mean())
    ).mean()
    print(f"Prédictions : {len(df_res)}")
    print(f"Erreur modèle 6J : {erreur:.3f}")
    print(f"Erreur si on prédit toujours la moyenne : {erreur_moyenne:.3f}")
    print(f"Amélioration vs moyenne : {(erreur_moyenne - erreur):.3f}")
    return erreur, len(df_res)

# ============================================================
# 4. UTILITAIRES JOUEURS
# ============================================================

def nom_depuis_id(id_joueur):
    return '_'.join(id_joueur.split('_')[:-1])

def club_depuis_id(id_joueur):
    return id_joueur.split('_')[-1]

def get_note_id(id_joueur, col, df_brut):
    nom = nom_depuis_id(id_joueur)
    club = club_depuis_id(id_joueur)
    row = df_brut[
        (df_brut['Joueur'].str.lower() == nom.lower()) &
        (df_brut['Club'].str.lower() == club.lower())
    ]
    if len(row) == 0:
        return None, 0
    val = str(row[col].values[0])
    buts = val.count('*') if '*' in val and '(' not in val else 0
    note = nettoyer_note(val)
    return note if note > 0 else None, buts

def buts_attendus_id(id_joueur, df_l1):
    nom = nom_depuis_id(id_joueur)
    club = club_depuis_id(id_joueur)
    row = df_l1[
        (df_l1['Joueur'].str.lower() == nom.lower()) &
        (df_l1['Club'].str.lower() == club.lower())
    ]
    if len(row) == 0:
        return 0
    buts = pd.to_numeric(row['Buts'].values[0], errors='coerce')
    matchs = sum(1 for col in [f'D{i}' for i in range(1, 35)]
                 if col in df_l1.columns and nettoyer_note(row[col].values[0]) > 0)
    if matchs == 0 or pd.isna(buts):
        return 0
    return buts / matchs

# ============================================================
# 5. MODÈLE MERCATO
# ============================================================

clutch_poids = {
    'G': 0.35, 'A': 0.30, 'MO': 0.20,
    'DL': 0.15, 'MD': 0.10, 'DC': 0.10
}

def calculer_clutch(id_joueur, cols_j, df_l1):
    nom = nom_depuis_id(id_joueur)
    club = club_depuis_id(id_joueur)
    row = df_l1[
        (df_l1['Joueur'].str.lower() == nom.lower()) &
        (df_l1['Club'].str.lower() == club.lower())
    ]
    if len(row) == 0:
        return 0
    notes = [nettoyer_note(row[col].values[0]) for col in cols_j if col in df_l1.columns]
    notes_jouees = [n for n in notes if n > 0]
    if len(notes_jouees) == 0:
        return 0
    return len([n for n in notes_jouees if n >= 7]) / len(notes_jouees)

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

# ============================================================
# 6. SIMULATION MATCH MPG
# ============================================================

def simuler_buts_mpg(equipe_att, equipe_def, domicile=True):
    buts_mpg = []
    moy_att_adv = np.mean([j['note'] for j in equipe_def.get('ATT', [])] or [0])
    moy_mil_adv = np.mean([j['note'] for j in equipe_def.get('MIL', [])] or [0])
    moy_def_adv = np.mean([j['note'] for j in equipe_def.get('DEF', [])] or [0])
    note_gb_adv = equipe_def['GB'][0]['note'] if equipe_def.get('GB') else 5

    for ligne, joueurs in equipe_att.items():
        if ligne == 'GB':
            continue
        for joueur in joueurs:
            note = joueur['note']
            nom = joueur['joueur']
            if note < 5.5 or joueur.get('buts', 0) > 0:
                continue
            note_courante = note
            if ligne == 'ATT':
                lignes_a_franchir = [(moy_def_adv, -1.0), (note_gb_adv, -0.5)]
            elif ligne == 'MIL':
                lignes_a_franchir = [(moy_mil_adv, -1.0), (moy_def_adv, -0.5), (note_gb_adv, -0.5)]
            elif ligne == 'DEF':
                lignes_a_franchir = [(moy_att_adv, -1.0), (moy_mil_adv, -0.5), (moy_def_adv, -0.5), (note_gb_adv, -0.5)]
            but_mpg = True
            for moy_adverse, malus in lignes_a_franchir:
                passe = note_courante >= moy_adverse if domicile else note_courante > moy_adverse
                if not passe:
                    but_mpg = False
                    break
                note_courante += malus
            if but_mpg:
                buts_mpg.append(nom)
    return buts_mpg

def simuler_match(eq_a, eq_b):
    buts_reels_a = sum(j['buts'] for ligne in eq_a.values() for j in ligne)
    buts_reels_b = sum(j['buts'] for ligne in eq_b.values() for j in ligne)
    if eq_a['GB'][0]['note'] >= 8:
        buts_reels_b = max(0, buts_reels_b - 1)
    if eq_b['GB'][0]['note'] >= 8:
        buts_reels_a = max(0, buts_reels_a - 1)
    buts_mpg_a = simuler_buts_mpg(eq_a, eq_b, domicile=True)
    buts_mpg_b = simuler_buts_mpg(eq_b, eq_a, domicile=False)
    rotaldos_a = sum(1 for ligne in eq_a.values() for j in ligne if j['joueur'] == 'Rotaldo')
    rotaldos_b = sum(1 for ligne in eq_b.values() for j in ligne if j['joueur'] == 'Rotaldo')
    score_a = buts_reels_a + len(buts_mpg_a) - rotaldos_a // 3
    score_b = buts_reels_b + len(buts_mpg_b) - rotaldos_b // 3
    return score_a, score_b, buts_mpg_a, buts_mpg_b

def appliquer_remplacements(equipe, remplacants, col, df_l1, df_brut, utiliser_prediction=False):
    equipe_finale = {}
    remplacants_utilises = []
    pool_remplacants = []
    for ligne, joueurs in remplacants.items():
        for id_j, bonus in joueurs:
            pool_remplacants.append((id_j, bonus, ligne))

    for ligne, joueurs in equipe.items():
        equipe_finale[ligne] = []
        for id_j, bonus in joueurs:
            nom = nom_depuis_id(id_j)
            if utiliser_prediction:
                note = predire_note_j(id_j, col, df_l1)
                buts = buts_attendus_id(id_j, df_l1)
            else:
                note, buts = get_note_id(id_j, col, df_brut)

            if note is None:
                remplacant_trouve = None
                for r_id, r_bonus in remplacants.get(ligne, []):
                    if r_id not in remplacants_utilises:
                        if utiliser_prediction:
                            note_r = predire_note_j(r_id, col, df_l1)
                            buts_r = buts_attendus_id(r_id, df_l1)
                        else:
                            note_r, buts_r = get_note_id(r_id, col, df_brut)
                        if note_r is not None:
                            remplacant_trouve = (r_id, note_r, buts_r, r_bonus)
                            remplacants_utilises.append(r_id)
                            break
                if remplacant_trouve is None:
                    for r_id, r_bonus, r_ligne in pool_remplacants:
                        if r_id not in remplacants_utilises:
                            if utiliser_prediction:
                                note_r = predire_note_j(r_id, col, df_l1)
                                buts_r = buts_attendus_id(r_id, df_l1)
                            else:
                                note_r, buts_r = get_note_id(r_id, col, df_brut)
                            if note_r is not None:
                                remplacant_trouve = (r_id, note_r, buts_r, r_bonus)
                                remplacants_utilises.append(r_id)
                                break
                if remplacant_trouve:
                    equipe_finale[ligne].append({
                        'joueur': nom_depuis_id(remplacant_trouve[0]),
                        'note': remplacant_trouve[1] + remplacant_trouve[3],
                        'buts': remplacant_trouve[2],
                        'statut': f'Remplaçant de {nom}'
                    })
                else:
                    equipe_finale[ligne].append({
                        'joueur': 'Rotaldo',
                        'note': 2.5,
                        'buts': 0,
                        'statut': f'Rotaldo ({nom})'
                    })
            else:
                equipe_finale[ligne].append({
                    'joueur': nom,
                    'note': note + bonus,
                    'buts': buts,
                    'statut': 'Titulaire'
                })
    return equipe_finale

# ============================================================
# 7. CALENDRIER
# ============================================================

def generer_calendrier(nb_equipes, nb_journees):
    equipes = list(range(nb_equipes))
    calendrier = []
    for j in range(nb_journees):
        equipes_rot = equipes[1:]
        idx = j % (nb_equipes - 1)
        equipes_rot = equipes_rot[idx:] + equipes_rot[:idx]
        paires = [(equipes[0], equipes_rot[0])]
        for k in range(1, nb_equipes // 2):
            paires.append((equipes_rot[k], equipes_rot[nb_equipes - 2 - k]))
        calendrier.append(paires)
    return calendrier
