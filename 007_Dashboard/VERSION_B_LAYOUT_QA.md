# CARE Version B — Layout Repair QA

Date: 2026-08-11. Two overlap/layout bug-fix passes on `007_Dashboard/care_dashboard_versionB.py`, documented in the order they happened. No screenshot file was attached to this conversation for either pass — reported bugs were located and confirmed by reproducing the described scenarios live (a High-risk location via postcode search, which produces the longest text in every affected component) rather than by viewing the actual images.

**Pass 1** (§1–9 below) fixed two specific reported bugs (Prediction Summary, SHAP definitions/expander) via a targeted `align-items` scoping fix.

**Pass 2** (§10 onward) responded to a follow-up report that the overlap was not isolated to those two spots but a global pattern across section headings/subtitles throughout the dashboard, and applied a broader, systematic fix: a single consistent section-header spacing standard applied to all 9 sections, plus restoring a real (not zeroed) per-element margin as a spacing floor that doesn't depend on flex-gap resolving correctly in every context.

---

## 1. Confirmed overlap bugs

| # | Section | Symptom described |
|---|---|---|
| 1 | 2. Prediction Summary | The `LOW \| MODERATE \| HIGH` risk scale rendering behind/overlapping the bottom edge of the three metric cards above it |
| 2 | 8. Why This Result? | The "What do the other features mean?" expander visually touching/overlapping the two feature-definition text blocks above it |

