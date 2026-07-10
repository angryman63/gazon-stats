import pandas as pd

CLE_FUSION = ['Joueur', 'Poste', 'Club']


def _colonnes_specifiques(df, taille):
    """Colonnes propres à une taille de ligue, ex: 'Enchere moy/L6', '% achat T1/L6'..."""
    suffixe = f"/L{taille}"
    return [c for c in df.columns if str(c).endswith(suffixe)]


def _verifier_cle_unique(df, nom_fichier):
    doublons = df[df.duplicated(subset=CLE_FUSION, keep=False)]
    if not doublons.empty:
        exemples = doublons[CLE_FUSION].drop_duplicates().head(5).values.tolist()
        raise ValueError(
            f"Le fichier « {nom_fichier} » contient des doublons sur Joueur+Poste+Club "
            f"(ex: {exemples}). Impossible de fusionner sans risquer une erreur d'attribution."
        )


def fusionner_fichiers_joueurs(fichier_6, fichier_8, fichier_10):
    """
    Fusionne les 3 exports MPGStats (ligues à 6, 8 et 10 joueurs) en un seul DataFrame.

    Chaque fichier est censé contenir déjà toutes les colonnes communes (Cote, Note,
    Club, D1-D34, etc.) ainsi que ses colonnes d'enchères spécifiques (suffixe /L6, /L8, /L10).
    Le fichier '6 joueurs' sert de base ; on ne récupère des fichiers 8 et 10 que
    leurs colonnes spécifiques, rattachées via la clé Joueur + Poste + Club.
    """
    df6 = pd.read_excel(fichier_6)
    df8 = pd.read_excel(fichier_8)
    df10 = pd.read_excel(fichier_10)

    for df, nom in [(df6, "6 joueurs"), (df8, "8 joueurs"), (df10, "10 joueurs")]:
        manquantes = [c for c in CLE_FUSION if c not in df.columns]
        if manquantes:
            raise ValueError(
                f"Le fichier « {nom} » ne contient pas les colonnes attendues : {manquantes}. "
                f"Vérifie qu'il s'agit bien d'un export MPGStats standard."
            )
        _verifier_cle_unique(df, nom)

    cols_8 = _colonnes_specifiques(df8, 8)
    cols_10 = _colonnes_specifiques(df10, 10)

    df = df6.merge(df8[CLE_FUSION + cols_8], on=CLE_FUSION, how='left')
    df = df.merge(df10[CLE_FUSION + cols_10], on=CLE_FUSION, how='left')

    return df
