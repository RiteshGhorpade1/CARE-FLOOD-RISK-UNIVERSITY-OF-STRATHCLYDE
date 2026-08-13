# CARE Dissertation — Final Visual & Word-Count Audit

Session: 2026-08-11, "Final 10,000-word / high-distinction visual enhancement pass."
Source of truth: `006_Dissertation/CARE_Dissertation_Chapters_1to6_Draft.md`.
Deliverable: `006_Dissertation/CARE_Dissertation_FINAL.docx` (regenerated this session via
`pandoc --reference-doc=<pre-session backup>`, so all fonts/heading/caption styles are
inherited from the working document rather than pandoc defaults).

## UPDATE (same day, second pass — "Final High-Distinction Revision")

A second pass this session found and fixed several real, concrete bugs beyond the
first pass's word-count/visual work, and added the mathematical-foundations content
requested:

- **Word count now 10,622** (up from 10,368 after this pass's additions; see
  `FINAL_WORD_COUNT_REPORT.txt` for the full chapter-by-chapter breakdown). Still
  comfortably inside 9,000–11,000, close to the 9,800–10,500 soft target.
- **Real bug found and fixed**: inline LaTeX math (`$r = -0.74$ vs. $-0.28$` in §3.3,
  and the `flood_risk` piecewise formula in §3.5) was being converted by pandoc into
  OMML equation objects that don't extract as plain text — rendering as literal gaps
  ("... water body ( vs. ), motivating...") when read back. This matches exactly the
  "(** vs.**)" pattern flagged as a known prior issue. Fixed by converting all math to
  plain-text/Unicode notation (monospace code blocks), eliminating the OMML path
  entirely rather than trying to verify OMML rendering without Word available.
- **Table 3.1 "see below" placeholders fixed** with real computed values from
  `feature_matrix_40yr.csv`: `mean_winter_mm_day` 3.33–3.73 mm/day, `max_daily_mm`
  31.72–33.32 mm.
- **Formulas added** (Accuracy, Precision, Recall, F1, Macro-F1 in §3.7; Random Forest
  ensemble notation in §3.6; SHAP additive formulation in §3.8), each with the
  formula → variable definitions → why-it's-used → CARE-relevance structure requested,
  using the project's actual implementation (e.g. macro F1 justified against the
  actual 48/34/17% class split, not a generic statement).
- **New Figure 1.3** — an 18-stage project roadmap diagram (§1.9), matching the house
  visual style (teal palette, rounded boxes) already used by Figures 1.1/3.3/3.7/etc.,
  built from real project stages only (Research Problem → ... → Conclusions & Future
  Work), in a compact 3×6 boustrophedon layout. 43 figures total now (was 42).
- **Chapter page-break bug found and fixed**: only Chapter 1 had an explicit page
  break; Chapters 2–6 relied on a markdown `---` divider, which renders as a
  horizontal rule, not a page break — so Chapters 2–6 likely did *not* reliably start
  on new pages. Fixed at the style level (`pageBreakBefore` added to the `Heading1`
  Word style, which every chapter and every major front-matter section uses), which
  also required *removing* the 15 manual page-break blocks that had accumulated
  through prior sessions' markdown (they would have doubled up with the new
  style-level break, producing blank pages) — net effect: cleaner markdown source and
  more robust page breaks that survive future edits without manual upkeep.
- **Headings centre-aligned**: `Heading1` and `Heading2` styles both patched with
  `<w:jc w:val="center"/>`, satisfying the "chapter and section headings must be
  centre-aligned" requirement without touching body-paragraph alignment.
- **Page numbering fixed**: the prior simplified regeneration had collapsed the
  document to a single section using lower-Roman numerals throughout (including the
  main body) — the opposite of the "main body must use 1, 2, 3..." requirement.
  Restored a genuine two-section split (front matter: lower-Roman from i; main body:
  Arabic restarting at 1), reusing the two footer parts (`footer1.xml`/`footer2.xml`,
  each with a real `PAGE` field) already present via `--reference-doc` inheritance.
- **§ symbol, AI-reference, and local-path sweeps**: all clean. Every `§` in the
  source is followed by a section number (§3.9, §1.1, etc.) — no bare/standalone
  artefacts found. No "Claude", "Anthropic", "AI-generated", or similar strings
  anywhere in the dissertation text. No `/Users/riteshghorpade/...` absolute paths
  anywhere in the dissertation text (Appendix A already used repo-relative paths).
- **List of Figures / List of Tables re-verified against the regenerated docx**:
  43/43 figures and 13/13 tables match exactly between the front-matter lists and the
  body captions (script-verified, not assumed).