Both were reproduced live in this session (not merely inferred) using the `G5 0RX` postcode (a High-risk grid point that also produces the longest interpretation-card text, the longest 4-item recommendation list, and the "Moderate elevation / Moderate distance from the River Clyde" definition pairing that matches the bug report's own example text).

---

## 2. Root cause — identified via live DOM/CSS inspection, one shared mechanism for both bugs

Investigated via `getComputedStyle()`/`getBoundingClientRect()` on the actual rendered page (not guessed). Both bugs traced to the **same single rule**:

```css
[data-testid="stHorizontalBlock"] { gap: 0.6rem; align-items: flex-start; }
```

This CSS was applied in the previous compact-UI pass to **every** `st.columns()` row in the app — but it was only ever intended for the one top-level left/right page split (so a short left column wouldn't be force-stretched to match a much taller right column). Applied globally, it also switched off Streamlit's own default `align-items: stretch` for every *other*, smaller `st.columns()` row in the dashboard — the 3-card metric row in Prediction Summary, and the 2-column feature-definition row in the SHAP section among them.

With `align-items: flex-start`, sibling columns in a row no longer stretch to a shared height — each column sizes to its own content instead. Column content length varies with the selected location (season name, exposure-category word, feature-definition sentence length, etc.), so:
- **Bug 1**: when the "SEASONAL RAINFALL" card's note text (`"{season} — historical, not model risk"`) wrapped to two lines while the other two cards' notes stayed on one line, that one card's background box extended further down than its siblings — a ragged, inconsistent bottom edge that read as the risk scale crowding into the taller card.
- **Bug 2**: the same mechanism on `def_col1, def_col2 = st.columns(2)` — whichever of the two selected features had the longer plain-English definition sentence produced a taller column than its sibling, leaving a ragged edge directly above the expander.

This is exactly the general mechanism flagged in the bug report's own root-cause checklist (`align-items`, `flex-gap manipulation`, `display:flex`, `nested st.columns`) — confirmed, not merely plausible, via the live inspection described above.

---

## 3. CSS/layout fix

**Not a blanket `margin:0`/`padding:0`/`gap:0` rule, and no negative margins, fixed heights, or absolute positioning were introduced.** The fix scopes the flex-start behaviour to only the one row that needs it:

1. Wrapped the top-level column split in a keyed container so it — and only it — carries a targeted CSS class:
   ```python
   with st.container(key="page_columns"):
       col_left, col_right = st.columns([0.95, 1.45], gap="small")
   ```
2. Removed `align-items: flex-start` from the blanket `[data-testid="stHorizontalBlock"]` rule, so every other `st.columns()` row in the app (metric cards, feature-definition columns, the historical-rainfall 2×2 stat grid, the seasonal 4-card row, the map's filter-row columns) reverts to Streamlit's own **default `align-items: stretch`** — sibling columns in those rows now always end at the same height, regardless of how much text any one of them happens to contain.
3. Added the scoped override back in, targeted only at the page-level split:
   ```css
   .st-key-page_columns [data-testid="stHorizontalBlock"] { align-items: flex-start; }
   ```
4. As a second, independent layer of defence specifically for the metric cards (matching the report's own suggested pattern — `min-height` rather than a fixed `height`, `box-sizing: border-box`, natural wrapping preserved): gave the mini-card HTML a `min-height: 72px` and a dedicated `.care-metric-card` class, so even if a future edit changes the note text again, the card has guaranteed minimum room for its three lines without being clipped, while still growing (not clipping) if content ever needs more than that.

No other spacing rule from the compact-UI pass was touched — `[data-testid="stVerticalBlock"] { gap: 0.4rem; }`, the bordered-card padding rule, and the four earlier caption/table margin fixes (Recommendations, footer, Location Details, Monthly table) are all unrelated to this mechanism and were left as they were, since they were not implicated by the live inspection and reverting them would have undone real, verified fixes from the prior session for no reason.

---

## 4. Screenshot QA

Tested at both required desktop widths, in both the default state (University of Strathclyde, Medium risk) and the worst-case content state (postcode `G5 0RX`, High risk — longest interpretation text, longest 4-item recommendation list, two-word "Moderate distance from the River Clyde" definition):

| Check | 1440×900 | 1920×1080 |
|---|---|---|
| Prediction Summary — cards vs. risk scale | ✅ equal-height cards, clean gap to scale, confirmed via pixel zoom | ✅ |
| SHAP — feature definitions vs. expander | ✅ clean gap, confirmed with the exact "Moderate elevation / Moderate distance from the River Clyde" pairing from the bug report | ✅ |
| Section boundaries 1→2, 2→3, 3→4 | ✅ no crossing | ✅ |
| Section boundaries 4→5, 5→6 (table→chart) | ✅ no crossing | ✅ |
| Section boundaries 6→7, 7→8, 8→9 | ✅ no crossing | ✅ |
| Footer | ✅ no overlap (two-line footer from the prior session's fix still intact) | ✅ |
| Map click-to-select | ✅ new grid point (#2441, "Right at the River Clyde") selected correctly, layout stayed clean | not re-tested at this width (same code path as 1440px, already verified functioning) |
| Reset All | ✅ reverts cleanly to default state | not re-tested at this width (same code path, already verified functioning at 1440px in the prior session and again here) |

No instance of the reported overlap pattern remained anywhere on the page in either state at either width.

---

## 5. Version A hash

```
Before this task: ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f
After this task:  ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f
```
Identical. `git diff -- 007_Dashboard/care_dashboard_versionA.py` produces no output. The file was never opened for editing during this task.

---

## 6. Version B functional test results

All exercised live via `streamlit run` + browser automation:

| Test | Result |
|---|---|
| Launches | ✅ no errors (one transient error was hit and fixed during development — see §7 — not present in the final version) |
| Postcode search (`G5 0RX`) | ✅ High risk, 99% confidence, `admin_district` "Glasgow City" captured |
| Prediction / risk summary / risk scale | ✅ |
| Location details | ✅ |
| Map (click-to-select) | ✅ selecting a different marker updates grid point, elevation, distance-to-Clyde, and re-renders the SHAP panel correctly |
| Monthly rainfall | ✅ chart + full 12-row table |
| Historical rainfall | ✅ 2×2 stat grid, line chart |
| Seasonal cards | ✅ all 4 cards equal height |
| SHAP | ✅ 9-feature chart, no clipping |
| Feature definitions | ✅ |
| Expander | ✅ opens/closes correctly, no longer touching the definitions above it |
| Recommendations | ✅ 4-item High-risk list |
| Reset | ✅ |

---

## 7. A development-time error worth recording

While implementing the `page_columns` container fix, an initial attempt used `st.columns([...], key="page_columns")` directly — Streamlit 1.50.0 (the version actually installed and pinned in `requirements.txt`) does **not** accept a `key` argument on `st.columns()`, and this threw `TypeError: columns() got an unexpected keyword argument 'key'` on load (caught immediately via a live screenshot before proceeding further). Fixed by wrapping the `st.columns()` call in `st.container(key="page_columns")` instead, which is supported and produces the same scoped CSS class on the wrapping element. This was caught and corrected within this session; it never reached a state the user would have seen.

---

## 8. Confirmation: model, data, and methodology unchanged

No changes were made to `FEATURE_COLS`, the model loading/prediction code, the `shap.TreeExplainer` setup, `monthly_exposure_for_point()` / `seasonal_exposure_for_point()`, `HISTORICAL_RAINFALL_STATS`, `RAINFALL_TREND`, `PRECAUTIONS`, or the risk-scale class definitions. Every edit in this pass was CSS (the `align-items` scoping change) or presentation-layer HTML (the `min-height`/class addition on the metric-card helper and the `st.container(key=...)` wrapper around the column declaration) — confirmed by reviewing the diff scope, which touches only the `<style>` block and the two specific code locations described in §3.

---

## 9. Git safety

```
$ shasum -a 256 007_Dashboard/care_dashboard_versionA.py
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f   (matches baseline)

$ git diff -- 007_Dashboard/care_dashboard_versionA.py
(no output)

$ git status --short | grep 007_Dashboard
 M 007_Dashboard/care_dashboard_step1.py       (pre-existing staged state, predates this task)
 M 007_Dashboard/care_dashboard_step3.py       (pre-existing staged state, predates this task)
 M 007_Dashboard/care_dashboard_versionA.py    (pre-existing staged state, predates this task — working tree unchanged, see diff above)
MM 007_Dashboard/care_dashboard_versionB.py    (this task's fixes)
 A 007_Dashboard/care_paths.py                 (pre-existing staged state, predates this task)
?? 007_Dashboard/FINAL_DASHBOARD_A_B_AUDIT.md
?? 007_Dashboard/VERSION_C_COMPACT_UI_AUDIT.md
?? 007_Dashboard/VERSION_C_IMPLEMENTATION_AUDIT.md
?? 007_Dashboard/VERSION_B_LAYOUT_QA.md

$ git diff --stat -- 007_Dashboard/
 007_Dashboard/care_dashboard_versionB.py | 1799 +++++++++++++++----------------
 1 file changed, 826 insertions(+), 973 deletions(-)
```

No commit or push was performed. Only `care_dashboard_versionB.py` and this new documentation file were written to.

---
---

# Pass 2 — Global section-header / spacing repair

## 10. Confirmed problem

Follow-up report: section titles, subtitles, card labels and explanatory text rendering too close to (or colliding with) neighbouring content in multiple places beyond Prediction Summary — described as a global CSS/layout-flow problem rather than a single-section bug.

## 11. Full CSS audit performed

Read the entire `<style>` block in `care_dashboard_versionB.py` line by line (not spot-checked) and catalogued every rule touching spacing/positioning:

| Rule | What it did |
|---|---|
| `[data-testid="stVerticalBlock"] { gap: 0.4rem; }` | Global gap between stacked elements in every vertical block |
| `[data-testid="stHorizontalBlock"] { gap: 0.6rem; }` | Global gap between columns (already fixed to not carry `align-items` in Pass 1) |
| `[data-testid="stElementContainer"] { margin: 0; }` | **Zeroed every element's own natural margin**, making inter-element spacing depend entirely on the parent's flex `gap` |
| `[data-testid="stMarkdownContainer"] p { margin-bottom: 0.25rem; }` | Small paragraph spacing |
| `[data-testid="stCaptionContainer"] p { margin: 0; }` | Zeroed caption paragraph margin |
| `.care-section-title { margin-bottom: 1px; }` | **Only 1px gap between a section title and whatever follows it** |
| `.care-section-subtitle { margin-bottom: 5px; }` | **Only 5px gap between a subtitle and the section's actual content** |

No `position: absolute`, no `transform`, and no negative margins were present anywhere in the file (confirmed by search — none of those three patterns appear at all). The mechanism was margin/gap collapse, not positioning.

**Two things stood out as genuinely undersized against a safe-flow standard**: the section-title margin-bottom (1px) and the section-subtitle margin-bottom (5px) — both well under a defensible "safe gap" for a heading directly followed by cards/charts/widgets. Combined with element margins being fully zeroed elsewhere, the *only* thing standing between a heading and the first card in several sections was the ambient 0.4rem flex-gap — and that gap is exactly the mechanism Pass 1 already proved can fail to apply reliably in specific Streamlit-internal contexts (bordered containers, in particular).

## 12. Fix — one consistent section-header standard, plus a real spacing floor

**a) Section-header standard**, applied identically to all 9 sections via `section_header()` (used by every section, so this is one change, not nine):
```css
.care-section-title {
    font-size: 0.94rem; font-weight: 800; letter-spacing: 0.01em;
    color: ...; margin: 0 0 10px 0; line-height: 1.2;
}
.care-section-title.has-subtitle { margin-bottom: 3px; }
.care-section-subtitle {
    font-size: 0.73rem; color: ...; line-height: 1.3;
    margin: 3px 0 10px 0;
}
```
```python
def section_header(number, title, subtitle=None):
    title_cls = "care-section-title has-subtitle" if subtitle else "care-section-title"
    st.markdown(f"<div class='{title_cls}'>{number}. {title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='care-section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)
```
The element that's actually followed by content — the title in the 5 sections without a subtitle (1, 2, 3, 4, 9), the subtitle in the 4 that have one (5, 6, 7, 8) — always carries a 10px bottom margin. Where a subtitle exists, the title's own margin collapses to a small 3px separator instead, so there is never a doubled gap and never a near-zero gap, regardless of which element sits directly above the section's content.

**b) Restored a real per-element margin as a spacing floor**, replacing the rule that zeroed it:
```css
[data-testid="stElementContainer"] { margin-bottom: 0.35rem; }
```
This means every pair of sibling elements now has a guaranteed ~5.6px of margin *on top of* whatever the parent's flex `gap` (0.5rem, nudged up slightly from 0.4rem) contributes — so total inter-element spacing no longer depends on gap resolving correctly in every context; margin alone is already enough to prevent visual collision even in a context where gap were to fail exactly as it did for the two Pass-1 bugs.

**c) Added `overflow-wrap: break-word`** to markdown/caption paragraph rules, so long text (a longer feature definition, a longer season description) always wraps within its container rather than overflowing into a neighbour.

No fixed heights, no negative margins, no absolute positioning, and no `!important`-forced zeroing were introduced anywhere in this pass. Font sizes were not changed.

## 13. Full re-audit, all 9 sections, both required widths

Re-tested from scratch at both 1440×900 and 1920×1080, in the same worst-case content state as Pass 1 (postcode `G5 0RX`, High risk), scrolling the complete page top to bottom and checking every section-title→subtitle→content transition and every section-to-section boundary:

| Section | Title fully visible | Subtitle fully visible | Safe gap before content | Content starts below title | No clipped text |
|---|---|---|---|---|---|
| 1. Enter Postcode | ✅ | n/a | ✅ | ✅ | ✅ |
| 2. Prediction Summary | ✅ | n/a | ✅ | ✅ | ✅ |
| 3. Location Details | ✅ | n/a | ✅ | ✅ | ✅ |
| 4. Risk Map | ✅ | n/a | ✅ | ✅ | ✅ |
| 5. Monthly Rainfall Exposure | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6. Historical Rainfall Summary | ✅ | ✅ | ✅ | ✅ | ✅ |
| 7. Seasonal Risk Overview | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8. Why This Result? | ✅ | ✅ | ✅ | ✅ | ✅ |
| 9. Recommendations | ✅ | n/a | ✅ | ✅ | ✅ |

Confirmed at both widths: all section boundaries (1→2 through 8→9) clean, footer's two lines clearly separated, Reset All reverts correctly, map click-to-select re-renders the whole right-hand panel (SHAP, monthly table) without disturbing layout.

## 14. Version A hash (Pass 2)

```
Before Pass 2: ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f
After Pass 2:  ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f
```
Identical. `git diff -- 007_Dashboard/care_dashboard_versionA.py` produces no output. The file was never opened for editing.

## 15. Confirmation: research/model/data unchanged (Pass 2)

Every edit in this pass was confined to the `<style>` block and the `section_header()` helper function. No change touched `FEATURE_COLS`, model loading/prediction, `shap.TreeExplainer`, the rainfall aggregation functions, `HISTORICAL_RAINFALL_STATS`, `RAINFALL_TREND`, `PRECAUTIONS`, or any risk-classification logic.

## 16. Git safety (Pass 2, final)

```
$ shasum -a 256 007_Dashboard/care_dashboard_versionA.py
ed3e865eee9859911d15a56478beadaeb7fa109dae9cb155f4a04eb23a96799f

$ git diff -- 007_Dashboard/care_dashboard_versionA.py
(no output)

$ git status --short | grep 007_Dashboard
 M 007_Dashboard/care_dashboard_step1.py       (pre-existing staged state, predates both passes)
 M 007_Dashboard/care_dashboard_step3.py       (pre-existing staged state, predates both passes)
 M 007_Dashboard/care_dashboard_versionA.py    (pre-existing staged state — working tree unchanged, see diff above)
MM 007_Dashboard/care_dashboard_versionB.py    (both passes' fixes)
 A 007_Dashboard/care_paths.py                 (pre-existing staged state, predates both passes)
?? 007_Dashboard/FINAL_DASHBOARD_A_B_AUDIT.md
?? 007_Dashboard/VERSION_C_COMPACT_UI_AUDIT.md
?? 007_Dashboard/VERSION_C_IMPLEMENTATION_AUDIT.md
?? 007_Dashboard/VERSION_B_LAYOUT_QA.md
```

No commit or push was performed at any point across either pass.
