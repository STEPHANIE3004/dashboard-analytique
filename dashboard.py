"""
dashboard.py - Dashboard analytique KPIs business
Auteure : Vanelle Stephanie MANGOUA DJOUSSEU

Genere un rapport visuel complet (8 graphiques) a partir de donnees
synthetiques de type entreprise : ventes, produits, regions, satisfaction client.
"""

import numpy as np
import pandas as pd
import matplotlib
# matplotlib.use("Agg")  # desactive pour affichage fenetre
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import os

# --------------------------------------------------------------------------
# 1. Generation de donnees synthetiques
# --------------------------------------------------------------------------

def generer_donnees(seed=42):
    rng = np.random.RandomState(seed)
    mois   = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun",
               "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
    trimestres = ["T1"] * 3 + ["T2"] * 3 + ["T3"] * 3 + ["T4"] * 3

    produits = ["Pret Immobilier", "Compte Epargne", "Carte Premium",
                 "Assurance Vie", "Credit Conso"]
    regions  = ["Ile-de-France", "Auvergne-Rhone", "PACA", "Occitanie",
                 "Bretagne", "Nouvelle-Aquitaine"]

    # Serie temporelle CA mensuel
    base_ca = 12_000_000
    tendance = np.linspace(0, 3_000_000, 12)
    saisonnalite = np.array([0.8, 0.85, 1.0, 0.95, 1.05, 1.1,
                              0.9, 0.85, 1.05, 1.1, 1.15, 1.3])
    ca_mensuel = (base_ca * saisonnalite + tendance
                  + rng.normal(0, 400_000, 12)).astype(int)
    ca_budget  = (base_ca * saisonnalite * 0.95 + tendance).astype(int)

    # KPIs par produit
    ca_produit = rng.dirichlet([3, 5, 2, 4, 1]) * ca_mensuel.sum()
    nb_clients_produit = rng.randint(1500, 15000, len(produits))

    # KPIs par region
    ca_region = rng.dirichlet([5, 2, 2, 1, 1, 1]) * ca_mensuel.sum()
    satisfaction = rng.uniform(3.8, 4.9, len(regions))

    # Evolution satisfaction client (NPS)
    nps = np.clip(rng.normal(42, 8, 12) + np.linspace(0, 15, 12), 10, 80).astype(int)

    # Couts & marges
    couts  = ca_mensuel * rng.uniform(0.55, 0.65, 12)
    marges = ca_mensuel - couts

    # Funnel de conversion
    funnel_labels  = ["Leads", "Prospects qualifies", "Devis envoyes",
                       "Negociation", "Clients signes"]
    funnel_values  = [10000, 4500, 2100, 950, 420]

    df_mensuel = pd.DataFrame({
        "mois":       mois,
        "trimestre":  trimestres,
        "ca":         ca_mensuel,
        "budget":     ca_budget,
        "couts":      couts.astype(int),
        "marge":      marges.astype(int),
        "nps":        nps,
    })
    df_produit = pd.DataFrame({
        "produit":     produits,
        "ca":          ca_produit.astype(int),
        "nb_clients":  nb_clients_produit,
    })
    df_region = pd.DataFrame({
        "region":       regions,
        "ca":           ca_region.astype(int),
        "satisfaction": satisfaction.round(2),
    })
    return df_mensuel, df_produit, df_region, funnel_labels, funnel_values


# --------------------------------------------------------------------------
# 2. Calcul KPIs
# --------------------------------------------------------------------------

def calculer_kpis(df_mensuel, df_produit):
    ca_total     = df_mensuel["ca"].sum()
    ca_budget    = df_mensuel["budget"].sum()
    marge_tot    = df_mensuel["marge"].sum()
    taux_marge   = marge_tot / ca_total
    nps_moyen    = df_mensuel["nps"].mean()
    meilleur_mois = df_mensuel.loc[df_mensuel["ca"].idxmax(), "mois"]
    top_produit  = df_produit.loc[df_produit["ca"].idxmax(), "produit"]
    ecart_budget = (ca_total - ca_budget) / ca_budget

    print("\n[KPIs] Tableau de bord annuel")
    print("  CA total       : {:>15,.0f} EUR".format(ca_total))
    print("  Budget         : {:>15,.0f} EUR".format(ca_budget))
    print("  Ecart budget   : {:>14.1%}".format(ecart_budget))
    print("  Marge nette    : {:>14.1%}".format(taux_marge))
    print("  NPS moyen      : {:>15.1f}".format(nps_moyen))
    print("  Meilleur mois  : {}".format(meilleur_mois))
    print("  Top produit    : {}".format(top_produit))

    return {
        "ca_total": ca_total, "ca_budget": ca_budget,
        "taux_marge": taux_marge, "nps_moyen": nps_moyen,
        "ecart_budget": ecart_budget, "top_produit": top_produit,
    }


