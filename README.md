# Dashboard Analytique - KPIs Business

Dashboard de reporting analytique complet genere en Python avec matplotlib.
Simule un tableau de bord business pour un portefeuille de produits financiers.

## Fonctionnalites

- 4 KPI cards : CA total, taux de marge, NPS, top produit
- Courbe CA mensuel vs budget
- Pie chart de repartition CA par produit
- Evolution NPS avec cible
- Analyse marge mensuelle
- Funnel de conversion commerciale
- Scatter CA vs satisfaction client par region
- Export automatique CSV + JSON

## Structure

```
dashboard-analytique/
├── dashboard.py         # Script principal
├── data/
│   ├── kpis_mensuel.csv
│   ├── kpis_produit.csv
│   ├── kpis_region.csv
│   └── synthese_kpis.json
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python dashboard.py
```

Genere `dashboard_kpis.png` (8 graphiques en un seul rapport) + fichiers CSV/JSON.

## Exemple de KPIs produits

| KPI | Valeur |
|-----|--------|
| CA Annuel | 164,6 M EUR |
| Ecart budget | +5.6% |
| Marge nette | 39.9% |
| NPS moyen | 46.6 / 100 |

## Technologies

- Python 3.x
- matplotlib (visualisations)
- pandas / numpy (agregations)
- json (export)

## Auteure

Vanelle Stephanie MANGOUA DJOUSSEU
Etudiante en IA & Systemes Embarques - Recherche d'alternance
