# 📊 Dashboard Analytique — Reporting KPIs Produits Financiers

Dashboard de reporting automatisé généré en Python : 8 graphiques couvrant CA, marges, NPS, satisfaction client et funnel de conversion — pour un portefeuille de produits bancaires/assurance.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![matplotlib](https://img.shields.io/badge/matplotlib-dashboard%208%20panneaux-orange)
![Finance](https://img.shields.io/badge/Domaine-Banque%20%2F%20Assurance-green)

---

## 🎯 Contexte métier

Ce dashboard simule l'outil de pilotage mensuel d'une **direction commerciale bancaire** (ou assurance) qui gère plusieurs lignes de produits :

> *"Chaque mois, le COMEX veut voir : est-ce qu'on est au budget ? Quels produits portent la croissance ? Où sont les problèmes de satisfaction ? Quel est notre taux de transformation commercial ?"*

Ce sont exactement les questions auxquelles répondent les 8 panneaux générés — avec les indicateurs standards du reporting bancaire (CA vs budget, NPS, marge nette, funnel commercial).

---

## 📈 KPIs générés — et ce qu'ils mesurent

| Indicateur | Valeur simulée | Utilité métier |
|-----------|---------------|----------------|
| **CA Annuel** | 164,6 M EUR | Vision globale de l'activité commerciale |
| **Écart budget** | **+5,6 %** | Alerter si on décroche de l'objectif fixé |
| **Marge nette** | **39,9 %** | Rentabilité réelle après coûts opérationnels |
| **NPS moyen** | 46,6 / 100 | Proxy de fidélisation et de risque de churn |
| **Top produit** | Assurance Vie | Arbitrage budgétaire et force commerciale |
| **Meilleur mois** | Décembre | Saisonnalité — planification campagnes |

---

## 🗂️ Les 8 panneaux du dashboard

```
┌─────────────────────────┬──────────────────────────┐
│  KPI Cards (4 blocs)    │  CA mensuel vs budget    │
│  CA · Marge · NPS · Top │  + visualisation écarts  │
├─────────────────────────┼──────────────────────────┤
│  Répartition CA         │  Évolution NPS mensuel   │
│  par produit (pie)      │  + cible (courbe)        │
├─────────────────────────┼──────────────────────────┤
│  Marge mensuelle        │  Funnel de conversion    │
│  superposée au CA       │  Leads → Clients signés  │
├─────────────────────────┼──────────────────────────┤
│  Scatter CA vs          │  Export CSV + JSON       │
│  satisfaction/région    │  (données structurées)   │
└─────────────────────────┴──────────────────────────┘
```

---

## 🔧 Données simulées — pourquoi ce choix

Les données sont générées avec des distributions réalistes :

- **CA mensuel** : base × saisonnalité (pic décembre +30 %) + tendance annuelle + bruit gaussien
- **Revenus par produit** : distribution Dirichlet (allocation réaliste sur 5 produits)
- **NPS** : évolution progressive avec variance (simulation d'une amélioration sur l'année)
- **Funnel** : taux de conversion 4,2 % Leads → Clients (réaliste secteur bancaire)

```python
# Exemple : saisonnalité bancaire modélisée
saisonnalite = np.array([0.8, 0.85, 1.0, 0.95, 1.05, 1.1,
                          0.9, 0.85, 1.05, 1.1, 1.15, 1.3])
# Pic janvier/décembre pour épargne, été creux pour crédits
```

---

## 💡 Cas d'usage réels similaires

Ce type de dashboard est produit dans les équipes BI / Data des banques pour :

- **Comités commerciaux mensuels** — slides automatisées depuis les données CRM
- **Reporting régulation** — transmission des KPIs à l'ACPR ou au groupe
- **Pilotage réseau agences** — comparaison régions, identification des sous-performeurs
- **Suivi plan stratégique** — écart réel vs budget sur l'année glissante

---

## ⚠️ Limites connues

**Données entièrement synthétiques.** Ce dashboard démontre la construction du pipeline de reporting (agrégation, visualisation, export), pas l'analyse de données réelles. Un branchement sur une vraie source (base SQL, API CRM, fichier de consolidation) est l'étape suivante naturelle.

**Pas d'interactivité.** Le dashboard est statique (image PNG exportée). Une version interactive nécessiterait Plotly Dash, Streamlit, ou Power BI — outils courants en entreprise.

**NPS simplifié.** Le Net Promoter Score réel se calcule sur des enquêtes structurées (promoteurs − détracteurs) / total. Ici il est simulé comme variable continue — la logique de visualisation reste identique.

---

## 🗂️ Structure

```
dashboard-analytique/
├── dashboard.py           ← Script principal (génération + 8 graphiques)
├── data/
│   ├── kpis_mensuel.csv   ← Série temporelle CA/marges/NPS
│   ├── kpis_produit.csv   ← KPIs par ligne de produit
│   ├── kpis_region.csv    ← KPIs par région commerciale
│   └── synthese_kpis.json ← Synthèse JSON (intégrable API)
├── docs/
│   └── screenshot_dashboard.png
├── requirements.txt
└── README.md
```

## ⚙️ Lancement

```bash
pip install -r requirements.txt
python dashboard.py
# → Génère dashboard_kpis.png (8 graphiques) + exports CSV/JSON dans data/
```

## 🛠️ Technologies

**Python 3** · **matplotlib** (GridSpec, FancyBboxPatch) · **pandas** · **numpy** · **json**

## 👩‍💻 Auteure

**Vanelle Stéphanie MANGOUA** — Recherche d'alternance en IA & Systèmes Embarqués
