import streamlit as st

def afficher_accueil():
    st.markdown("""
    <div class="hero-section">

      <!-- Logo -->
      <div class="hero-logo">
        <div class="hero-logo-mt">MT</div>
        <div class="hero-logo-sep"></div>
        <div class="hero-logo-tactico">TACTICO</div>
      </div>

      <!-- Titre -->
      <h1 class="hero-title">Devenez le meilleur manager<br><span>de votre ligue</span></h1>

      <!-- Sous-titre -->
      <p class="hero-subtitle">
        Vos rivaux font des choix au feeling. Vous, vous avez Maestro Tactico.<br>
        Chaque journée, chaque mercato, chaque match — prenez les décisions qui font la différence.
      </p>

      <!-- Fonctionnalités -->
      <div class="features-grid">

        <div class="feature-card">
          <span class="feature-emoji">🏆</span>
          <div class="feature-name">Conseiller Hebdo</div>
          <span class="feature-badge badge-free">Gratuit</span>
          <p class="feature-desc">Qui titulariser cette semaine ? Score de fiabilité, régularité, alertes — votre compo du dimanche ne sera plus jamais hasardeuse.</p>
        </div>

        <div class="feature-card">
          <span class="feature-emoji">🛒</span>
          <div class="feature-name">Conseiller Mercato</div>
          <span class="feature-badge badge-premium">Premium</span>
          <p class="feature-desc">Stars, valeurs sûres, pépites planquées : trouvez les joueurs qui feront exploser votre budget dans le bon sens.</p>
        </div>

        <div class="feature-card">
          <span class="feature-emoji">⚔️</span>
          <div class="feature-name">Analyser l'Adversaire</div>
          <span class="feature-badge badge-premium">Premium</span>
          <p class="feature-desc">% de victoire, stratégie optimale, choix du capitaine — affrontez votre prochain adversaire avec les cartes en main.</p>
        </div>

      </div>

    </div>
    """, unsafe_allow_html=True)
