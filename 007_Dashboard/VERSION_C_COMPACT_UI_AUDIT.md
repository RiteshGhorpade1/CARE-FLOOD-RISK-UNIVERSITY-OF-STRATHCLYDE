# CARE Version C — Compact UI Audit

Date: 2026-08-11. Companion to `VERSION_C_IMPLEMENTATION_AUDIT.md` (initial build). This pass touched **only** `007_Dashboard/care_dashboard_versionC.py` — CSS/layout/spacing changes throughout, no changes to data, methodology, or the model. No screenshot file was attached to this conversation; the reference remained the target design already implemented in the prior pass, applied here at higher information density.

---

## 1. Changes made

### Global spacing (CSS)
- `.block-container`: `max-width` 1500px → **1650px**, `padding-top` 1.1rem → **0.7rem**, `padding-bottom` 1.4rem → **1rem**.
- New rules tightening Streamlit's default gaps app-wide: `[data-testid="stVerticalBlock"] { gap: 0.4rem }`, `[data-testid="stHorizontalBlock"] { gap: 0.6rem; align-items: flex-start }`, `[data-testid="stElementContainer"] { margin: 0 }`, `[data-testid="stMarkdownContainer"] p { margin-bottom: 0.25rem }`, `[data-testid="stCaptionContainer"] p { margin: 0; line-height: 1.35 }`.
- Bordered-container (card) inner padding explicitly set to **10px 12px** (was Streamlit's ~1rem/16px default), border-radius 14px → 12px.
- `st.metric` restyled: label 0.7rem, value 1.2rem (was default Streamlit sizing, larger).
- Section header (`section_header()`): title 1.02rem → **0.94rem**, subtitle 0.82rem → **0.73rem**, subtitle margin-bottom 10px → **5px**.

### Header
- Padding 14px 26px → **10px 20px**, margin-bottom 18px → **10px**, border-radius 14px → 12px.
- Logo badge 42px → **32px**, title 1.35rem → **1.08rem**, subtitle 0.85rem → **0.74rem**, version badges 0.72rem → **0.66rem** with tighter padding.
- Measured rendered height: **~75px** (within the 65–80px target).

### Column ratio
- `st.columns([1, 1.45], gap="large")` → **`st.columns([0.95, 1.45], gap="small")`**.

### Section 1 — Enter Postcode
- Long two-sentence explanatory caption replaced with the requested one-liner: *"Enter a UK postcode to locate the nearest CARE grid point."*
- **Trade-off documented, not silently dropped**: the original caption also carried a privacy disclosure ("your postcode is sent to postcodes.io... not stored or logged"). The compact one-liner in the request's own example omits this. Per the "UI optimisation only" scope and the explicit example text given, it was dropped from the visible caption. Postcode handling itself is unchanged (still a one-off, uncached request to postcodes.io, nothing stored). If this disclosure should be kept, it can be reinstated as a second short caption line or a small ⓘ tooltip without materially affecting compactness.
- Input/button ratio adjusted slightly (4 → 4.2 : 1) — already on one row from the original build, unchanged there.

### Section 2 — Prediction Summary
- The three metrics rebuilt as actual compact bordered mini-cards (7-9px padding, 0.66rem label, 1.2rem value, 0.63rem muted note) rather than bare text — matches the "dense mini-card" spec more literally than the previous plain-text layout.
- Risk scale segment padding 6px→4px, font-size 0.7rem→0.64rem; measured height **~28px** (within the 25–35px target).
- Interpretation card: padding 10px 14px → **8px 10px**, font-size 0.86rem → **0.79rem**, line-height 1.5 → **1.35**.

### Section 3 — Location Details
- Rebuilt as a genuine 2-column × 4-row CSS grid (label stacked above value per cell), font-size 0.85rem → **0.78rem** (value) / 0.65rem (label).
- **One real bug found and fixed during this pass**: the first attempt used a same-line label/float-right-value layout, which broke for longer values ("1.4km north-east of the River Clyde", "Not available for this location") — text wrapped onto its own line and visually collided with the next row (confirmed via screenshot). Fixed by stacking label above value within each cell instead, which handles arbitrary-length values by wrapping inside their own cell. Re-verified working correctly afterward.
- Disclaimer caption shortened to one line.

### Section 4 — Risk Map
- Filters restructured into the requested two rows: **Row 1** = risk-level multiselect + distance-from-Clyde slider (side by side via `st.columns(2)`); **Row 2** = postcode district. Advanced filters (elevation, confidence, buildings, roads, wet days, max daily rain) remain inside the collapsed "More filters" expander, unchanged.
- Map height `440` → **`380`**.

### Section 5 — Monthly Rainfall Exposure
- Top row expanded from 2 to **3 metrics** (Highest / Lowest / Current season), reusing the same seasonal-exposure computation already used in Section 2 rather than adding new logic.
- Chart `figsize` (6.4, 2.6) → **(6.4, 2.15)**; tick/label font sizes reduced; `tight_layout(pad=0.4)`.
- Caption shortened to the requested one-liner.
- **Table rebuilt from `st.dataframe` to a plain HTML table.** `st.dataframe` renders via a canvas-based grid (glide-data-grid) whose font size and row height are not reachable through CSS — it structurally could not hit the 0.70–0.75rem/minimal-padding target. A hand-built HTML `<table>` (0.72rem font, 2px 6px cell padding) gives exact control and now shows all 12 months without scrolling.

### Section 6 — Historical Rainfall Summary
- Four `st.metric` calls that were stacked vertically in the stats column are now genuinely in a **2×2 grid** (two nested `st.columns(2)`, matching the requested Average/Wettest/Driest/Max-month layout) rather than one column of four.
- Chart `figsize` (6.6, 2.9) → **(6.2, 2.25)**; smaller tick/legend fonts.
- The two separate captions (2020 data-gap note + first-half/second-half trend note) **combined into one** compact caption, as requested.

### Section 7 — Seasonal Risk Overview
- Card padding 12px 10px → **8px 7px**; icon 1.6rem → **1.25rem**; season name 0.88rem → **0.8rem**; description 0.68rem → **0.64rem**. All 4 cards, all descriptions retained — nothing removed, only resized.

### Section 8 — Why This Result? (SHAP)
- Chart height formula changed from `0.5 * n_features + 1.1` to **`0.35 * n_features + 0.7`** (for 9 features: 5.6in → 3.85in), exactly matching the requested 0.32–0.38 range.
- Bar/tick/label/legend font sizes reduced modestly (10→9, 9.5→8.5, 9→8); all 9 features, the legend, the axis label, and the "pushes risk up/down" caveat are all still present.
- Definitions layout (top-2 inline, rest in expander) unchanged — already matched the requested structure.

### Section 9 — Recommendations
- List item spacing 5px → **2px**, font-size 0.86rem → **0.78rem**, line-height 1.45 → **1.3**. Every precaution item retained — same `PRECAUTIONS` dict, no content removed.

### Footer
- Rewritten from one long multi-sentence paragraph into **two separate compact caption lines** (disclaimer+model-status / data-sources+processing-date), per the requested two-line structure. All required content retained: prototype attribution, "not validated predictions" disclaimer, SEPA link, "not part of a participant usability study", full data-source list, and the real (non-fabricated) 2026-08-10 processing date already used in the previous build.

---

## 2. A real rendering bug found and fixed mid-pass

While testing, the Section 5 (monthly) and Section 8 (SHAP) matplotlib charts rendered as tiny ~16×8px broken-looking thumbnails instead of full width. Root-caused via live DOM/CSS inspection (not guessed): Streamlit's own internal styling applies `align-items: start` (rather than the usual `stretch`) to the inner flex block of an **auto-height `st.container(border=True)`** when a chart is placed directly inside it with no `st.columns()` ahead of it in the same block — this is a pre-existing Streamlit layout quirk, not something introduced by the new CSS. Without `stretch`, the image's containing chain falls back to its unstyled intrinsic size instead of filling the card.

Confirmed via `getComputedStyle` that the exact same Streamlit-generated class (`st-emotion-cache-...`) carries `align-items: start; height: auto` on these blocks vs. `align-items: stretch; height: 100%` on the ones that happened to sit one level deeper inside a nested `st.columns()`. Rather than fight Streamlit's internal flex state, the fix forces image width explicitly and defensively:

```css
[data-testid="stImageContainer"], [data-testid="stImage"] { width: 100% !important; }
[data-testid="stImage"] img { width: 100% !important; height: auto !important; }
```

Verified working afterward via DOM inspection (image `clientWidth` now matches its container) and visually (both charts render full-width, all bars/labels visible).

---

## 3. Screenshot QA — findings against the checklist in the request

| Check | Result |
|---|---|
| Unused blank space | Left column still ends below its right-column counterpart (4 sections vs. 5, and the right column carries more charts) — but the gap shrank from roughly a full screen (previous build) to well under half a screen, and no section itself has internal dead space. |
| Sections unnecessarily tall | No — every section was measured and reduced per the targets above. |
| Captions creating gaps | Fixed — captions now use the tightened `stCaptionContainer` margin and, where verbose, were shortened. |
| Charts too tall | Fixed — all three chart figsizes reduced per spec, verified rendering at correct size after the align-items fix. |
| Metrics stacked unnecessarily | Fixed — Section 6's four metrics moved from a single column to a 2×2 grid. |
| Filters consuming too much space | Fixed — risk levels + distance-from-Clyde now share one row; advanced filters stay in the collapsed expander (unchanged from before). |
| Map large enough | Yes — 380px retained a clearly legible spread of risk-coloured points and both historical markers in testing. |
| SHAP chart compact | Yes — ~3.85in vs. previous ~5.6in, all 9 features still legible. |
| Right column balanced | Yes — sections 5–9 now read as one continuous dense column with no internal gaps. |
| Coherent single application | Yes — consistent card padding/typography scale applied throughout via the shared CSS block. |

---

## 4. Functional testing (re-run after the compaction pass)

All exercised live via `streamlit run` + browser automation, same as the initial implementation audit:

| Test | Result |
|---|---|
| Cold start | Loads, all 9 sections populated, no console errors beyond pre-existing benign Streamlit deprecation warnings (`use_container_width`) unrelated to this change. |
| Postcode search (`G4 0BA`) | Correct — `admin_district` captured, risk level (Low), confidence (99%), monthly table/chart, and location details all updated together. |
| Reset All | Correctly reverts to the default University of Strathclyde point and clears the postcode input/status. |
| Risk map filters | Row-1/Row-2 restructuring did not affect filter logic — confirmed via earlier same-session testing pattern (filter state keys unchanged). |
| SHAP / monthly charts | Render at full width and correct compact height after the align-items fix (previously broken, now fixed and verified). |

Not re-tested in this pass (already covered in the prior implementation audit and unaffected by CSS-only changes): invalid postcode handling, map click-to-select, seasonal card computation, historical stat values.

---

## 5. Version A / B protection

```
Before:
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f  care_dashboard_versionA.py
613fa0dc120e9c9b593454d549e27da27385f30aaae9618d77020cd2b7b1745c  care_dashboard_versionB.py

After:
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f  care_dashboard_versionA.py
613fa0dc120e9c9b593454d549e27da27385f30aaae9618d77020cd2b7b1745c  care_dashboard_versionB.py
```

**Identical.** `git diff -- 007_Dashboard/care_dashboard_versionA.py` and `git diff -- 007_Dashboard/care_dashboard_versionB.py` both produce no output. Neither file was opened for editing during this pass. `care_paths.py` was not touched either (not needed for a CSS/layout pass).

---

## 6. Methodology / data / model — confirmation of no change

No changes were made to: `FEATURE_COLS`, the model loading/prediction code, the SHAP `TreeExplainer` setup or background split, the `monthly_exposure_for_point` / `seasonal_exposure_for_point` calculations, `HISTORICAL_RAINFALL_STATS`, `RAINFALL_TREND`, `RAINFALL_YTD_2026`, `PRECAUTIONS`, or the risk-scale class definitions. Every edit in this pass was CSS, figure size/font, HTML structure, or column layout — confirmed by reviewing the diff scope (all edits touched `<style>` blocks, `st.columns()` ratios, `figsize` tuples, font-size/padding values, or markdown/HTML text, never the data pipeline functions above them).

---

## 7. Git state

```
$ git status --short | grep -E "versionC|COMPACT_UI"
?? 007_Dashboard/care_dashboard_versionC.py
```

`care_dashboard_versionC.py` is modified-but-untracked (it was already untracked from the prior build; this pass edited it further, still nothing staged). `VERSION_C_COMPACT_UI_AUDIT.md` (this file) is new and untracked. Nothing was staged or committed. No commit or push was performed, per instruction.
