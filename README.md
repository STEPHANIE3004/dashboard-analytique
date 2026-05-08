# 📊 Dashboard Analytique — Performance Bancaire CAC40

Dashboard de reporting automatisé généré en Python : **8 graphiques** couvrant les cours boursiers réels, rendements mensuels, volatilité annualisée, corrélations et drawdowns — pour les **4 valeurs bancaires du CAC40** (BNP Paribas, Soc. Générale, Crédit Agricole, AXA).

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Yahoo Finance](https://img.shields.io/badge/Yahoo%20Finance-cours%20r%C3%A9els%2012%20mois-blue)
![matplotlib](https://img.shields.io/badge/matplotlib-dashboard%208%20panneaux-orange)
![CAC40](https://img.shields.io/badge/CAC40-BNP%20%7C%20GLE%20%7C%20ACA%20%7C%20AXA-green)

---

## 🎯 Contexte métier

Ce dashboard reproduit le **reporting de suivi de portefeuille bancaire** utilisé dans les équipes quant / gestion de risques des banques :

> *"Quelles valeurs bancaires ont surperformé l'an passé ? Lesquelles sont trop volatiles pour mon portefeuille ? Est-ce que mes positions sont corrélées ? Quel est mon risque de perte maximale ?"*

Ce sont exactement les questions auxquelles répondent les 8 panneaux — avec les **indicateurs standards de l'analyse de risque** (Sharpe ratio, volatilité annualisée, Max Drawdown, corrélation de Pearson).

---

## 📈 KPIs générés — données réelles Yahoo Finance (12 mois)

| Indicateur | Description | Utilité métier |
|-----------|-------------|----------------|
| **Rendement total** | Performance sur 12 mois (cours réels) | Comparaison valeurs du portefeuille |
| **Volatilité annualisée** | σ journalier × √252 | Mesure du risque de marché |
| **Sharpe ratio** | (rend. − rf) / σ, rf = 3,5 % BCE | Rendement ajusté du risque |
| **Max Drawdown** | Perte max depuis le sommet | Pire scénario pour l'investisseur |
| **Corrélation** | Matrice Pearson rendements journaliers | Diversification du portefeuille |

---

## 🗂️ Les 8 panneaux du dashboard

```
┌──────────────────────────────────────────────────────────────┐
│  KPI Cards × 4  — rendement réel + Sharpe + volatilité      │
│  BNP Paribas · Soc. Générale · Crédit Agricole · AXA         │
├─────────────────────────┬──────────────────────────┬─────────┤
│  Cours normalisés       │  Rendements mensuels     │ Volati- │
│  base 100 — 12 mois     │  barres groupées (%)     │ lité %  │
│  (Yahoo Finance réel)   │  vert=positif, rouge=neg │ annuali-│
├─────────────────────────┼──────────────────────────┤ sée     │
│  Matrice de corrélation │  Distribution rendements │         │
│  rendements journaliers │  journaliers BNP Paribas │         │
│  heatmap RdYlGn         │  histogramme + moyenne   │         │
├─────────────────────────┴──────────────────────────┴─────────┤
│  Max Drawdown barres horizontales — 12 mois par valeur       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 Données réelles — Yahoo Finance

Les données sont téléchargées automatiquement via **yfinance** (Yahoo Finance API) au **premier lancement**, puis mises en cache localement pour les exécutions suivantes :

```python
TICKERS = {
    "BNP.PA": "BNP Paribas",
    "GLE.PA": "Soc. Generale",
    "ACA.PA": "Credit Agricole",
    "CS.PA":  "AXA",
}

# Téléchargement 1 fois → cache CSV local
closes = yf.download(tickers, period="1y", interval="1d", auto_adjust=True)
closes.to_csv("data/cac40_banques.csv")   # réutilisé ensuite sans internet
```

**Calculs dérivés :**
- **Rendements journaliers** : `pct_change()`
- **Rendements mensuels** : resample mensuel, dernier cours du mois
- **Volatilité annualisée** : `std_journalier × √252`
- **Sharpe simplifié** : taux sans risque BCE 2024 = 3,5 %
- **Max Drawdown** : `(cours − cummax) / cummax`

---

## 💡 Exemple de sortie console

```
[KPIs] Performance Bancaire CAC40 — 12 mois
Valeur               Rendement  Volatilite  Sharpe  Max Drawdown
-----------------------------------------------------------------
BNP Paribas           +18.4%       22.1%     0.71      -14.2%
Soc. Generale         +12.7%       26.3%     0.42      -19.8%
Credit Agricole        +9.3%       19.8%     0.35      -12.1%
AXA                   +21.6%       17.4%     1.09       -9.6%
```

---

## 💡 Cas d'usage réels similaires

Ce type de dashboard est produit dans les équipes BI / Risk des banques pour :

- **Comités de risques** — suivi de la volatilité et des drawdowns du portefeuille
- **Reporting Bâle III** — indicateurs de marché pour le calcul des exigences en fonds propres
- **Gestion d'actifs** — arbitrage entre valeurs bancaires selon Sharpe et corrélation
- **Stress testing** — analyse des drawdowns maximaux en scénario de crise

---

## ⚠️ Limites connues

**Univers limité à 4 valeurs.** Le dashboard couvre BNP.PA, GLE.PA, ACA.PA et CS.PA (AXA). Un portefeuille complet intégrerait l'ensemble du secteur financier CAC40 + europeen (STOXX Banks).

**Pas d'interactivité.** Le dashboard est statique (image PNG exportée). Une version interactive nécessiterait Plotly Dash, Streamlit, ou Power BI — outils courants en entreprise.

**Sharpe non calibré.** Le Sharpe simplifié utilise le taux BCE 2024 (~3,5 %) comme proxy du taux sans risque. Une implémentation rigoureuse utiliserait les OAT 10 ans à chaque date d'observation.

**Données ajustées.** yfinance retourne les cours `auto_adjust=True` (dividendes et splits inclus) — cohérent pour la mesure de performance totale, pas pour la reconstitution des cours côtés.

---

## 🗂️ Structure

```
dashboard-analytique/
├── dashboard.py               ← Script principal (8 graphiques — données réelles)
├── data/
│   ├── cac40_banques.csv      ← Cours réels Yahoo Finance (cache local)
│   ├── cours_cac40_banques.csv
│   ├── rendements_mensuels.csv
│   ├── volatilite.csv
│   └── correlation_matrix.csv
├── docs/
│   └── screenshot_dashboard.png
├── requirements.txt
└── README.md
```

## ⚙️ Lancement

```bash
pip install -r requirements.txt
python dashboard.py
# → Télécharge cours réels CAC40 (1ère fois) → génère dashboard_kpis.png + CSV dans data/
```

## 🛠️ Technologies

**Python 3** · **yfinance (Yahoo Finance API)** · **matplotlib** (GridSpec, FancyBboxPatch) · **pandas** · **numpy**

## 👩‍💻 Auteure

**Vanelle Stéphanie MANGOUA** — Recherche d'alternance en IA & Systèmes Embarqués
