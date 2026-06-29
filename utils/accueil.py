import streamlit as st

def afficher_accueil():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Inter:wght@400;500;600&display=swap');
.hero-section { text-align: center; padding: 48px 24px 32px 24px; max-width: 860px; margin: 0 auto; }
.hero-logo { display: inline-flex; align-items: center; justify-content: center; width: 120px; height: 120px; border-radius: 50%; border: 3px solid #c8a84b; background-color: #141414; margin-bottom: 24px; flex-direction: column; }
.hero-logo-mt { font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 28px; color: #c8a84b; letter-spacing: 2px; line-height: 1; }
.hero-logo-sep { width: 64px; height: 1px; background-color: #c8a84b; opacity: 0.55; margin: 6px auto; }
.hero-logo-tactico { font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 10px; color: #c8a84b; letter-spacing: 4px; opacity: 0.85; line-height: 1; }
.hero-title { font-family: 'Oswald', sans-serif; font-size: 42px; font-weight: 700; color: #ffffff; line-height: 1.1; margin: 0 0 8px 0; }
.hero-title span { color: #c8a84b; }
.hero-subtitle { font-family: 'Inter', sans-serif; font-size: 17px; color: #aaaaaa; line-height: 1.6; margin: 0 auto 40px auto; max-width: 640px; text-align: center !important; }
.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; max-width: 860px; margin: 0 auto 40px auto; padding: 0 8px; }
.feature-card { background-color: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; padding: 24px 20px; text-align: left; }
.feature-emoji { font-size: 28px; margin-bottom: 10px; display: block; }
.feature-name { font-family: 'Oswald', sans-serif; font-size: 16px; font-weight: 700; color: #c8a84b; letter-spacing: 0.5px; margin-bottom: 6px; }
.feature-badge { display: inline-block; font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 20px; margin-bottom: 8px; letter-spacing: 0.5px; text-transform: uppercase; }
.badge-free { background-color: #1e3a1e; color: #4ade80; border: 1px solid #4ade8044; }
.badge-premium { background-color: #3a2a1a; color: #c8a84b; border: 1px solid #c8a84b44; }
.feature-desc { font-family: 'Inter', sans-serif; font-size: 13px; color: #888888; line-height: 1.5; margin: 0; }
@media (max-width: 700px) { .features-grid { grid-template-columns: 1fr; } .hero-title { font-size: 28px; } }
</style>

<div class="hero-section">
  <div class="hero-logo">
    <div class="hero-logo-mt">MT</div>
    <div class="hero-logo-sep"></div>
    <div class="hero-logo-tactico">TACTICO</div>
  </div>
  <h1 class="hero-title">Le coach que vos adversaires<br><span>n'ont pas</span></h1>
  <div style="text-align:center !important; width:100%; display:block;"><p class="hero-subtitle">Recommandations hebdo, stratégie mercato, analyse de vos adversaires.</p></div>
  <div class="features-grid">
    <div class="feature-card">
      <span class="feature-emoji">🏆</span>
      <div class="feature-name">Conseiller Hebdo</div>
      <span class="feature-badge badge-free">Gratuit</span>
      <p class="feature-desc">La meilleure compo possible à chaque match.</p>
    </div>
    <div class="feature-card">
      <span class="feature-emoji">🛒</span>
      <div class="feature-name">Conseiller Mercato</div>
      <span class="feature-badge badge-premium">Premium</span>
      <p class="feature-desc">Le bon joueur, au bon prix.</p>
    </div>
    <div class="feature-card">
      <span class="feature-emoji">⚔️</span>
      <div class="feature-name">Simuler le match</div>
      <span class="feature-badge badge-premium">Premium</span>
      <p class="feature-desc">Le match est déjà joué.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
