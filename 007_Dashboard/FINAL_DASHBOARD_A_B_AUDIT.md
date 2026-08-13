# CARE Final Dashboard Structure — Version C → Version B Audit

Date: 2026-08-11. This is the authoritative record of the restructuring that collapsed the project from three dashboards (A/B/C) down to the required two: **Version A** (unchanged baseline) and **Version B** (the former Version C, now finalized as the advanced/explainable dashboard). No screenshot file was attached to this conversation; the reference remained the design already implemented in the prior Version C build/compaction passes.

---

## 1. Version A status

**Completely unchanged.** Never opened for editing during this task.

```
Before this task: ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f
After this task:  ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f
```

`git diff -- 007_Dashboard/care_dashboard_versionA.py` produces no output. Launched live and tested (postcode search for G1 1XQ, map, prediction) — functioning identically to before.

---

## 2. New Version B status

`007_Dashboard/care_dashboard_versionB.py` now contains what was previously `care_dashboard_versionC.py` — the fixed 9-section, two-column, dark-theme, compact-layout advanced dashboard built and refined across the prior two sessions (initial build, then a compact-UI pass). Launched live and fully tested (see §11).

**Text changes made during the rename** (content only — no layout, data, or methodology changes):
- Docstring rewritten to describe the file as Version B in its own right (no longer framed as "independent of A and B" or as reusing code "from care_dashboard_versionB.py", since that file no longer exists in that form).
- `st.set_page_config(page_title=...)`: `"CARE Dashboard — Version C"` → `"CARE Dashboard — Version B"`.
- Header version badges: removed the "Version C" badge entirely; badges are now just **Version A | Version B**, with Version B shown active/highlighted.
- Header subtitle: `"Advanced Dashboard Prototype"` → **`"Advanced Explainable Flood-Risk Dashboard"`**.
- Footer attribution: `"CARE Version C"` → `"CARE Version B"`.
- Two in-code comments referencing "Version C" reworded to "Version B".
- `003_Code/08_Rainfall_Monthly_Seasonal.py` (the offline rainfall-preprocessing script this dashboard depends on): its docstring referenced `care_dashboard_versionC.py` three times — all updated to `care_dashboard_versionB.py`.

Confirmed via repo-wide search: no active `.py`/`.md`/`.ipynb` file contains "Version C" or "versionC" any more, **except** the two historical audit documents from the Version C build phase (§4). No `Claude`/`Anthropic`/`AI-generated`/`development-agent` references were found anywhere in the file (checked before and after).

---

## 3. Old Version B — removal

The previous `care_dashboard_versionB.py` (the tabbed Overview/"Why this prediction?" dashboard with a sidebar rainfall-trend widget, built up through `care_dashboard_step1.py` → `step3.py` → that version) has been **overwritten** — its content no longer exists as an active file under any name in `007_Dashboard/`.

**This is recoverable, not destroyed**, because nothing has been committed this session: the old content is still the version checked into the last git commit (`git show HEAD:007_Dashboard/care_dashboard_versionB.py` would return it in full), so `git checkout -- 007_Dashboard/care_dashboard_versionB.py` would restore it if ever needed — right up until a future commit supersedes that history. No `versionB_old.py` / `versionB_backup.py` file was created, per instruction. `care_dashboard_step1.py` and `care_dashboard_step3.py` (the pre-A/B build-history files CLAUDE.md already documents as intentionally preserved) were left untouched.

---

## 4. Version C → Version B rename mechanics

```bash
cp care_dashboard_versionC.py care_dashboard_versionB.py   # byte-identical copy (hash-verified)
rm care_dashboard_versionC.py
# then targeted text edits (see §2) applied to the new versionB.py
```

`007_Dashboard/` now contains exactly:
```
care_dashboard_step1.py     (build history, unchanged)
care_dashboard_step3.py     (build history, unchanged)
care_dashboard_versionA.py  (baseline, unchanged)
care_dashboard_versionB.py  (NEW — was versionC.py)
care_paths.py                (unchanged)
```
No `care_dashboard_versionC.py` remains.

