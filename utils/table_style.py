import html as _html
import streamlit as st
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600&display=swap');

div[data-testid="stRadio"] > div {
    background-color: #1a1a1a;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid rgba(200, 168, 75, 0.35);
}
div[data-testid="stRadio"] label p {
    color: #f5f5f5 !important;
}

/* ── Sélecteurs Mercato : taille de ligue / stratégie (pilules or) ── */
.st-key-mercato_taille_ligue [data-testid="stRadioGroup"],
.st-key-mercato_strategie [data-testid="stRadioGroup"] {
    gap: 6px;
}
.st-key-mercato_taille_ligue [data-testid="stRadioOption"],
.st-key-mercato_strategie [data-testid="stRadioOption"] {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 16px;
    transition: background-color 0.2s ease, border-color 0.2s ease;
}
.st-key-mercato_taille_ligue [data-testid="stRadioOption"]:hover,
.st-key-mercato_strategie [data-testid="stRadioOption"]:hover {
    background-color: rgba(200, 168, 75, 0.08);
}
.st-key-mercato_taille_ligue [data-testid="stRadioOption"][data-selected="true"],
.st-key-mercato_strategie [data-testid="stRadioOption"][data-selected="true"] {
    background-color: rgba(200, 168, 75, 0.18);
    border-color: #c8a84b;
}
.st-key-mercato_taille_ligue [data-testid="stRadioOption"] > div > div > div:first-child,
.st-key-mercato_strategie [data-testid="stRadioOption"] > div > div > div:first-child {
    display: none;
}
.st-key-mercato_taille_ligue [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p,
.st-key-mercato_strategie [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p {
    font-family: 'Oswald', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em;
    color: rgba(255, 255, 255, 0.75) !important;
    margin: 0 !important;
    transition: color 0.2s ease;
}
.st-key-mercato_taille_ligue [data-testid="stRadioOption"][data-selected="true"] [data-testid="stMarkdownContainer"] p,
.st-key-mercato_strategie [data-testid="stRadioOption"][data-selected="true"] [data-testid="stMarkdownContainer"] p {
    color: #c8a84b !important;
    font-weight: 700 !important;
}

/* ── Onglets de poste (Mercato + Conseiller Hebdo) : Attaquants / Milieux / ... ── */
.st-key-mercato_postes .react-aria-SelectionIndicator,
.st-key-hebdo_postes .react-aria-SelectionIndicator {
    display: none !important;
}
.st-key-mercato_postes > div > [role="tablist"],
.st-key-hebdo_postes > div > [role="tablist"] {
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    padding: 6px !important;
    gap: 6px !important;
}
.st-key-mercato_postes > div > [role="tablist"] > [data-testid="stTab"],
.st-key-hebdo_postes > div > [role="tablist"] > [data-testid="stTab"] {
    position: relative !important;
    background-color: transparent !important;
    color: rgba(255, 255, 255, 0.62) !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 0 18px !important;
    border-radius: 8px !important;
    border-bottom: none !important;
    transition: color 0.25s ease, background-color 0.25s ease !important;
}
.st-key-mercato_postes > div > [role="tablist"] > [data-testid="stTab"]:hover,
.st-key-hebdo_postes > div > [role="tablist"] > [data-testid="stTab"]:hover {
    color: rgba(255, 255, 255, 0.92) !important;
    background-color: rgba(200, 168, 75, 0.08) !important;
}
.st-key-mercato_postes > div > [role="tablist"] > [data-testid="stTab"][aria-selected="true"],
.st-key-hebdo_postes > div > [role="tablist"] > [data-testid="stTab"][aria-selected="true"] {
    color: #c8a84b !important;
    background-color: rgba(200, 168, 75, 0.13) !important;
    font-weight: 700 !important;
}
.st-key-mercato_postes > div > [role="tablist"] > [data-testid="stTab"][aria-selected="true"]::after,
.st-key-hebdo_postes > div > [role="tablist"] > [data-testid="stTab"][aria-selected="true"]::after {
    content: "";
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 4px;
    height: 2px;
    border-radius: 2px;
    background-color: #c8a84b;
}

/* ── Sélecteur "Trier par" : texte en Raleway (valeur affichée + options du menu) ── */
[class*="st-key-tri_col_"] input[role="combobox"] {
    font-family: 'Raleway', sans-serif !important;
}
[role="listbox"] [role="option"] {
    font-family: 'Raleway', sans-serif !important;
}

/* ── Sélecteur d'ordre de tri (↓ / ↑) à côté de "Trier par" ── */
[class*="st-key-tri_ordre_"] [data-testid="stRadioGroup"] {
    gap: 4px;
}
[class*="st-key-tri_ordre_"] [data-testid="stRadioOption"] {
    background-color: transparent;
    border: 1px solid rgba(200, 168, 75, 0.25);
    border-radius: 6px;
    padding: 4px 10px;
    transition: background-color 0.2s ease, border-color 0.2s ease;
}
[class*="st-key-tri_ordre_"] [data-testid="stRadioOption"]:hover {
    background-color: rgba(200, 168, 75, 0.08);
}
[class*="st-key-tri_ordre_"] [data-testid="stRadioOption"][data-selected="true"] {
    background-color: rgba(200, 168, 75, 0.18);
    border-color: #c8a84b;
}
[class*="st-key-tri_ordre_"] [data-testid="stRadioOption"] > div > div > div:first-child {
    display: none;
}
[class*="st-key-tri_ordre_"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255, 255, 255, 0.7) !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 700 !important;
    margin: 0 !important;
    transition: color 0.2s ease;
}
[class*="st-key-tri_ordre_"] [data-testid="stRadioOption"][data-selected="true"] [data-testid="stMarkdownContainer"] p {
    color: #c8a84b !important;
}

/* ── Expander "Légende blessures" ── */
[data-testid="stExpander"] details {
    background-color: #161616 !important;
    border: 1px solid rgba(200, 168, 75, 0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    border-radius: 10px;
    transition: background-color 0.2s ease;
}
[data-testid="stExpander"] summary:hover {
    background-color: rgba(200, 168, 75, 0.06) !important;
}
[data-testid="stExpander"] [data-testid="stIconMaterial"] {
    color: #c8a84b !important;
}
[data-testid="stExpander"] summary p {
    font-family: 'Oswald', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
}
[data-testid="stExpander"] table {
    font-family: 'Raleway', sans-serif !important;
}
.gs-caption {
    color: #c8a84b;
    font-size: 0.85em;
    margin-top: -6px;
    margin-bottom: 10px;
}
.gs-table-wrap {
    max-height: 440px;
    overflow-y: auto;
    border-radius: 10px;
    border: 1px solid rgba(200, 168, 75, 0.25);
    margin-bottom: 8px;
}
.gs-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Raleway', sans-serif;
    font-size: 0.87em;
}
.gs-table thead th {
    position: sticky;
    top: 0;
    background-color: #0d0d0d;
    color: #c8a84b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-family: 'Oswald', sans-serif;
    font-size: 0.72em;
    font-weight: 700;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid rgba(200, 168, 75, 0.35);
    white-space: nowrap;
}
.gs-table tbody td {
    padding: 9px 14px;
    color: #e8e8e8;
    border-bottom: 1px solid #232323;
    white-space: nowrap;
}
.gs-table tbody tr:nth-child(odd) { background-color: #161616; }
.gs-table tbody tr:nth-child(even) { background-color: #202020; }
.gs-table tbody tr:hover { background-color: #2a2412; }
.gs-table .gs-name { color: #ffffff; font-weight: 600; }
.gs-table .gs-pill { font-family: 'Inter', sans-serif; }
.gs-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.92em;
    font-weight: 600;
    white-space: nowrap;
}
.gs-pill-bad        { background-color: #3d1f1f; color: #ff6b6b; }
.gs-pill-warn       { background-color: #3a2a12; color: #e8a33d; }
.gs-pill-good       { background-color: #1e3a24; color: #6fd18c; }
.gs-pill-good-dark  { background-color: #0d2414; color: #3da85e; }
.gs-pill-mid        { background-color: #2a2a2a; color: #c8a84b; }
.gs-pill-info       { background-color: #14262e; color: #6ec6d9; }
.gs-page-title {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 2.1em;
    color: #ffffff;
    letter-spacing: 0.5px;
    margin: 0 0 18px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid #c8a84b;
    display: inline-block;
}
.gs-dash { color: #555555; }

/* ── Séparateur or ── */
.gs-sep {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 1rem 0 0.8rem;
}
.gs-sep-line-l {
    flex: 1;
    height: 2px;
    background: linear-gradient(to right, transparent, #c8a84b66);
}
.gs-sep-line-r {
    flex: 1;
    height: 2px;
    background: linear-gradient(to left, transparent, #c8a84b66);
}
.gs-sep-label {
    font-family: 'Oswald', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 0.22em;
    color: #c8a84b;
    white-space: nowrap;
    text-transform: uppercase;
}

/* ── Cards équipes ── */
.gs-equipe-card {
    background-color: #141414;
    border-radius: 6px;
    padding: 16px 20px;
    border-top: 2px solid;
    margin-bottom: 12px;
}
.gs-equipe-card.moi { border-color: #c8a84b; }
.gs-equipe-card.adv { border-color: #333333; }
.gs-equipe-title {
    font-family: 'Oswald', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.gs-equipe-title.or  { color: #c8a84b; }
.gs-equipe-title.gris { color: #555555; }

/* ── Bouton simulation ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #c8a84b, #8a6f2e) !important;
    color: #0d0d0d !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.75rem 2.5rem !important;
    transition: opacity 0.2s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.85 !important;
}

/* ── Bouton "Valider" (sidebar) — même typographie que le bouton de simulation ── */
.st-key-btn_valider_joueurs button {
    font-family: 'Oswald', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}

.gs-roster {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.gs-roster-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background-color: #161616;
    border: 1px solid #232323;
    border-radius: 8px;
    padding: 8px 12px;
}
.gs-roster-ligne {
    color: #c8a84b;
    font-size: 0.72em;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    width: 42px;
    flex-shrink: 0;
}
.gs-roster-nom {
    color: #ffffff;
    font-weight: 600;
    flex-grow: 1;
}
.gs-roster-note {
    color: #c8a84b;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    width: 48px;
    text-align: right;
    flex-shrink: 0;
}
</style>
"""
def inject_style():
    st.markdown(THEME_CSS, unsafe_allow_html=True)

def separateur(titre):
    st.markdown(f"""
    <div class="gs-sep">
        <div class="gs-sep-line-l"></div>
        <span class="gs-sep-label">{titre}</span>
        <div class="gs-sep-line-r"></div>
    </div>
    """, unsafe_allow_html=True)

def escape(val):
    return _html.escape(str(val))
def pill(text, kind='mid'):
    """kind: bad | warn | good | good-dark | mid | info"""
    return f'<span class="gs-pill gs-pill-{kind}">{escape(text)}</span>'
def dash(symbol='—'):
    return f'<span class="gs-dash">{symbol}</span>'
def name_cell(val):
    return f'<span class="gs-name">{escape(val)}</span>'
def table_html(df, cell_renderer):
    """Construit un tableau HTML stylé.
    cell_renderer(col, val) -> str (html à insérer dans la cellule)."""
    colonnes = list(df.columns)
    entetes = ''.join(f'<th>{escape(c)}</th>' for c in colonnes)
    lignes = []
    for _, row in df.iterrows():
        cellules = ''.join(f'<td>{cell_renderer(c, row[c])}</td>' for c in colonnes)
        lignes.append(f'<tr>{cellules}</tr>')
    corps = ''.join(lignes)
    return (
        '<div class="gs-table-wrap"><table class="gs-table">'
        f'<thead><tr>{entetes}</tr></thead><tbody>{corps}</tbody>'
        '</table></div>'
    )