**Still outstanding** (unchanged from the first pass): no Word/LibreOffice is
available in this sandboxed environment, so the regenerated docx's visual rendering
(TOC field populating on "Update Fields", page breaks landing correctly, the page
border inherited from the reference doc, font sizes) has been verified structurally
(XML well-formed, styles present, correct values) but not visually. This remains the
one verification step requiring the student to do before submission — see the
"Known limitation" section at the end of this file, which still applies.

## Word count (the headline requirement, first-pass figures — superseded above)

**True main-body count: 10,368 words** (Chapter 1 heading → References heading, matched
on paragraph style = Heading1/Heading2 + exact text, not substring match — see "Bug found
and fixed" below). This is inside the required 9,000–11,000 range and close to the
10,000 target.

| Stage | True count (corrected method) |
|---|---|
| Start of session (before any edits) | 11,713 |
| End of session (after cuts + new evidence) | **10,368** |

**Bug found and fixed during this session**: the word-count script used throughout most
of this session's editing matched the *first paragraph whose text starts with* `"Chapter
1"` as the main-body start boundary. The front matter's own "List of Figures" section
contains a bold lead-in line reading "Chapter 1 — Introduction" (grouping that chapter's
figure entries) — a plain-text paragraph, not a heading — and the script matched *that*
line instead of the real `Heading 1`-styled "Chapter 1: Introduction" chapter heading
120 words later. This made every in-session word-count checkpoint read ~600 words too
high (each checkpoint was actually measuring from partway through the front matter, not
from the real Chapter 1). It did not corrupt the document — the qualitative editing
(which sections to cut, what new evidence to add) was sound regardless of the exact
number — but it meant the session's cutting effort overshot what was strictly necessary.
The true final count (10,368) is comfortably inside range; had the bug not been caught,
the reported figure would have read 10,985, which is also inside range but closer to the
1,000-word ceiling with less margin. Fixed by requiring the boundary paragraph's `pStyle`
to start with `Heading` in addition to the text match. The Declaration's word-count line
and this file both report the corrected, true figure.

## Figures: 42 total (was 41; +1 this session)

All sequential, no gaps, all captions match the List of Figures front matter exactly
(script-verified), all 42 image files resolve on disk (script-verified).

| Ch | Figures | Count |
|---|---|---|
| 1 | 1.1–1.2 | 2 |
| 2 | 2.1 | 1 |
| 3 | 3.1–3.18 | 18 |
| 4 | 4.1–4.15 | 15 |
| 5 | 5.1–5.6 | 6 |

**New this session — Figure 4.15**: "Near-Clyde audit: recomputed risk class and PVA
membership for all 528 points within 150m of the Clyde, against elevation and distance
to river." Evidence source: this session's independent point-in-polygon re-verification
of `flood_risk` labelling against the raw `PVAv2.gpkg`, plotted from the real,
unmodified audit output (`002_Dataset/outputs/clyde_pva_audit_scatter.png`, generated
with the `dataviz` skill, risk-class colours matched to the existing dashboard/dissertation
convention). Discussed in §4.14 immediately above and below the image (what it shows, why
81 near-river Low-risk points exist, why that's expected not a defect). Cross-referenced
from §3.11.

**Everything else audited as already covered, per the plan's category table (A–R in the
original request)** — no further new figures were added for categories already
satisfied by existing figures (research workflow, system architecture, spatial maps,
model evaluation, spatial validation, SHAP, dashboard screens, user evaluation charts),
to avoid decorative duplication per the request's own "more evidence, not more
decoration" principle.

## Tables: 13 total (was 11; +2 this session)

All sequential, no gaps, all captions match the List of Tables front matter exactly.

| Ch | Tables | Count |
|---|---|---|
| 2 | 2.1 | 1 |
| 3 | 3.1–3.3 | 3 |
| 4 | 4.1–4.6 | 6 |
| 5 | 5.1 | 1 |
| 6 | 6.1–6.2 | 2 |

**New this session:**
- **Table 4.5** — Independent near-Clyde spatial audit: recomputed vs. stored `flood_risk`
  label. Rows for 50m/100m/150m thresholds; 0 mismatches at every threshold (real,
  unmodified audit result).
- **Table 4.6** — Four historical flood events: agreement with model prediction. Event |
  Date | Nearest grid point | Model prediction | Consistent? | Why, for all four events
  (2002 Greenfield, 1994 SEC Centre, 1994 Central Station, 1795 Saltmarket), using the
  exact verified numbers computed earlier this session (geocoded via OSM Nominatim,
  matched to nearest grid point, model run live).

Both placed at the end of §4.14 (Chapter 4's last section) specifically so their
insertion required no renumbering of any figure/table in Chapter 5 or 6.

## Discussed-in-text / caption / cross-reference status

- Every figure and table is introduced in prose before or immediately after it appears
  (script-verified: no dangling `Figure X.Y` or `Table X.Y` reference without a
  corresponding caption elsewhere in the document).
- Every `Section X.Y` cross-reference resolves to an actual section heading
  (script-verified: zero dangling section references).
- All 42 image file paths resolve on disk (script-verified).
- Captions follow the "what it shows, not just its name" convention already established
  in the document (e.g. Figure 4.15's caption states what's plotted and over what
  population, not just "Clyde audit chart").

## Deliberately skipped (judgement calls, flagged for visibility)

Per the original request's own principle ("if the answer to 'what does this help the
examiner understand' is unclear, don't include it"):

- **New research-workflow diagram** — already covered collectively by Figures 1.1, 3.3,
  3.4, 3.7, 3.8, 3.18; a 12th pipeline-style diagram would duplicate, not add, evidence.
- **New Version A/B comparison figure** — Table 3.2 already does this; an unused
  `figure_3_versionA_vs_B.png` asset was found during the pre-pass audit but left unused
  as redundant with the table, consistent with the "no duplicated figures" rule.
- **A dedicated Limitations framework table** (data/model/spatial/temporal/user/dashboard)
  — §3.19 and §6.7 already cover the same categories in prose (7 bolded categories);
  given the word-count pressure this session, a duplicate table was judged lower value
  than the word budget it would cost.
- **A second historical-events map** — the four events are already visible as markers on
  the live dashboard (shown in Figures 3.9/3.10's screenshots); Table 4.6 carries the
  comparison data. A new static map was judged redundant.
- **Reproducibility diagram** — added as a plain-text workflow list at the top of
  Appendix A (word-count-free, since Appendix content is excluded from the main-body
  count) rather than a numbered Figure, to avoid front-matter List-of-Figures overhead
  for a non-body item.

## What changed structurally this session

- Chapter 3 §§3.9–3.17 (dashboard screen-by-screen descriptions) compressed most
  heavily — these narrated UI content already fully shown in 8 screenshots with their
  own captions; compressed to "what it shows + one analytical line" per section, leaning
  on Table 3.2 for the feature comparison instead of restating it in prose.
- The historical-events discussion, previously a single 120-word run-on sentence buried
  in §3.11, was extracted into Table 4.6 with proper per-event analysis; §3.11 now just
  points to it.
- Chapters 2 and 6 had their prose tightened against Tables 2.1/6.1/6.2, which already
  carried the same information in structured form — cut the restatement, kept the
  citations and the original synthesis argument.
- Chapter 4 (Results, the 35%-weight Analysis chapter) was deliberately protected from
  cuts and is the only chapter that grew, carrying the two new evidence tables + figure.
- One sentence added near Figure 3.8 explicitly naming the "model layer" vs.
  "communication/visualisation layer" two-tier framing requested, without adding a new
  figure.

## Verification methods used (all script-based, not eyeballed)

1. Word count: python-docx traversal of `document.xml` body in reading order,
   paragraphs + table cells, bounded by `Heading`-styled "Chapter 1" → "References".
2. Figure/table sequence: regex extraction of every `Figure X.Y —` / `Table X.Y —`
   caption from the docx, deduplicated, sorted numerically, checked for gaps.
3. Cross-references: regex extraction of every `Figure X.Y`, `Table X.Y`, `Section X.Y`
   mention in the source markdown, diffed against the set of actual captions/headings.
4. Image paths: `os.path.exists()` on every markdown image reference.
5. Structural sanity: embedded-media count (85 files) and paragraph/table count
   (478 paragraphs, 15 tables) confirmed non-zero and consistent with a 42-figure,
   13-table document after regeneration.

## Known limitation of this verification

No Word or LibreOffice binary is available in this sandboxed environment, so the docx
could not be visually rendered/screenshotted to confirm print-layout appearance (font
sizes, page breaks landing sensibly, the TOC field's page numbers). The TOC field itself
is present and correctly coded (`TOC \o "1-3" \h \z \u`), and `settings.xml` has
`updateFields` set so Word will prompt to populate it on first open — but this has not
been visually confirmed to render correctly, only structurally confirmed to be present
and well-formed. Recommend the student open the file in real Word, accept the "Update
Fields?" prompt (or press Ctrl+A, F9), and do one final visual read-through before
submission.