**Historical audit files kept, not deleted or rewritten**: `VERSION_C_IMPLEMENTATION_AUDIT.md` and `VERSION_C_COMPACT_UI_AUDIT.md` (both produced during the Version C build phase) still reference "Version C" throughout. Per the instruction not to blindly rewrite historical records that legitimately document development history, these were left as-is — they are an accurate record of what was actually built and tested at the time, under the name it had at the time. This file (`FINAL_DASHBOARD_A_B_AUDIT.md`) is the authoritative current-state document; the two `VERSION_C_*` files should be read as historical/superseded from this point forward.

---

## 5. Overlap fixes applied before finalizing

Per the instruction to fix all visual issues *before* the rename, a dedicated QA pass (live browser testing, not just code review) was run against the pre-rename Version C file, deliberately targeting worst-case content lengths (a High-risk location via postcode `G5 0RX`, which produces the longest Recommendations list — 4 items — and longest interpretation-card text). This found **four real instances of one root-cause bug**, all fixed:

| Location | Symptom | Fix |
|---|---|---|
| Section 9 (Recommendations) | Last bullet's descender nearly touched the "Source: SEPA..." caption below it | Added `margin-bottom:6px` to the `<ul>` |
| Footer | The two-line disclaimer text ran directly into the "Data:" line beneath it with no gap | Converted from two separate `st.caption()` calls into one `st.markdown()` block with explicit `margin-top:6px` between the two `<div>`s |
| Section 3 (Location Details) | The details grid's last row touched the "Nearest 100m grid point..." disclaimer directly beneath it | Folded the disclaimer into the same `st.markdown()` call as the grid, with explicit `margin-top:6px` |
| Section 5 (Monthly Rainfall) | The "Relative historical rainfall exposure..." caption touched the table's header row directly beneath it | Folded the caption into the same `st.markdown()` call as the table, with explicit `margin-bottom:6px` before the `<table>` |

