import sys
import os

# Permet d'importer utils.fusion_joueurs depuis la racine du repo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fusion_joueurs import fusionner_fichiers_joueurs

FICHIER_6 = "L1joueurs26-27_6joueurs.xlsx"
FICHIER_8 = "L1joueurs26-27_8joueurs.xlsx"
FICHIER_10 = "L1joueurs26-27_10joueurs.xlsx"
FICHIER_SORTIE = "joueurs_fusionne.xlsx"


def main():
    for fichier in (FICHIER_6, FICHIER_8, FICHIER_10):
        if not os.path.exists(fichier):
            print(f"❌ Fichier manquant : {fichier}")
            sys.exit(1)

    df = fusionner_fichiers_joueurs(FICHIER_6, FICHIER_8, FICHIER_10)
    df.to_excel(FICHIER_SORTIE, index=False)
    print(f"✅ Fusion réussie : {len(df)} joueurs -> {FICHIER_SORTIE}")


if __name__ == "__main__":
    main()
