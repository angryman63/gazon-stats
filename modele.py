import pandas as pd
import numpy as np

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

def calculer_clutch(row, cols_journees, seuil=7):
    notes = [row[col] for col in cols_journees if col in row.index]
    notes_jouees = [n for n in notes if n > 0]
    if len(notes_jouees) == 0:
        return 0
    return len([n for n in notes_jouees if n >= seuil]) / len(notes_jouees)

def compter_matchs(row, cols_journees):
    return sum(1 for col in cols_journees if row[col] > 0)

def absences_consecutives(row, cols_journees):
    notes = [row[col] for col in cols_journees]
    count = 0
    for n in notes:
        if n == 0:
            count += 1
        else:
            break
    return count

def predire_note(row, cols_journees):
    notes = [row[col] for col in cols_journees if row[col] > 0]
    if len(notes) < 3:
        return None
    poids = [0.30, 0.23, 0.18, 0.14, 0.10, 0.05]
    notes_6 = notes[:6]
    total_poids = sum(poids[:len(notes_6)])
    return round(sum(n * poids[i] for i, n in enumerate(notes_6)) / total_poids, 2)

def alerte_blessure(row, cols_journees):
    indispo = row.get('Indispo ?', False)
    absences = absences_consecutives(row, cols_journees)
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

def etiquette_regularite(valeur, q25, q50, q75):
    if valeur >= q75:
        return "1 ✅ Valeur sûre"
    elif valeur >= q50:
        return "2 👌 Fiable"
    elif valeur >= q25:
        return "3 ⚠️ Capricieux"
    else:
        return "4 🐐 Rotaldo"

def get_joueur_info(nom_joueur, df, cols_journees):
    row = df[df['Joueur'].str.lower() == nom_joueur.strip().lower()]
    if len(row) == 0:
        return None
    row = row.iloc[0]
    note_pred = predire_note(row, cols_journees)
    buts_moy = pd.to_numeric(row.get('Buts', 0), errors='coerce')
    matchs = compter_matchs(row, cols_journees)
    buts_par_match = (buts_moy / matchs) if matchs > 0 and not pd.isna(buts_moy) else 0
    clutch_7 = calculer_clutch(row, cols_journees, seuil=7)
    clutch_8 = calculer_clutch(row, cols_journees, seuil=8)
    notes_jouees = [row[col] for col in cols_journees if row[col] > 0]
    regularite = 1 / (1 + np.std(notes_jouees)) if notes_jouees else 0
    return {
        'nom': row['Joueur'],
        'poste': row.get('Poste', 'MO'),
        'note_pred': note_pred,
        'buts': buts_par_match,
        'clutch_7': clutch_7,
        'clutch_8': clutch_8,
        'regularite': regularite,
        'alerte': alerte_blessure(row, cols_journees)
    }

def poste_vers_ligne(poste):
    mapping = {'G': 'GB', 'DC': 'DEF', 'DL': 'DEF', 'MD': 'MIL', 'MO': 'MIL', 'A': 'ATT'}
    return mapping.get(poste, 'MIL')

def simuler_buts_mpg(equipe_att, equipe_def, domicile=True):
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
            if note is None or note < 5.5 or j.get('buts', 0) > 0:
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

