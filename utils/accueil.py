import streamlit as st

def afficher_accueil():

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Raleway:wght@400;500&display=swap');

.hero-section {
    text-align: center;
    padding: 56px 24px 24px 24px;
    max-width: 900px;
    margin: 0 auto;
}
.hero-logo-big {
    display: inline-flex; align-items: center; justify-content: center;
    width: 110px; height: 110px; border-radius: 50%;
    border: 3px solid #c8a84b; background-color: #0d0d0d;
    margin-bottom: 40px; flex-direction: column;
}
.hero-logo-big .mt {
    font-family: "Oswald", sans-serif; font-weight: 700;
    font-size: 26px; color: #c8a84b; letter-spacing: 2px; line-height: 1;
}
.hero-logo-big .sep {
    width: 58px; height: 1px; background-color: #c8a84b;
    opacity: 0.55; margin: 5px auto;
}
.hero-logo-big .tactico {
    font-family: "Oswald", sans-serif; font-weight: 700;
    font-size: 9px; color: #c8a84b; letter-spacing: 4px; opacity: 0.85; line-height: 1;
}
.hero-title {
    font-family: "Oswald", sans-serif; font-size: 38px; font-weight: 700;
    color: #ffffff; line-height: 1.1; margin: 0 0 24px 0; white-space: nowrap;
}
.hero-title span { color: #c8a84b; }
.hero-subtitle {
    font-family: "Raleway", sans-serif; font-size: 16px; color: #aaaaaa;
    line-height: 1.7; margin: 0 auto 48px auto; max-width: 560px; text-align: center;
}
.feat-card {
    background-color: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 14px; padding: 36px 28px; height: 100%;
}
.feat-emoji { font-size: 32px; margin-bottom: 18px; display: block; }
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

<div class="hero-section">
  <div class="hero-logo-big">
    <div class="mt">MT</div>
    <div class="sep"></div>
    <div class="tactico">TACTICO</div>
  </div>
  <h1 class="hero-title">Le coach que vos adversaires <span>n\'ont pas</span></h1>
  <p class="hero-subtitle">Recommandations hebdo, strat\u00e9gie mercato, analyse de vos adversaires.</p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
<div class="feat-card">
  <span class="feat-emoji">\U0001f3c6</span>
  <div class="feat-name">Conseiller Hebdo</div>
  <span class="feat-badge badge-free">Gratuit</span>
  <p class="feat-desc">La meilleure compo possible \u00e0 chaque match.</p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="feat-card">
  <span class="feat-emoji">\U0001f6d2</span>
  <div class="feat-name">Conseiller Mercato</div>
  <span class="feat-badge badge-premium">Premium</span>
  <p class="feat-desc">Le bon joueur, au bon prix.</p>
</div>
""", unsafe_allow_html=True)

    with col3:
        st.markdown("""
<div class="feat-card">
  <span class="feat-emoji">\u2694\ufe0f</span>
  <div class="feat-name">Simuler le match</div>
  <span class="feat-badge badge-premium">Premium</span>
  <p class="feat-desc">Le match est d\u00e9j\u00e0 jou\u00e9.</p>
</div>
""", unsafe_allow_html=True)