**Root cause identified via live DOM/CSS inspection** (not guessed): inside a `st.container(border=True)` card, when one custom HTML block (`st.markdown(unsafe_allow_html=True)`) is immediately followed by a separate Streamlit element (another `st.markdown()` or `st.caption()`) with no `st.columns()` between them, the ambient flex `gap` between the two elements resolves to effectively zero in this app's specific combination of custom CSS and Streamlit's own internal styling for bordered containers — the same underlying class of issue as the SHAP/monthly-chart squashing bug found and fixed in the previous compact-UI session (`align-items: start` on Streamlit's own auto-height bordered-container block). Rather than continue fighting that ambient behaviour rule-by-rule, every trailing caption identified as being at risk was folded into the same `st.markdown()` call as the content before it, with an explicit pixel margin — a deterministic fix that doesn't depend on Streamlit's internal flex state.

**A separate, distinct overlap** was found and fixed in the header itself after the rename: the new subtitle line ("Advanced Explainable Flood-Risk Dashboard") rendered directly underneath the "Reset All" button, completely hidden behind it (confirmed via `getBoundingClientRect()` — both elements occupied the same ~64-80px vertical band). Root cause: the header's `gap: 0` CSS (added during the earlier compact-UI pass) combined with Streamlit's own button-wrapper spacing to produce literal overlap rather than just a tight gap. Fixed by changing the header's gap from `0` to `4px` and adding an explicit `margin-top: 10px` directly on the button's own wrapper (`[data-testid="stButton"]`), which is not dependent on ambient flex-gap resolution.

**Verification**: every fix was re-screenshotted and, where the fix wasn't visually unambiguous at normal zoom, re-inspected with pixel-region zooms and/or `getComputedStyle`/`getBoundingClientRect()` checks to confirm actual clearance, not just "looks fine." A final full top-to-bottom pass across both the default state and the high-risk/longest-content state found no further instances of the pattern.

---

## 6. Compact-layout state (carried over, not re-done)

The compact layout achieved in the prior session is unchanged by this task: two-column fixed 9-section layout (`st.columns([0.95, 1.45], gap="small")`), ~75-80px header, bordered cards with 10-12px internal padding, 2×2 metric grids (Historical Rainfall), 3-metric top row (Monthly Rainfall), HTML tables instead of `st.dataframe` (for font/row-height control), compact SHAP/monthly/historical chart heights. This task only added the four gap fixes in §5 on top of that existing layout — no section was resized, reordered, or redesigned.

---

## 7. Features confirmed present in final Version B

All nine numbered sections, unchanged from the approved Version C design:

1. Enter Postcode — postcodes.io lookup, valid/invalid handling, admin_district capture
2. Prediction Summary — risk level, model confidence, seasonal rainfall exposure, 3-segment risk scale, hedged-language interpretation card
3. Location Details — postcode/lat/lon/elevation/distance-to-Clyde/grid point/local authority/data source
4. Risk Map — folium map, risk-level/distance/district filters + "More filters" expander, historical event markers, click-to-select
5. Monthly Rainfall Exposure — highest/lowest/current-season metrics, bar chart, full 12-month table
6. Historical Rainfall Summary — 39-year line chart, 2×2 stat grid (avg/wettest/driest/max-month)
7. Seasonal Risk Overview — 4 season cards with relative rainfall-exposure categories
8. Why This Result? — live SHAP explanation, diverging bar chart, top-2 definitions + expander for the rest
9. Recommendations — risk-tiered `PRECAUTIONS` content, sourced to SEPA/Ready Scotland

Plus the methodology disclaimer footer, compact space-optimised design, and the dark theme as the dashboard's fixed visual identity.

---

## 8. Model integrity

**Nothing about the model changed.** `care_dashboard_versionB.py` loads the same `rf_model_40yr.joblib` via the same `care_paths.py` (unmodified — no new constants were added to it during this task), predicts with the same `FEATURE_COLS`, and reads the same `feature_matrix_40yr.csv`. No retraining, no new labels, no changes to `04_ML_Model.ipynb`, `03_Feature_Engineering.ipynb`, the spatial-block validation, or any reported research result. This task's edits were confined to `care_dashboard_versionB.py`'s own text/layout and `003_Code/08_Rainfall_Monthly_Seasonal.py`'s docstring.

---

## 9. SHAP integrity

Unchanged: `shap.TreeExplainer(model, data=X_train, model_output="probability")`, background = the same 80% training split (`random_state=42`) as `04_ML_Model.ipynb`, computed live per selected point via `explainer.shap_values(row)`. Feature contribution chart, positive/negative direction colour-coding, plain-English feature explanations, and the non-causal caveat ("These bars show what influenced this model classification. They do not prove what caused flooding.") are all present and untouched by this task.

---

## 10. Monthly rainfall methodology

Unchanged and correctly labelled throughout as **"Monthly Rainfall Exposure"** / **"Historical Rainfall Climatology"** — never "monthly flood prediction/probability." Derived offline (`003_Code/08_Rainfall_Monthly_Seasonal.py`, only its Version-B file-path references were updated this task) from the existing `rainfall_daily_1987_2025.parquet`, itself already computed by `03_Feature_Engineering.ipynb`. No new raw data, no changes to the aggregation logic (mean/wet-days/max-daily by grid_id × month, mirroring `03_Feature_Engineering.ipynb`'s existing annual/winter methodology).

---

## 11. Tests performed

| Test | Version A | New Version B |
|---|---|---|
| Launches | ✅ (already running, screenshot-verified) | ✅ |
| Postcode search | ✅ (G1 1XQ → correct result panel) | ✅ (G5 0RX → High risk, `admin_district` "Glasgow City" captured) |
| Prediction / risk classification | ✅ | ✅ |
| Model confidence | — | ✅ (99%) |
| Location details | — | ✅ |
| Map | ✅ (visible, risk-coloured points) | ✅ (visible in section 4) |
| Filters | — | Unchanged from the prior session's verified compact-UI filter test; not re-run this pass since no filter code was touched |
| Monthly rainfall | — | ✅ (chart + full 12-row table render correctly) |
| Historical rainfall | — | ✅ (2×2 stat grid: 1079mm avg / 2011 wettest / 2001 driest / Feb 2020 max) |
| Seasonal overview | — | Unchanged from prior session; not re-exercised this pass (no code touched) |
| SHAP | — | ✅ (9-feature diverging bar chart, no clipping, at the High-risk test location) |
| Recommendations | — | ✅ (4-item High-risk list, clean spacing confirmed after the fix) |
| Reset All | — | ✅ (reverts to default University point, clears input) |
| Header (no "Version C" anywhere, Version B badge active) | — | ✅ (confirmed via screenshot + DOM text search) |

---

## 12. Screenshot QA result

Full top-to-bottom review at desktop resolution (1470-1568px viewport, matching the primary target per the compact-UI instructions), in both the default state and the High-risk/longest-content state:

- No overlapping text remaining (all four instances found were fixed and re-verified — see §5)
- No clipping
- No excessive blank space (unchanged from the prior compact-UI pass's already-verified result)
- No broken cards
- No chart collisions — the SHAP/monthly-chart squashing bug from the prior session stayed fixed (not reintroduced by this task's edits)
- No table clipping (12-row monthly table renders in full)
- Header renders at correct compact height with badges, subtitle, and the Reset All button all clearly separated

---

## 13. Files changed this task

| File | Change |
|---|---|
| `007_Dashboard/care_dashboard_versionC.py` | 4 overlap fixes applied, then Version C → Version B text updates applied, then copied to `versionB.py` and deleted |
| `007_Dashboard/care_dashboard_versionB.py` | **Replaced** — now contains the former Version C content (with the fixes/renames above) instead of the original tabbed SHAP dashboard |
| `007_Dashboard/care_dashboard_versionA.py` | **Not modified** (hash-verified) |
| `007_Dashboard/care_paths.py` | **Not modified** |
| `003_Code/08_Rainfall_Monthly_Seasonal.py` | 4 docstring references updated from `versionC.py` to `versionB.py`; no logic changed |
| `007_Dashboard/FINAL_DASHBOARD_A_B_AUDIT.md` | **New** — this file |

Not modified: `007_Dashboard/VERSION_C_IMPLEMENTATION_AUDIT.md`, `007_Dashboard/VERSION_C_COMPACT_UI_AUDIT.md` (kept as historical record — see §4), the trained model, any feature/rainfall data file, `04_ML_Model.ipynb`, `03_Feature_Engineering.ipynb`, `02_EDA.ipynb`, `01_Data_Collection.ipynb`, the dissertation, `README.md`, `CLAUDE.md`.

---

## 14. Dissertation references requiring later update — REPORT ONLY, NOT EDITED

**This is the most significant finding of this task and needs a decision from you before anyone touches the dissertation.**

`006_Dissertation/CARE_Dissertation_Chapters_1to6_Draft.md` mentions **"Version B" 43 times**, and it is not describing the dashboard this task just built. It describes the *original* tabbed dashboard (Overview / "Why this prediction?" tabs, a "Why am I seeing this result?" button that jumps between tabs, a sidebar rainfall-trend widget, a citywide risk-mix donut chart) — the one that has just been overwritten. Specifically:

- **Chapter 3** (system description): §3.11 "Dashboard Version B", Table 3.2 (Version A vs Version B feature comparison), and Figures 3.10–3.17, several of which are literal screenshots of the old design — `006_Dissertation/figures/screenshots/versionB_landing.jpg`, `versionB_shap_panel.jpg`, `versionB_shap_panel_full.png`, `versionB_why_button.jpg`, plus `figures/figure_3_versionA_vs_B.png` (a side-by-side comparison screenshot).
- **Chapter 4**: one reference tying a SHAP waterfall example to "the same style of explanation surfaced live in Version B's 'Why this prediction?' panel."
- **Chapter 5** (usability evaluation) — the one that matters most: **this is real, already-collected participant data.** Six participants (P01–P06) were split 3-and-3 between Version A and "Version B," and Version B's *specific* SHAP-tab design is what they evaluated and what the reported findings (increased trust, "black box" language, technical-terminology friction, Figure 5.5's "SHAP explanation feedback, Version B only") are actually about. §5.9 ("Version A versus Version B"), Table 5.1, and the RQ2/RQ3 conclusions in Chapter 6 all rest on this.

**The core problem**: "Version B" in the dissertation is not just a design description that needs refreshing — it's the label attached to genuine, already-collected human-subjects research data. The dashboard now called "Version B" in the live repository is a different design that no participant has ever seen or evaluated. If the dissertation is edited to describe the *new* Version B's design while keeping the *old* Version B's participant data attached to the same name, the two would silently contradict each other (the figures/prose would show one interface, the participant quotes would describe a different one they actually used).

**Recommendation (not implemented, yours to decide)**: before any dissertation edit, decide how to resolve the naming collision — options include (a) keeping the dissertation's "Version B" as-is, describing it explicitly as "the version used in the usability study" and introducing the new dashboard under a different label (e.g. "the current CARE dashboard" or a dated/versioned name) for any forward-looking sections, or (b) renaming the studied version throughout the dissertation (e.g. to "Version B (study prototype)") and introducing the new design as a distinct, not-yet-evaluated successor. Both are legitimate; neither should be done by silent find-and-replace given how much empirical content is tied to the exact wording.

`README.md` (repo root) was checked and found to have the same issue at smaller scale (it describes the old Version B's SHAP-tab design and references the same n=6 usability study) — also **not edited**, for the same reason.

---

## 15. Git safety

```
$ shasum -a 256 007_Dashboard/care_dashboard_versionA.py
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f   (matches pre-task baseline)

$ git diff -- 007_Dashboard/care_dashboard_versionA.py
(no output)

$ git status --short | grep -E "007_Dashboard|08_Rainfall"
 M 007_Dashboard/care_dashboard_step1.py       (pre-existing staged state, predates this task)
 M 007_Dashboard/care_dashboard_step3.py       (pre-existing staged state, predates this task)
 M 007_Dashboard/care_dashboard_versionA.py    (pre-existing staged state, predates this task — working tree unchanged, see diff above)
MM 007_Dashboard/care_dashboard_versionB.py    (this task's replacement — see §2-4)
 A 007_Dashboard/care_paths.py                 (pre-existing staged state, predates this task)
?? 003_Code/08_Rainfall_Monthly_Seasonal.py
?? 007_Dashboard/VERSION_C_COMPACT_UI_AUDIT.md
?? 007_Dashboard/VERSION_C_IMPLEMENTATION_AUDIT.md
?? 007_Dashboard/FINAL_DASHBOARD_A_B_AUDIT.md

$ git diff --stat
 003_Code/02_EDA.ipynb                     | 27 ++++++++---------  (pre-existing, not touched this task)
 007_Dashboard/care_dashboard_versionB.py  | 1783 +++++++++--------  (this task's replacement)
```

The `M`/`A` markers on `step1.py`, `step3.py`, `versionA.py`, and `care_paths.py` are **pre-existing staged state from before this task began** (part of the earlier raw/processed/outputs/archive reorg work in this repo's history) — not something this task did. `versionA.py`'s working-tree content is confirmed identical to the pre-task baseline via the hash and empty diff above. No commit or push was performed. Nothing beyond `care_dashboard_versionB.py` (intentionally) and the new documentation files was written to.