# --------------------------------------------------------------------------
# 3. Dashboard
# --------------------------------------------------------------------------

PALETTE = ["#003f5c", "#2f9e8f", "#bc5090", "#ffa600",
            "#58508d", "#ff6361"]

def ajouter_kpi_box(ax, titre, valeur, couleur="#003f5c", sous_titre=""):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    rect = FancyBboxPatch((0.05, 0.1), 0.9, 0.8,
                           boxstyle="round,pad=0.02",
                           facecolor=couleur, alpha=0.15,
                           edgecolor=couleur, linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.72, titre, ha="center", va="center",
            fontsize=9, color="#333333", fontweight="bold")
    ax.text(0.5, 0.42, valeur, ha="center", va="center",
            fontsize=16, color=couleur, fontweight="bold")
    if sous_titre:
        ax.text(0.5, 0.2, sous_titre, ha="center", va="center",
                fontsize=7.5, color="#666666")


def creer_dashboard(df_mensuel, df_produit, df_region,
                     funnel_labels, funnel_values, kpis):
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor("#f8f9fa")
    fig.suptitle("DASHBOARD ANALYTIQUE - KPIs Business",
                  fontsize=18, fontweight="bold", color="#003f5c", y=0.98)

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.5, wspace=0.4)

    # ── Ligne 1 : KPI boxes ──────────────────────────────────────────────
    ax_k1 = fig.add_subplot(gs[0, 0])
    ax_k2 = fig.add_subplot(gs[0, 1])
    ax_k3 = fig.add_subplot(gs[0, 2])
    ax_k4 = fig.add_subplot(gs[0, 3])

    ajouter_kpi_box(ax_k1, "CA Annuel Total",
                     "{:,.0f} EUR".format(kpis["ca_total"]), "#003f5c",
                     "vs budget : {:+.1%}".format(kpis["ecart_budget"]))
    ajouter_kpi_box(ax_k2, "Taux de Marge",
                     "{:.1%}".format(kpis["taux_marge"]), "#2f9e8f",
                     "Marge nette annuelle")
    ajouter_kpi_box(ax_k3, "NPS Moyen",
                     "{:.0f} / 100".format(kpis["nps_moyen"]), "#bc5090",
                     "Net Promoter Score")
    ajouter_kpi_box(ax_k4, "Top Produit",
                     kpis["top_produit"].replace(" ", "\n"), "#ffa600",
                     "Meilleure contribution CA")

    # ── Ligne 2 : CA mensuel + CA vs budget ─────────────────────────────
    ax2a = fig.add_subplot(gs[1, 0:2])
    x    = np.arange(len(df_mensuel))
    bars = ax2a.bar(x, df_mensuel["ca"] / 1e6, color=PALETTE[0], alpha=0.8,
                     label="CA reel")
    ax2a.plot(x, df_mensuel["budget"] / 1e6, "o--", color="#ffa600",
               linewidth=2, label="Budget", zorder=5)
    ax2a.set_xticks(x)
    ax2a.set_xticklabels(df_mensuel["mois"], fontsize=8)
    ax2a.set_ylabel("CA (M EUR)")
    ax2a.set_title("CA Mensuel vs Budget", fontweight="bold")
    ax2a.legend(fontsize=8)
    ax2a.grid(axis="y", alpha=0.3)
    ax2a.set_facecolor("#fdfdfd")

    # ── Ligne 2 : Repartition CA par produit ────────────────────────────
    ax2b = fig.add_subplot(gs[1, 2])
    wedges, texts, autotexts = ax2b.pie(
        df_produit["ca"],
        labels=None,
        autopct="%1.1f%%",
        colors=PALETTE,
        startangle=140,
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontsize(7.5)
    ax2b.legend(df_produit["produit"], loc="lower left",
                 fontsize=6.5, bbox_to_anchor=(-0.3, -0.15))
    ax2b.set_title("Part de CA par Produit", fontweight="bold")

    # ── Ligne 2 : Evolution NPS ─────────────────────────────────────────
    ax2c = fig.add_subplot(gs[1, 3])
    ax2c.fill_between(df_mensuel["mois"], df_mensuel["nps"],
                       alpha=0.3, color="#bc5090")
    ax2c.plot(df_mensuel["mois"], df_mensuel["nps"],
               "o-", color="#bc5090", linewidth=2)
    ax2c.axhline(50, color="gray", linestyle="--", alpha=0.5, label="NPS cible=50")
    ax2c.set_ylabel("NPS")
    ax2c.set_title("Evolution NPS", fontweight="bold")
    ax2c.tick_params(axis="x", rotation=45, labelsize=7)
    ax2c.legend(fontsize=7)
    ax2c.grid(alpha=0.3)
    ax2c.set_facecolor("#fdfdfd")

    # ── Ligne 3 : Marge mensuelle ────────────────────────────────────────
    ax3a = fig.add_subplot(gs[2, 0:2])
    ax3a.bar(df_mensuel["mois"], df_mensuel["marge"] / 1e6,
              color="#2f9e8f", alpha=0.8, label="Marge")
    ax3a.plot(df_mensuel["mois"], df_mensuel["ca"] / 1e6,
               "s--", color=PALETTE[0], linewidth=1.5, label="CA")
    ax3a.set_ylabel("M EUR")
    ax3a.set_title("Marge & CA mensuel", fontweight="bold")
    ax3a.legend(fontsize=8)
    ax3a.tick_params(axis="x", rotation=30, labelsize=8)
    ax3a.grid(axis="y", alpha=0.3)
    ax3a.set_facecolor("#fdfdfd")

    # ── Ligne 3 : Funnel de conversion ──────────────────────────────────
    ax3b = fig.add_subplot(gs[2, 2])
    y_pos = np.arange(len(funnel_labels))
    colors_funnel = ["#003f5c", "#2f4b7c", "#665191",
                      "#a05195", "#d45087"]
    bars3 = ax3b.barh(y_pos, funnel_values, color=colors_funnel, height=0.6)
    ax3b.set_yticks(y_pos)
    ax3b.set_yticklabels(funnel_labels, fontsize=8)
    ax3b.set_xlabel("Nombre")
    ax3b.set_title("Funnel de Conversion", fontweight="bold")
    for bar, val in zip(bars3, funnel_values):
        ax3b.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                   "{:,}".format(val), va="center", fontsize=8)
    ax3b.grid(axis="x", alpha=0.3)
    ax3b.set_facecolor("#fdfdfd")

    # ── Ligne 3 : CA et satisfaction par region ──────────────────────────
    ax3c = fig.add_subplot(gs[2, 3])
    sc = ax3c.scatter(
        df_region["ca"] / 1e6,
        df_region["satisfaction"],
        s=200,
        c=range(len(df_region)),
        cmap="viridis",
        zorder=5,
    )
    for _, row in df_region.iterrows():
        ax3c.annotate(row["region"].split("-")[0],
                       (row["ca"] / 1e6, row["satisfaction"]),
                       fontsize=6.5, xytext=(4, 4),
                       textcoords="offset points")
    ax3c.set_xlabel("CA (M EUR)")
    ax3c.set_ylabel("Satisfaction client")
    ax3c.set_title("CA vs Satisfaction (region)", fontweight="bold")
    ax3c.grid(alpha=0.3)
    ax3c.set_facecolor("#fdfdfd")

    out = "dashboard_kpis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight",
                 facecolor=fig.get_facecolor())
    print("[VIZ] Dashboard sauvegarde : {}".format(out))
    return out


