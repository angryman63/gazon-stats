import streamlit as st

def afficher_accueil():

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Raleway:wght@400;500&display=swap');

.hero-wrap {
    width: 100%;
    text-align: center;
    padding: 48px 0 40px 0;
}
.hero-title {
    font-family: "Oswald", sans-serif; font-size: 38px; font-weight: 700;
    color: #ffffff; line-height: 1.1; margin: 0 0 20px 0;
}
.hero-title span { color: #c8a84b; }
.hero-subtitle {
    font-family: "Raleway", sans-serif; font-size: 16px; color: #aaaaaa;
    line-height: 1.7; margin: 0 auto 48px auto;
}
.feat-card {
    background-color: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 14px; padding: 36px 28px; height: 100%;
}
.feat-name {
    font-family: "Oswald", sans-serif; font-size: 17px; font-weight: 700;
    color: #c8a84b; letter-spacing: 0.5px; margin-bottom: 14px;
}
.feat-badge {
    display: inline-block; font-family: "Raleway", sans-serif;
    font-size: 10px; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; margin-bottom: 18px; letter-spacing: 0.8px; text-transform: uppercase;
}
.badge-free  { background-color: #252525; color: #c0c0c0; border: 1px solid #c0c0c066; }
.badge-premium { background-color: #2a1f0a; color: #c8a84b; border: 1px solid #c8a84b88; }
.feat-desc {
    font-family: "Raleway", sans-serif; font-size: 14px;
    color: #888888; line-height: 1.75; margin: 0;
}
</style>

<div class="hero-wrap">
  <h1 class="hero-title">Le coach que vos adversaires <span>n\'ont pas</span></h1>
  <div style="font-family:Raleway,sans-serif; font-size:16px; color:#aaaaaa; line-height:1.7; margin:0 auto 48px auto; text-align:center; width:100%;">Recommandations hebdo, strat\u00e9gie mercato, analyse de vos adversaires.</div>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
<div class="feat-card">
  <div class="feat-name">Conseiller Hebdo</div>
  <p class="feat-desc">Le bon choix pour aligner les meilleurs joueurs de la semaine.</p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="feat-card">
  <div class="feat-name">Conseiller Mercato</div>
  <p class="feat-desc">Trouver les joueurs \u00e0 acheter selon le budget et la strat\u00e9gie \u2014 Stars, Valeurs s\u00fbres, P\u00e9pites ou joueurs \u00e0 \u00e9viter.</p>
</div>
""", unsafe_allow_html=True)

    with col3:
        st.markdown("""
<div class="feat-card">
  <div class="feat-name">Simuler le match</div>
  <p class="feat-desc">Pr\u00e9parer chaque match comme un pro.</p>
</div>
""", unsafe_allow_html=True)
