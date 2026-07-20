import html as _html
import streamlit as st
THEME_CSS = """
<style>
div[data-testid="stRadio"] > div {
    background-color: #1a1a1a;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid rgba(200, 168, 75, 0.35);
}
div[data-testid="stRadio"] label p {
    color: #f5f5f5 !important;
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
    font-family: 'Inter', sans-serif;
    font-size: 0.87em;
}
.gs-table thead th {
    position: sticky;
    top: 0;
    background-color: #0d0d0d;
    color: #c8a84b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
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
.gs-table tbody tr:nth-child(even) { background-color: #1c1c1c; }
.gs-table tbody tr:hover { background-color: #2a2412; }
.gs-table .gs-name { color: #ffffff; font-weight: 600; }
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
    font-size: 1.9em;
    color: #ffffff;
    letter-spacing: 0.5px;
    margin: 0 0 14px 0;
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
