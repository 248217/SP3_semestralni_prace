import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy import stats


def quantile_analysis(model, dependent="poměr", covariates=["věk", "pohlaví"], quantiles=[0.1, 0.25, 0.5, 0.75, 0.9], bootstrap=1000):
    """
    Kvantilová regrese pro analýzu poměru s ohledem na pohlaví a věk.
    Provádí:
    - kvantilovou regresi
    - Waldovy testy významnosti koeficientů
    - Waldův test shody se zlatým řezem (φ)
    Výsledky ukládá do .txt a grafy do .png.
    """

    # zlatý řez
    phi = (1 + np.sqrt(5)) / 2

    data = model.data.copy()

    # ------------------------------------------------------------
    # Převod kategoriálních proměnných
    # ------------------------------------------------------------
    for var in covariates:
        data[var] = data[var].astype("category")

    # ------------------------------------------------------------
    # Regresní formule
    # ------------------------------------------------------------
    formula = f"{dependent} ~ " + " + ".join(covariates)

    # ------------------------------------------------------------
    # Výstupní složky
    # ------------------------------------------------------------
    base_dir = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.join(base_dir, "vystupy", "QR")
    os.makedirs(out_dir, exist_ok=True)

    txt_path = os.path.join(out_dir, f"kvantilova_regrese_{dependent}.txt")

    # ------------------------------------------------------------
    # Kvantilová regrese + testy
    # ------------------------------------------------------------
    mod = smf.quantreg(formula, data)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("KVANTILOVÁ REGRESE – TESTY VÝZNAMNOSTI\n")
        f.write("====================================\n\n")
        f.write(f"Zlatý řez φ = {phi:.6f}\n")
        f.write(f"Regresní formule: {formula}\n\n")

        for q in quantiles:
            f.write(f"\n--- KVANTIL τ = {q} ---\n\n")

            res = mod.fit(q=q, cov_type="boot", bootstrap=bootstrap)
            f.write(res.summary().as_text())
            f.write("\n\n")

            # ------------------------------------------------
            # Test shody interceptu se zlatým řezem
            # ------------------------------------------------
            intercept = res.params["Intercept"]
            se = res.bse["Intercept"]

            t_stat = (intercept - phi) / se
            p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))

            f.write("Test shody referenční skupiny se zlatým řezem (Waldův test):\n")
            f.write(f"H0: Q_{q}(poměr) = φ\n")
            f.write(f"Odhad interceptu: {intercept:.4f}\n")
            f.write(f"t-statistika: {t_stat:.3f}\n")
            f.write(f"p-hodnota: {p_value:.4f}\n")

            if p_value < 0.05:
                f.write("→ H0 zamítáme: kvantil se významně liší od φ.\n\n")
            else:
                f.write("→ H0 nezamítáme: kvantil se statisticky neliší od φ.\n\n")

    print(f"Textový výstup uložen: {txt_path}")

    # ------------------------------------------------------------
    # Grafy kvantilové regrese  
    # ------------------------------------------------------------ 
    plot_quantile_predictions(
        data=data,
        dependent=dependent,
        covariates=covariates,
        quantiles=quantiles,
        out_dir=out_dir,
        phi=phi
    )


def plot_quantile_predictions(data, dependent, covariates, quantiles, out_dir, phi):

    for cov in covariates:
        plt.figure(figsize=(8, 5))

        plt.axhline(
            y=phi,
            linestyle="--",
            linewidth=2,
            label="Zlatý řez φ"
        )

        categories = data[cov].cat.categories
        x = np.arange(len(categories))

        for q in quantiles:
            formula = f"{dependent} ~ {cov}"
            mod = smf.quantreg(formula, data)
            res = mod.fit(q=q)

            preds = [
                res.predict(pd.DataFrame({cov: [cat]}))[0]
                for cat in categories
            ]

            plt.plot(x, preds, marker="o", label=f"Kvantil {q}")

        plt.xticks(x, categories)
        plt.xlabel(cov)
        plt.ylabel(dependent)
        plt.title(f"Kvantilová regrese podle {cov}")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        path = os.path.join(out_dir, f"kvantilova_regrese_{dependent}_{cov}.png")
        plt.savefig(path, dpi=200)
        plt.close()

        print(f"Graf uložen: {path}")