def appliquer_bonus(equipe_moi, equipe_adv, mon_bonus, bonus_adv, joueur_uber=None):
    import copy
    eq_moi = copy.deepcopy(equipe_moi)
    eq_adv = copy.deepcopy(equipe_adv)
    ann_adv = 0
    ann_moi = 0

    # Mon bonus
    if "Zahia" in mon_bonus:
        for ligne, joueurs in eq_moi.items():
            if ligne != 'GB':
                for j in joueurs:
                    if j['note_pred']:
                        j['note_pred'] = min(10, j['note_pred'] + 1)
    elif "Suarez" in mon_bonus:
        if eq_adv.get('GB') and eq_adv['GB'][0]['note_pred']:
            eq_adv['GB'][0]['note_pred'] = max(0, eq_adv['GB'][0]['note_pred'] - 1)
    elif "Cheat Code" in mon_bonus:
        for ligne, joueurs in eq_adv.items():
            if ligne != 'GB':
                for j in joueurs:
                    if j['note_pred']:
                        j['note_pred'] = max(0, j['note_pred'] - 0.5)
    elif "Valise" in mon_bonus:
        ann_adv = 1
    elif "Uber Eats" in mon_bonus and joueur_uber:
        for ligne, joueurs in eq_moi.items():
            for j in joueurs:
                if j['nom'] == joueur_uber and j['note_pred']:
                    j['note_pred'] = min(10, j['note_pred'] + 1)
    elif "Chapron" in mon_bonus:
        meilleur_score = 0
        meilleure_ligne = None
        meilleur_idx = None
        for ligne, joueurs in eq_adv.items():
            if ligne == 'GB':
                continue
            for idx, j in enumerate(joueurs):
                if j['note_pred'] and j['note_pred'] > meilleur_score:
                    meilleur_score = j['note_pred']
                    meilleure_ligne = ligne
                    meilleur_idx = idx
        if meilleure_ligne is not None:
            eq_adv[meilleure_ligne][meilleur_idx] = {
                'nom': 'Rotaldo', 'note_pred': 2.5, 'buts': 0,
                'clutch_7': 0, 'clutch_8': 0, 'regularite': 0, 'alerte': ''
            }
    elif "Miroir" in mon_bonus and bonus_adv != "Aucun":
        eq_moi, eq_adv, ann_adv, ann_moi = appliquer_bonus(eq_moi, eq_adv, bonus_adv, "Aucun", joueur_uber)
        return eq_moi, eq_adv, ann_adv, ann_moi

    # Bonus adverse
    if "Zahia" in bonus_adv:
        for ligne, joueurs in eq_adv.items():
            if ligne != 'GB':
                for j in joueurs:
                    if j['note_pred']:
                        j['note_pred'] = min(10, j['note_pred'] + 1)
    elif "Suarez" in bonus_adv:
        if eq_moi.get('GB') and eq_moi['GB'][0]['note_pred']:
            eq_moi['GB'][0]['note_pred'] = max(0, eq_moi['GB'][0]['note_pred'] - 1)
    elif "Cheat Code" in bonus_adv:
        for ligne, joueurs in eq_moi.items():
            if ligne != 'GB':
                for j in joueurs:
                    if j['note_pred']:
                        j['note_pred'] = max(0, j['note_pred'] - 0.5)
    elif "Valise" in bonus_adv:
        ann_moi = 1
    elif "Chapron" in bonus_adv:
        meilleur_score = 0
        meilleure_ligne = None
        meilleur_idx = None
        for ligne, joueurs in eq_moi.items():
            if ligne == 'GB':
                continue
            for idx, j in enumerate(joueurs):
                if j['note_pred'] and j['note_pred'] > meilleur_score:
                    meilleur_score = j['note_pred']
                    meilleure_ligne = ligne
                    meilleur_idx = idx
        if meilleure_ligne is not None:
            eq_moi[meilleure_ligne][meilleur_idx] = {
                'nom': 'Rotaldo', 'note_pred': 2.5, 'buts': 0,
                'clutch_7': 0, 'clutch_8': 0, 'regularite': 0, 'alerte': ''
            }

    return eq_moi, eq_adv, ann_adv, ann_moi


