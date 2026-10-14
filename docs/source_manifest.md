# Source manifest — how to obtain the source files without them being in the repository

The external source documents (official notices, rules, KEC and NREL ATB files,
and their page excerpts) are **not stored in this repository**. They are listed
in `.gitignore` by name.

Two things are kept apart:

- **Running the calculations does not need them.** No code reads `docs/sources/`.
  Values taken from these documents are written into the code as constants,
  with the cell or page cited (`src/contract_case.py`, `src/assumptions.py`).
  `run_all.sh` and the tests run from a checkout without `docs/sources/`.
- **Checking where an assumption comes from does need them.** To verify a cited
  value, page or formula, obtain the original as described below.

To check, download each file, save it under the name and path below, and
compare the SHA-256 with the value recorded here (`sha256sum docs/sources/*`).
A different hash means a different file or version. Re-check the cited pages or
cells before relying on it.

Access note: kpx.or.kr, epsis.kpx.or.kr, atb.nlr.gov, data.openei.org and
law.go.kr were blocked from the environment where this project was built. The
links below were supplied by the author, or are named in the documents
themselves. They were **not opened from this environment**. The files were
supplied by the author (upload or Google Drive). Hashes below are of the files
as supplied.

## Files

| Save as (`docs/sources/…`) | Issuer · title · version | Where to get it | What this project used | Size (bytes) · SHA-256 |
|---|---|---|---|---|
| `kpx_notice_2026-05_ess_central_contract_mainland.pdf` | 한국전력거래소 공고 제2026-05호, "2026년 ESS 중앙계약시장(육지) 경쟁입찰 공고", 2026-09-22 (PDF metadata created 2026-09-22 16:49 KST; 34 PDF pages) | kpx.or.kr notice board `bid=0042`, `list_no=78164`, attachment seq 1 (`https://www.kpx.or.kr/board.es?mid=a11201000000&bid=0042&act=view&list_no=78164`) | Whole file; page refs in `docs/market_rules.md` §2 (printed page = PDF page − 2) | 708,894 · `6cb6196ca345fc131f2e7642910d01a66e8d7125063b27166920c38818870880` |
| `KPX_rules_20260725_excerpt.pdf` | 전력시장운영규칙 (2026. 7.), full file `KPX_rules_20260725.pdf` (1,326 PDF pages, PDF metadata created 2026-07-24; full-file SHA-256 `624c4f9400d5f39b9ccd381e1d3e4278d434a42440bf4ed2a590dcfee4d4770c`) | kpx.or.kr board `bid=0030`, `list_no=77795` (rules attachment) | Excerpt = full-file PDF pages 1, 5, 264–276, 419–426, 448, 459, 460, 549, 550, 605–607, 644, 648, 652, 670, 675 (36 pages). Printed page = PDF page − 18. To rebuild: extract those pages from the full file | 686,421 · `5065334db8235e9ee128fc1ba69060c1bc0d0c966f62df5ae3e9d1de560e2cf9` |
| `KEC_2025-052_pp520-526_excerpt.pdf` | 한국전기설비규정, 기후에너지환경부 공고 제2025-052호 (2025-10-01, 제10차 개정); full file `KEC_official_attachment.pdf` (~23.2 MB) | Source URL of the original, as given by the author (not opened from this environment): `https://www.law.go.kr/flDownload.do?flSeq=158125635` | Full-file PDF pages 550–556 = printed 520–526 (512.1.2 on printed 523) | 372,307 · `e6cd58d4adf93e6cecc23d1309b6b0b9777993e7d891fbd44e5fa252ab15cf8d` |
| `KEC_2025-052_cover_and_addenda_excerpt.pdf` | Same KEC file | Same URL as above | Full-file PDF pages 1, 1205, 1206, 1207 = cover + printed 부칙 pp.1175–1177 | 357,897 · `9d72b67641e82309a2a84b715d403ec0f764cd9425b91f591f4013042e919b9e` |
| `ATB_2024_v3_Workbook.xlsx` | NREL Annual Technology Baseline 2024, workbook "2024 v3" (metadata modified 2025-02-14), sheet "Utility-Scale Battery Storage" | NREL ATB 2024 data downloads (OEDI / data.openei.org, ATB 2024 workbook) | Cells D10, D67, G9, G20, G26, H77, H108, H111, N111, H125, H128; rows 19–27, 70–84, 104–135, 155–164, 172–186 | 5,008,097 · `34316344383535a8bf9eb220bc54282cff75bcbc332a38e8c10a17c487dc8e46` |
| `ATB_2024_battery_webtext.pdf` | Text export of the ATB 2024 "Utility-Scale Battery Storage" web page, prepared by the author (not a publisher PDF; 3 pages) | `https://atb.nlr.gov/electricity/2024/utility-scale_battery_storage` (print the page to PDF) | Quoted text: "240 MWh usable", 2022$, FOM 2.5% incl. augmentation, RTE 85% | 9,956 · `41731ffb579af7300c4f1fddd3703807071d86bd427134d5bfc4a17deea543f9` |
| `atb2024_battery_cost_components.pdf` | ATB 2024 dashboard printout (Tableau), cost components | Same ATB 2024 page, dashboard view, printed 2026-09-27 | $1,906.95/kW, $476.74/kWh (2023 column) | 31,194 · `b445661b5970aabdfb44d541f7901caa7640295945baa3183c19cf21eaf36b05` |
| `atb2024_battery_capex_inclusions.pdf` | ATB dashboard printout, "Inclusions in CAPEX" | Same | Item list only | 35,964 · `904d0c0d3b47018081bfb44df8152e512ce77486eb17658e078d947550c5b8cd` |
| `atb2024_battery_om_inclusions.pdf` | ATB dashboard printout, "Inclusions in O&M" | Same | "Battery augmentation" under fixed costs | 30,457 · `a2113500ca83533235454e50559516c5abc19c321f55e2f2e4496ce993ec16eb` |
| `atb2024_battery_tech_summary.pdf` | ATB dashboard printout, parameter projections ("data updated: 02/26/2025 v4.109") | Same | Chart only; superseded by the workbook | 59,961 · `9b2cd90091030f8da6a99d8d42e965fd0e326fbaa914d655696ec40c56d36f93` |

Case A price data (`data/smp_2024_hourly.csv`) is part of the repository and is
not covered here. Its provenance and open questions are in `README.md` and
`docs/model_audit.md`.

## Rebuilding the page excerpts

With the full files saved locally, and page numbers 1-based as listed above:

```python
import pymupdf
def excerpt(src, pages, out):
    doc, new = pymupdf.open(src), pymupdf.open()
    for p in pages:
        new.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
    new.save(out)
```

A rebuilt excerpt has a different SHA-256 from the file listed above, because
PDF writers differ. Compare the page text instead.
