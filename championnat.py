# ============================================================
# MINI CHAMPIONNAT MPG — 8 ÉQUIPES
# ============================================================

import random
random.seed(42)

noms_equipes = [
    "Les Invincibles",
    "FC Rotaldo",
    "Stade des Clutchs",
    "AS Pépites",
    "Olympique des Stars",
    "RC Valeurs Sûres",
    "SC Mercato",
    "Athletic Gazon"
]

besoins = {
    'G': 2,
    'DC': 4,
    'DL': 3,
    'MD': 4,
    'MO': 3,
    'A': 4,
}

poste_map = {
    'G':  ('GB',  0,    1),
    'DC': ('DEF', 0.5,  2),
    'DL': ('DEF', 0,    2),
    'MD': ('MIL', 0,    2),
    'MO': ('MIL', 0,    2),
    'A':  ('ATT', 0,    3),
}

def snake_draft(joueurs_poste, nb_equipes, nb_par_equipe):
    selections = {i: [] for i in range(nb_equipes)}
    joueurs = list(joueurs_poste)
    tour = 0
    ordre = list(range(nb_equipes))
    while any(len(v) < nb_par_equipe for v in selections.values()) and joueurs:
        ordre_tour = ordre if tour % 2 == 0 else ordre[::-1]
        for eq in ordre_tour:
            if len(selections[eq]) < nb_par_equipe and joueurs:
                selections[eq].append(joueurs.pop(0))
        tour += 1
    return selections

def creer_equipes(df_l1):
    df_eligible = df_l1.copy()
    for col in ['Note', 'Cote', '%Titu']:
        df_eligible[col] = pd.to_numeric(df_eligible[col], errors='coerce')
    df_eligible = df_eligible[
        (df_eligible['Note'] >= 4.5) &
        (df_eligible['%Titu'] >= 30)
    ].dropna(subset=['Note', 'Cote', '%Titu'])
    df_eligible['ID'] = df_eligible['Joueur'] + '_' + df_eligible['Club']
    df_eligible = df_eligible.sort_values('Note', ascending=False)

    nb_equipes = 8
    equipes_joueurs = {i: {} for i in range(nb_equipes)}
    ids_utilises = set()

    for poste, nb in besoins.items():
        ids_poste = df_eligible[df_eligible['Poste'] == poste]['ID'].tolist()
        ids_poste = [j for j in ids_poste if j not in ids_utilises]
        draft = snake_draft(ids_poste, nb_equipes, nb)
        for eq, ids in draft.items():
            equipes_joueurs[eq][poste] = ids
            for j in ids:
                ids_utilises.add(j)

    return equipes_joueurs

def construire_equipe(eq_idx, equipes_joueurs):
    equipe = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
    remplacants = {'GB': [], 'DEF': [], 'MIL': [], 'ATT': []}
    for poste, (ligne, bonus, nb_titu) in poste_map.items():
        ids = equipes_joueurs[eq_idx].get(poste, [])
        for i, id_j in enumerate(ids):
            if i < nb_titu:
                equipe[ligne].append((id_j, bonus))
            else:
                remplacants[ligne].append((id_j, bonus))
    return equipe, remplacants
