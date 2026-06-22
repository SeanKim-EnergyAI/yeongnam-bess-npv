"""Build the model's real inputs from the Phase 1/2 research files.

Reads the working-paper panel and the hourly HTE estimates, then writes three
small hour-of-day CSVs into data/. Only these aggregates live in this repo; the
raw 140k-row panel stays in the separate research project.

    python3 scripts/build_inputs_from_panel.py \
        --panel "~/Desktop/korea_iv_project/Claude V4/panel_v4_main.csv" \
        --hte   "~/Desktop/korea_iv_project/Claude V4/v4_phase2_hte.csv"

Outputs:
    data/baseline_smp_hourly.csv  - national hour-of-day mean SMP (KRW/kWh), 2024
    data/solar_profile_hourly.csv - national hour-of-day mean solar generation (MWh)
    data/elasticities.csv         - hourly log(SMP)~log(Solar) IV coefficients

SMP is a single national price, so we de-duplicate to one row per (date, hour)
before averaging. Hours with no identified IV coefficient (pre-dawn, where solar
generation is ~0) are set to 0: we do not claim a solar price effect at hours
when there is essentially no solar.
"""

import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def national_hourly(panel: pd.DataFrame, value_col: str) -> pd.Series:
    one_per_hour = panel.drop_duplicates(["date", "hour"])
    return one_per_hour.groupby("hour")[value_col].mean()


def build_elasticities(hte: pd.DataFrame, hours=range(1, 25)) -> pd.Series:
    estimated = hte.set_index("hour")["iv_coef"]
    full = pd.Series(0.0, index=pd.Index(list(hours), name="hour"))
    full.loc[estimated.index] = estimated.values
    return full


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--panel", required=True)
    ap.add_argument("--hte", required=True)
    args = ap.parse_args()

    panel = pd.read_csv(os.path.expanduser(args.panel))
    hte = pd.read_csv(os.path.expanduser(args.hte))

    baseline = national_hourly(panel, "smp").round(2)
    solar = national_hourly(panel, "solar_total").round(1)
    elasticities = build_elasticities(hte).round(6)

    (baseline.rename("smp_krw_per_kwh").rename_axis("hour")
             .reset_index().to_csv(os.path.join(DATA, "baseline_smp_hourly.csv"), index=False))
    (solar.rename("solar_mwh").rename_axis("hour")
          .reset_index().to_csv(os.path.join(DATA, "solar_profile_hourly.csv"), index=False))
    (elasticities.rename("elasticity").rename_axis("hour")
                 .reset_index().to_csv(os.path.join(DATA, "elasticities.csv"), index=False))

    print(f"Baseline SMP : mean {baseline.mean():.1f} KRW/kWh | "
          f"cheapest {list(baseline.nsmallest(4).index)} | dearest {list(baseline.nlargest(4).index)}")
    print(f"Solar (MWh)  : peak hour {int(solar.idxmax())} ({solar.max():.0f}), "
          f"night hours ~{solar.loc[[1, 2, 3, 24]].mean():.1f}")
    print(f"Elasticities : {(elasticities != 0).sum()} hours identified, "
          f"min {elasticities.min():.4f} (h{int(elasticities.idxmin())}), "
          f"max {elasticities.max():.4f} (h{int(elasticities.idxmax())})")


if __name__ == "__main__":
    main()