def monte_carlo_match(joueurs_moi, joueurs_adv, n_simulations=500, bonus_moi=None, bonus_adv=None):
    victoires = 0
    nuls = 0
    defaites = 0
    scores_moi = []
    scores_adv = []

    for _ in range(n_simulations):
        # Générer notes aléatoires
        notes_moi = {}
        for j in joueurs_moi:
            note = np.random.normal(j['moyenne'], j['ecart_type'])
            note = max(0, min(10, note))
            notes_moi[j['nom']] = {
                'note': note,
                'ligne': j['ligne'],
                'buts': j['buts']
            }

        notes_adv = {}
        for j in joueurs_adv:
            note = np.random.normal(j['moyenne'], j['ecart_type'])
            note = max(0, min(10, note))
            notes_adv[j['nom']] = {
                'note': note,
                'ligne': j['ligne'],
                'buts': j['buts']
            }

        # Appliquer bonus mon équipe
        if bonus_moi == 'zahia':
            for k in notes_moi:
                if notes_moi[k]['ligne'] != 'GB':
                    notes_moi[k]['note'] = min(10, notes_moi[k]['note'] + 1)
        elif bonus_moi == 'suarez':
            for k in notes_adv:
                if notes_adv[k]['ligne'] == 'GB':
                    notes_adv[k]['note'] = max(0, notes_adv[k]['note'] - 1)
        elif bonus_moi == 'cheat_code':
            for k in notes_adv:
                if notes_adv[k]['ligne'] != 'GB':
                    notes_adv[k]['note'] = max(0, notes_adv[k]['note'] - 0.5)

        # Appliquer bonus adverse
        if bonus_adv == 'zahia':
            for k in notes_adv:
                if notes_adv[k]['ligne'] != 'GB':
                    notes_adv[k]['note'] = min(10, notes_adv[k]['note'] + 1)
        elif bonus_adv == 'cheat_code':
            for k in notes_moi:
                if notes_moi[k]['ligne'] != 'GB':
                    notes_moi[k]['note'] = max(0, notes_moi[k]['note'] - 0.5)

        # Moyennes par ligne
        def moy_ligne(notes, ligne):
            vals = [v['note'] for v in notes.values() if v['ligne'] == ligne]
            return np.mean(vals) if vals else 5.0

        moy_def_adv = moy_ligne(notes_adv, 'DEF')
        moy_mil_adv = moy_ligne(notes_adv, 'MIL')
        moy_att_adv = moy_ligne(notes_adv, 'ATT')
        note_gb_adv = next((v['note'] for v in notes_adv.values() if v['ligne'] == 'GB'), 5.0)

        moy_def_moi = moy_ligne(notes_moi, 'DEF')
        moy_mil_moi = moy_ligne(notes_moi, 'MIL')
        moy_att_moi = moy_ligne(notes_moi, 'ATT')
        note_gb_moi = next((v['note'] for v in notes_moi.values() if v['ligne'] == 'GB'), 5.0)

        # Buts réels
        score_moi = sum(1 for v in notes_moi.values()
                       if v['buts'] > 0 and np.random.random() < v['buts'])
        score_adv = sum(1 for v in notes_adv.values()
                       if v['buts'] > 0 and np.random.random() < v['buts'])

        # Valise
        if bonus_moi == 'valise':
            score_adv = max(0, score_adv - 1)
        if bonus_adv == 'valise':
            score_moi = max(0, score_moi - 1)

        # Arrêt MPG gardien
        if note_gb_moi >= 8:
            score_adv = max(0, score_adv - 1)
        if note_gb_adv >= 8:
            score_moi = max(0, score_moi - 1)

        # Buts MPG mon équipe
        for nom, j in notes_moi.items():
            if j['note'] < 5.5 or j['buts'] > 0:
                continue
            note_c = j['note']
            if j['ligne'] == 'ATT':
                lignes = [(moy_def_adv, -1.0), (note_gb_adv, -0.5)]
            elif j['ligne'] == 'MIL':
                lignes = [(moy_mil_adv, -1.0), (moy_def_adv, -0.5), (note_gb_adv, -0.5)]
            elif j['ligne'] == 'DEF':
                lignes = [(moy_att_adv, -1.0), (moy_mil_adv, -0.5),
                          (moy_def_adv, -0.5), (note_gb_adv, -0.5)]
            else:
                continue
            but = True
            for moy, malus in lignes:
                if note_c < moy:
                    but = False
                    break
                note_c += malus
            if but:
                score_moi += 1

        # Buts MPG adversaire
        for nom, j in notes_adv.items():
            if j['note'] < 5.5 or j['buts'] > 0:
                continue
            note_c = j['note']
            if j['ligne'] == 'ATT':
                lignes = [(moy_def_moi, -1.0), (note_gb_moi, -0.5)]
            elif j['ligne'] == 'MIL':
                lignes = [(moy_mil_moi, -1.0), (moy_def_moi, -0.5), (note_gb_moi, -0.5)]
            elif j['ligne'] == 'DEF':
                lignes = [(moy_att_moi, -1.0), (moy_mil_moi, -0.5),
                          (moy_def_moi, -0.5), (note_gb_moi, -0.5)]
            else:
                continue
            but = True
            for moy, malus in lignes:
                if note_c <= moy:
                    but = False
                    break
                note_c += malus
            if but:
                score_adv += 1

        scores_moi.append(score_moi)
        scores_adv.append(score_adv)

        if score_moi > score_adv:
            victoires += 1
        elif score_moi < score_adv:
            defaites += 1
        else:
            nuls += 1

    return {
        'victoires': round(victoires / n_simulations * 100, 1),
        'nuls': round(nuls / n_simulations * 100, 1),
        'defaites': round(defaites / n_simulations * 100, 1),
        'score_moy_moi': round(np.mean(scores_moi), 1),
        'score_moy_adv': round(np.mean(scores_adv), 1),
    }

def get_stats_joueur_mc(info_joueur, cols_journees, df):
    nom = info_joueur['nom']
    row = df[df['Joueur'].str.lower() == nom.lower()]
    if len(row) == 0:
        return None
    row = row.iloc[0]
    notes = [row[col] for col in cols_journees if row[col] > 0]
    if len(notes) < 3:
        return None
    buts = pd.to_numeric(row.get('Buts', 0), errors='coerce')
    matchs = len(notes)
    buts_par_match = buts / matchs if matchs > 0 and not pd.isna(buts) else 0
    return {
        'nom': nom,
        'ligne': poste_vers_ligne(info_joueur['poste']),
        'moyenne': np.mean(notes),
        'ecart_type': np.std(notes),
        'buts': buts_par_match
    }
