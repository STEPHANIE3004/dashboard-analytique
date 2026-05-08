"""
dashboard.py - Dashboard analytique — Performance Bancaire CAC40
Auteure : Vanelle Stephanie MANGOUA DJOUSSEU

Donnees : Yahoo Finance API (yfinance) — cours reels sur 12 mois
Valeurs : BNP Paribas (BNP.PA), Societe Generale (GLE.PA),
          Credit Agricole (ACA.PA), AXA (CS.PA)
Analyse : rendements mensuels reels, volatilite, correlations, KPIs marche

Cache local : data/cac40_banques.csv — telecharge 1 fois, reutilise ensuite.
Source      : Yahoo Finance (https://finance.yahoo.com)
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import os
import warnings
warnings.filterwarnings("ignore")

# Valeurs bancaires CAC40 suivies
TICKERS = {
    "BNP.PA":  "BNP Paribas",
    "GLE.PA":  "Soc. Generale",
    "ACA.PA":  "Credit Agricole",
    "CS.PA":   "AXA",
}
PALETTE = ["#003f5c", "#2f9e8f", "#bc5090", "#ffa600", "#58508d", "#ff6361"]


# --------------------------------------------------------------------------
# 1. Chargement des donnees reelles (Yahoo Finance)
# --------------------------------------------------------------------------

def charger_donnees_reelles(csv_cache="data/cac40_banques.csv", periode="1y"):
    """
    Charge les cours de cloture ajustes sur 12 mois pour 4 banques CAC40.
    Premier lancement : telechargement Yahoo Finance (~100KB).
    Lancements suivants : lecture directe du CSV local (pas d'internet).
    """
    os.makedirs("data", exist_ok=True)

    if os.path.exists(csv_cache):
        print("[DATA] Lecture cache local : {}".format(csv_cache))
        df = pd.read_csv(csv_cache, index_col=0, parse_dates=True)
        print("[DATA] {} jours x {} valeurs chargees".format(len(df), len(df.columns)))
        return df

    try:
        import yfinance as yf
        print("[DATA] Telechargement Yahoo Finance — {} valeurs bancaires CAC40...".format(
            len(TICKERS)))
        tickers_list = list(TICKERS.keys())
        data = yf.download(tickers_list, period=periode, interval="1d",
                           progress=False, auto_adjust=True)
        closes = data["Close"].dropna(how="all")
        closes.columns = [TICKERS.get(c, c) for c in closes.columns]
        closes.to_csv(csv_cache)
        print("[DATA] Cours reels sauvegardes : {}".format(csv_cache))
        print("[DATA] {} jours x {} valeurs".format(len(closes), len(closes.columns)))
        return closes
    except Exception as e:
        print("[ERREUR] yfinance indisponible : {}".format(e))
        print("[ERREUR] Installer : pip install yfinance")
        raise


def preparer_donnees(closes):
    """
    Calcule les indicateurs derives a partir des cours reels :
    - Rendements journaliers et mensuels
    - Volatilite annualisee
    - Matrice de correlation
    - KPIs synthetiques par valeur
    """
    # Rendements journaliers
    returns_daily = closes.pct_change().dropna()

    # Agregation mensuelle (dernier cours du mois)
    closes_monthly = closes.resample("ME").last()
    returns_monthly = closes_monthly.pct_change().dropna()

    # Volatilite annualisee (std journalier * sqrt(252))
    volatilite = returns_daily.std() * np.sqrt(252)

    # Rendement total sur la periode
    rendement_total = (closes.iloc[-1] / closes.iloc[0] - 1)

    # Sharpe simplifie (taux sans risque ~3.5% BCE 2024)
    rf = 0.035 / 252
    sharpe = ((returns_daily.mean() - rf) / returns_daily.std()) * np.sqrt(252)

    # Drawdown maximum
    def max_drawdown(serie):
        peak = serie.cummax()
        dd = (serie - peak) / peak
        return dd.min()
    drawdowns = {col: max_drawdown(closes[col].dropna()) for col in closes.columns}

    # Correlation
    corr_matrix = returns_daily.corr()

    return {
        "closes":          closes,
        "closes_monthly":  closes_monthly,
        "returns_daily":   returns_daily,
        "returns_monthly": returns_monthly,
        "volatilite":      volatilite,
        "rendement_total": rendement_total,
        "sharpe":          sharpe,
        "drawdowns":       pd.Series(drawdowns),
        "corr_matrix":     corr_matrix,
    }


def calculer_kpis(data):
    """Affiche les KPIs marche principaux."""
    print("\n[KPIs] Performance Bancaire CAC40 — 12 mois")
    print("{:<20} {:>10} {:>10} {:>10} {:>12}".format(
        "Valeur", "Rendement", "Volatilite", "Sharpe", "Max Drawdown"))
    print("-" * 65)
    for col in data["closes"].columns:
        r = data["rendement_total"].get(col, np.nan)
        v = data["volatilite"].get(col, np.nan)
        s = data["sharpe"].get(col, np.nan)
        d = data["drawdowns"].get(col, np.nan)
        print("{:<20} {:>+9.1%} {:>10.1%} {:>10.2f} {:>12.1%}".format(
            col, r, v, s, d))
    return data


# --------------------------------------------------------------------------
# 2. Dashboard
# --------------------------------------------------------------------------

def ajouter_kpi_box(ax, titre, valeur, couleur="#003f5c", sous_titre=""):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    rect = FancyBboxPatch((0.05, 0.1), 0.9, 0.8, boxstyle="round,pad=0.02",
                           facecolor=couleur, alpha=0.15,
                           edgecolor=couleur, linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.72, titre, ha="center", va="center",
            fontsize=9, color="#333333", fontweight="bold")
    ax.text(0.5, 0.42, valeur, ha="center", va="center",
            fontsize=15, color=couleur, fontweight="bold")
    if sous_titre:
        ax.text(0.5, 0.2, sous_titre, ha="center", va="center",
                fontsize=7.5, color="#666666")


def creer_dashboard(data):
    closes   = data["closes"]
    ret_m    = data["returns_monthly"]
    ret_d    = data["returns_daily"]
    vol      = data["volatilite"]
    rend     = data["rendement_total"]
    sharpe   = data["sharpe"]
    corr     = data["corr_matrix"]
    dd       = data["drawdowns"]
    valeurs  = list(closes.columns)

    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor("#f8f9fa")
    fig.suptitle("DASHBOARD ANALYTIQUE — Performance Bancaire CAC40\n"
                 "BNP Paribas · Soc. Generale · Credit Agricole · AXA  |  Source : Yahoo Finance",
                 fontsize=15, fontweight="bold", color="#003f5c", y=0.98)

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.52, wspace=0.40)

    # ── Ligne 1 : KPI boxes (rendement reel par valeur) ─────────────────
    couleurs_kpi = ["#003f5c", "#2f9e8f", "#bc5090", "#ffa600"]
    for i, (val, col) in enumerate(zip(valeurs, couleurs_kpi)):
        ax = fig.add_subplot(gs[0, i])
        r  = rend.get(val, np.nan)
        s  = sharpe.get(val, np.nan)
        signe = "+" if r >= 0 else ""
        ajouter_kpi_box(ax, val,
                         "{}{:.1%}".format(signe, r), col,
                         "Sharpe : {:.2f} | Vol : {:.0%}".format(
                             s, vol.get(val, np.nan)))

    # ── Ligne 2a : Cours normalises (base 100) ──────────────────────────
    ax2a = fig.add_subplot(gs[1, 0:2])
    closes_norm = closes / closes.iloc[0] * 100
    for i, col in enumerate(valeurs):
        ax2a.plot(closes_norm.index, closes_norm[col],
                   label=col, color=PALETTE[i], linewidth=1.8)
    ax2a.axhline(100, color="gray", linestyle="--", alpha=0.4, linewidth=1)
    ax2a.set_title("Cours normalises base 100 — 12 mois (Yahoo Finance)", fontweight="bold")
    ax2a.set_ylabel("Valeur relative")
    ax2a.legend(fontsize=8)
    ax2a.grid(alpha=0.25)
    ax2a.set_facecolor("#fdfdfd")
    ax2a.tick_params(axis="x", rotation=20, labelsize=7)

    # ── Ligne 2b : Rendements mensuels barres groupees ───────────────────
    ax2b = fig.add_subplot(gs[1, 2])
    x = np.arange(len(ret_m))
    w = 0.2
    for i, col in enumerate(valeurs):
        vals = ret_m[col].values if col in ret_m.columns else np.zeros(len(x))
        colors_bar = ["#2f9e8f" if v >= 0 else "#d62728" for v in vals]
        ax2b.bar(x + i * w, vals * 100, w, color=colors_bar, alpha=0.8, label=col)
    ax2b.axhline(0, color="black", linewidth=0.8)
    ax2b.set_title("Rendements mensuels (%)", fontweight="bold")
    ax2b.set_ylabel("%")
    ax2b.legend(fontsize=6.5)
    ax2b.grid(axis="y", alpha=0.3)
    ax2b.set_facecolor("#fdfdfd")
    mois_labels = [str(d)[:7] for d in ret_m.index]
    ax2b.set_xticks(x + w * 1.5)
    ax2b.set_xticklabels(mois_labels, rotation=45, fontsize=6)

    # ── Ligne 2c : Volatilite annualisee ────────────────────────────────
    ax2c = fig.add_subplot(gs[1, 3])
    vol_vals = [vol.get(v, 0) * 100 for v in valeurs]
    bars = ax2c.bar(valeurs, vol_vals,
                     color=[PALETTE[i] for i in range(len(valeurs))], alpha=0.85)
    for bar, v in zip(bars, vol_vals):
        ax2c.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                   "{:.1f}%".format(v), ha="center", fontsize=8, fontweight="bold")
    ax2c.set_title("Volatilite annualisee (%)", fontweight="bold")
    ax2c.set_ylabel("Volatilite (%)")
    ax2c.tick_params(axis="x", rotation=15, labelsize=8)
    ax2c.grid(axis="y", alpha=0.3)
    ax2c.set_facecolor("#fdfdfd")

    # ── Ligne 3a : Matrice de correlation ───────────────────────────────
    ax3a = fig.add_subplot(gs[2, 0:2])
    im = ax3a.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    ax3a.set_xticks(range(len(valeurs)))
    ax3a.set_yticks(range(len(valeurs)))
    ax3a.set_xticklabels(valeurs, rotation=20, fontsize=8)
    ax3a.set_yticklabels(valeurs, fontsize=8)
    for i in range(len(valeurs)):
        for j in range(len(valeurs)):
            ax3a.text(j, i, "{:.2f}".format(corr.values[i, j]),
                       ha="center", va="center", fontsize=9, fontweight="bold",
                       color="black")
    fig.colorbar(im, ax=ax3a, fraction=0.046, pad=0.04)
    ax3a.set_title("Matrice de correlation des rendements journaliers", fontweight="bold")

    # ── Ligne 3b : Distribution rendements journaliers BNP ──────────────
    ax3b = fig.add_subplot(gs[2, 2])
    col0 = valeurs[0]
    rd   = ret_d[col0].dropna() * 100
    ax3b.hist(rd, bins=40, color=PALETTE[0], alpha=0.75, edgecolor="white", linewidth=0.3)
    ax3b.axvline(rd.mean(), color="red", linestyle="--", linewidth=1.5,
                  label="Moyenne : {:.2f}%".format(rd.mean()))
    ax3b.axvline(0, color="black", linewidth=0.8, alpha=0.5)
    ax3b.set_xlabel("Rendement journalier (%)")
    ax3b.set_ylabel("Frequence")
    ax3b.set_title("Distribution rendements — {}".format(col0), fontweight="bold")
    ax3b.legend(fontsize=8)
    ax3b.grid(alpha=0.3)
    ax3b.set_facecolor("#fdfdfd")

    # ── Ligne 3c : Max Drawdown ──────────────────────────────────────────
    ax3c = fig.add_subplot(gs[2, 3])
    dd_vals = [dd.get(v, 0) * 100 for v in valeurs]
    bars3 = ax3c.barh(valeurs, dd_vals,
                       color=["#d62728" if v < 0 else "#2f9e8f" for v in dd_vals],
                       alpha=0.85)
    for bar, v in zip(bars3, dd_vals):
        ax3c.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height() / 2,
                   "{:.1f}%".format(v), va="center", ha="right",
                   fontsize=9, fontweight="bold", color="white")
    ax3c.axvline(0, color="black", linewidth=0.8)
    ax3c.set_xlabel("Drawdown (%)")
    ax3c.set_title("Maximum Drawdown — 12 mois", fontweight="bold")
    ax3c.grid(axis="x", alpha=0.3)
    ax3c.set_facecolor("#fdfdfd")

    out = "dashboard_kpis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print("[VIZ] Dashboard sauvegarde : {}".format(out))
    return out


# --------------------------------------------------------------------------
# 3. Export CSV
# --------------------------------------------------------------------------

def exporter_rapport(data):
    os.makedirs("data", exist_ok=True)
    data["closes"].to_csv("data/cours_cac40_banques.csv")
    data["returns_monthly"].to_csv("data/rendements_mensuels.csv")
    data["volatilite"].to_frame("volatilite_annualisee").to_csv("data/volatilite.csv")
    data["corr_matrix"].to_csv("data/correlation_matrix.csv")
    print("[EXPORT] CSV sauvegardes dans data/")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print("=" * 65)
    print("   DASHBOARD ANALYTIQUE — Performance Bancaire CAC40")
    print("   Source : Yahoo Finance (cours reels 12 mois)")
    print("=" * 65)

    closes = charger_donnees_reelles()
    data   = preparer_donnees(closes)
    calculer_kpis(data)
    creer_dashboard(data)
    exporter_rapport(data)

    print("\n[DONE] Fichiers generes :")
    print("  - dashboard_kpis.png          (8 graphiques — donnees reelles)")
    print("  - data/cac40_banques.csv      (cours bruts Yahoo Finance)")
    print("  - data/rendements_mensuels.csv")
    print("  - data/volatilite.csv")
    print("  - data/correlation_matrix.csv")


if __name__ == "__main__":
    main()