# --------------------------------------------------------------------------
# 4. Export rapport CSV
# --------------------------------------------------------------------------

def exporter_rapport(df_mensuel, df_produit, df_region, kpis):
    os.makedirs("data", exist_ok=True)
    df_mensuel.to_csv("data/kpis_mensuel.csv", index=False)
    df_produit.to_csv("data/kpis_produit.csv", index=False)
    df_region.to_csv("data/kpis_region.csv",  index=False)
    with open("data/synthese_kpis.json", "w") as f:
        import json
        json.dump({k: str(v) for k, v in kpis.items()}, f, indent=2)
    print("[EXPORT] Rapports CSV/JSON sauvegardes dans data/")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("   DASHBOARD ANALYTIQUE - KPIs Business")
    print("=" * 60)

    df_mensuel, df_produit, df_region, fl, fv = generer_donnees()
    kpis = calculer_kpis(df_mensuel, df_produit)
    creer_dashboard(df_mensuel, df_produit, df_region, fl, fv, kpis)
    exporter_rapport(df_mensuel, df_produit, df_region, kpis)

    print("\n[DONE] Fichiers generes :")
    print("  - dashboard_kpis.png")
    print("  - data/kpis_mensuel.csv")
    print("  - data/kpis_produit.csv")
    print("  - data/kpis_region.csv")
    print("  - data/synthese_kpis.json")


if __name__ == "__main__":
    main()
