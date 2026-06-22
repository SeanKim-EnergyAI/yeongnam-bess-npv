"""Build the real hour-of-day baseline SMP from your working-paper panel.

The shipped `data/baseline_smp_hourly.csv` is a stylized curve calibrated to the
KPX 2024 mainland average (~126 KRW/kWh). To replace it with *real* data, drop
your hourly panel (the one behind the regression) as a CSV and run:

    python3 -m src.data_prep path/to/panel.csv --smp-col smp --hour-col hour

It averages SMP by hour-of-day and overwrites data/baseline_smp_hourly.csv, so
the rest of the pipeline immediately runs on your real prices.
"""

import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "..", "data", "baseline_smp_hourly.csv")


def build_baseline_from_panel(panel: pd.DataFrame, smp_col: str,
                              hour_col: str) -> pd.Series:
    """Hour-of-day mean SMP (KRW/kWh), indexed 1..24."""
    baseline = (panel.groupby(hour_col)[smp_col]
                     .mean()
                     .rename("smp_krw_per_kwh")
                     .rename_axis("hour")
                     .sort_index())
    return baseline


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("panel_csv")
    ap.add_argument("--smp-col", default="smp")
    ap.add_argument("--hour-col", default="hour")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    panel = pd.read_csv(args.panel_csv)
    baseline = build_baseline_from_panel(panel, args.smp_col, args.hour_col)
    baseline.to_frame().reset_index().to_csv(args.out, index=False)
    print(f"Wrote {len(baseline)} hourly rows -> {os.path.normpath(args.out)}")
    print(f"Mean SMP: {baseline.mean():.1f} KRW/kWh")


if __name__ == "__main__":
    main()
