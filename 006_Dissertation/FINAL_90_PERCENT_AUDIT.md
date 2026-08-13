# CARE Dissertation — Final Marking-Criteria Audit

Evaluates `CARE_Dissertation_Chapters_1to6_Draft.md` / `CARE_Dissertation_FINAL.docx` (as regenerated this session) against the marking dimensions a Type-3 (Application Based) MSc dissertation is assessed on. This is a candid, evidence-based self-assessment, not a grade prediction — **no percentage or grade band is promised**. Each dimension states what evidence exists, its strength, its weakness, a priority for any further work, and a concrete recommendation. Nothing below is fabricated; where evidence is thin, that is stated as a weakness rather than papered over.

---

## 1. Research problem

**Evidence**: §1.1–1.2 frame a specific "translation gap" (authoritative flood data exists but doesn't convert into individual action), grounded in Rizzoli and Young (1997) and Power and Sharda (2009), and made concrete with two real Glasgow flood events (2002, 1994).
**Strength**: The problem is specific, motivated by cited literature (not just assertion), and scoped to something an MSc project can actually address (a translation/communication gap, not "solve flooding").
**Weakness**: The problem statement is not independently corroborated by, e.g., evidence that SEPA or Glasgow City Council have identified this exact translation gap as a stated priority — the motivation rests on academic literature and the two historical events, not a needs-assessment with the target user group.
**Priority**: Low.
**Recommendation**: None required; a single sentence noting the problem statement is literature-derived rather than needs-assessment-derived would pre-empt an examiner's question, but this is optional polish, not a gap.

## 2. Research gap

**Evidence**: §1.3, three gaps (no integrated system; descriptive-not-prescriptive tools; explanation as diagnostic-not-user-facing), each cited, cross-referenced to Chapter 2's fuller treatment, and made visually concrete (Figure 1.2 Venn diagram, Table 2.1 gap matrix).
**Strength**: Unusually well-hedged — §1.3 explicitly states the "no comparable system found" claim is bounded to the review's own search terms and databases, not an exhaustive claim about the world. This is exactly the kind of self-aware scoping that distinguishes strong from merely competent gap statements.
**Weakness**: The systematic review (§2.1) used three databases and stated search terms but does not report a PRISMA-style count of records screened/excluded, so the gap claim's evidential base, while credible, is not independently auditable in the way a formal systematic review would be.
**Priority**: Low.
**Recommendation**: None required for Type-3 scope; a full PRISMA flow diagram would be disproportionate to an MSc application-based project.

## 3. Literature criticality

**Evidence**: Chapter 2, six themed sections (§2.2–2.7), each with an explicit "What is known" / "Strengths, weaknesses, and disagreement" / "Gap" structure, converging in §2.8's critical synthesis; this session added one further critical point (§2.2, geographic/hydrological transferability of the benchmarked flood-susceptibility studies).
**Strength**: This chapter is genuinely critical, not just descriptive — it identifies disagreement (§2.2, which ensemble variant is best), a structural DSS-field problem (§2.3, rigor cycle vs. under-executed relevance cycle), a raster/vector scale-mismatch limitation (§2.4), SHAP's specific epistemic limits (§2.5, explains model behaviour not causation), and — the standout point — §2.8's observation that the XAI and risk-communication literatures don't cite each other, which is the reviewer's own synthesis, not restated from a single source.
**Weakness**: All 34 references are relatively recent (2001–2022) foundational/survey papers; there is limited engagement with more recent (2023–2026) flood-risk ML or XAI-in-HCI literature, which may exist and would strengthen currency.
**Priority**: Medium.
**Recommendation**: If time permits before submission, a targeted search for 2023–2026 work specifically on XAI presentation to non-specialist/lay audiences (the exact gap §2.8 identifies) would let the dissertation claim its gap is current, not just historically under-addressed.

## 4. Methodology

**Evidence**: Chapter 3 documents Design Science Research (Hevner et al., 2004) as the explicit methodological frame (§3.1), with rigor-cycle/relevance-cycle separation carried through consistently; data sources, feature engineering, label construction, ML methodology, SHAP methodology and evaluation methodology are each given their own section with parameters stated exactly (`n_estimators=100`, `random_state=42`, 80/20 stratified split). **Updated this session**: §3.6–3.8 now state the actual formulas underpinning the methodology — the Random Forest ensemble rule, the full metric set (Accuracy/Precision/Recall/F1/Macro-F1) with macro F1's justification tied to the real 48/34/17% class split, and SHAP's additive decomposition — each with variable definitions and a one-line "why this, for CARE" justification, not inserted as decoration.
**Strength**: Reproducibility-minded — exact hyperparameters, exact split sizes, exact CRS handling, a stated rationale for every non-obvious choice (e.g. why `dist_to_clyde` is separate from `dist_to_water`, why macro F1 over accuracy), and now the formal notation for every metric and mechanism actually used, closing a mathematical-foundations gap a reader could previously only infer from prose. This session also fixed a real data-integrity gap: Table 3.1 previously had two "see below" placeholders (`mean_winter_mm_day`, `max_daily_mm`) that pointed nowhere — now populated with the actual computed ranges from the feature matrix.
**Weakness**: The methodology for participant recruitment (§3.17) is thin on justification for *why* three-per-version was the chosen sample size (as opposed to, e.g., a resourcing constraint stated honestly) — it is disclosed as a limitation (§3.19) but not methodologically justified at the point of design.
**Priority**: Low.
**Recommendation**: A one-sentence addition to §3.17 stating the sample size was resourcing-bounded (if true) rather than power-calculated would close this gap without new content being invented.

## 5. Technical implementation

**Evidence**: Chapter 3 §3.9–3.16 documents the dashboard architecture (Figure 3.8), both dashboard versions, and the recommendation engine; Appendix A gives full reproduction instructions (environment, hardcoded-path limitation disclosed honestly, launch commands, troubleshooting).
**Strength**: The implementation is real and runnable (confirmed via Appendix A.9's manual verification log, and via this session's own regeneration work touching the same repository), not merely described in the abstract. The hardcoded-path limitation (A.3) is disclosed as exactly that — a genuine limitation — rather than hidden.
**Weakness**: No `requirements.txt`/environment manifest is version-pinned in a way visible from the dissertation body itself (it's described in Appendix A.2 as "~140 packages," which is honest but not maximally reproducible without the actual file).
**Priority**: Low.
**Recommendation**: None required — Appendix A.2 already discloses this candidly, and the actual `requirements.txt` exists in the repository even if not reproduced in full in the appendix.

## 6. Model evaluation

**Evidence**: §4.2–4.6: accuracy (99.62%), macro F1 (99.50%), per-class P/R/F1 (Table 4.1), confusion matrix (Figure 4.1), 5-fold CV (99.26% ± 0.17%), XGBoost benchmark (Table 4.2), ROC-AUC (Figure 4.5, 0.9998 mean). **Updated this session**: §4.14 now adds two independent checks that speak directly to this dimension's previously-largest weakness — Table 4.5 (a from-scratch point-in-polygon re-verification of `flood_risk` labelling for all 528 grid points within 150m of the Clyde against the raw `PVAv2.gpkg`, not the stored label: zero mismatches at every distance threshold) and Table 4.6 (agreement between the live model's predictions and four independently geocoded historical flood events, 1795–1994: two agree, two don't, each disagreement traced to a named, specific cause rather than left as unexplained noise).
**Strength**: Comprehensive and multi-angle (not just accuracy) — precisely the kind of evaluation depth Type-3's "Analysis" weighting rewards. The critical caveat (§4.2, §4.14) that this is engineered-label reconstruction, not real-world validation, is stated at first mention, not buried. The two new checks are a genuine, if partial, answer to this section's own previous "no independent ground truth" weakness: Table 4.5 confirms the label-construction *implementation* is correct (not just plausible), and Table 4.6 is the closest thing in the dissertation to real-world validation — small-sample (n=4) and explicitly reported as such, but honestly interpreted (2/4 agree, with the two disagreements attributed to specific, named, non-arbitrary causes: an underground/tunnel-transmitted flood pathway the surface features cannot see, and a PVA-zone boundary gap of exactly the kind Table 4.5 shows is common near the river) rather than cherry-picked or hidden.
**Weakness**: All evaluation is still fundamentally against the same engineered label the model partially reconstructs from its own inputs. Table 4.6's n=4 historical check is illustrative, not a substitute for genuine independently-observed-outcome validation at scale — the dissertation is explicit about this (§4.14: "too small to generalise from"), which is the correct way to present it, but the underlying evidential gap (no large-scale independent ground truth) remains the single largest one in the dissertation.
**Priority**: High (as a disclosed limitation, correctly handled and now partially, honestly probed — not a fixable gap within this project's scope, but the dissertation's own most important self-critique, and now backed by two concrete checks rather than assertion alone).
**Recommendation**: None beyond what's already done — §6.8 correctly identifies real-flood-outcome validation *at scale* as the top future-work priority; the new n=4 historical check and n=528 spatial audit are honest, bounded contributions toward that, not a claim of having closed the gap.

## 7. Spatial validation

**Evidence**: §4.4, Figure 4.3: a second 5-fold `GroupKFold` CV withholding complete 500 m spatial tiles, giving 99.21% (± 0.36%) accuracy — closely matching the random-split figures, interpreted correctly as "does not materially alter performance for label reconstruction at this block scale" rather than overclaimed as proof of real-world generalisation.
**Strength**: This is a genuinely sophisticated methodological addition (added in this project's more recent work per the commit history) that most comparable MSc projects would omit — testing for spatial autocorrelation inflation is a real methodological strength.
**Weakness**: Only one block size (500 m) was tested; sensitivity to block size is not explored, so the robustness of "does not materially alter performance" is asserted at one scale only.
**Priority**: Low.
**Recommendation**: Optional if time allows: one additional block size (e.g. 1 km) would strengthen the claim; not essential given the honest single-scale framing already in place.

## 8. SHAP / explainability

**Evidence**: §3.8 (methodology), §4.7–4.8 (global/local technical results), §3.15 (live user-facing interface), §5.10 (real participant evidence on its effect).
**Strength**: This is the dissertation's strongest cross-chapter evidence chain — methodology → technical result → live implementation → real user comprehension data, closing the loop that most XAI dissertations leave open (implementing SHAP but never testing whether a non-specialist actually understands it). The finding that explainability increased trust for all three Version B participants *while also* introducing technical friction for two of the same three (§5.10) is a genuinely nuanced, non-obvious result, correctly not oversimplified into a pure success story.
**Weakness**: The XGBoost SHAP magnitude-comparability limitation (§4.5) is a real, disclosed technical constraint, not a design choice — worth noting it slightly weakens the strength of the RF-vs-XGBoost SHAP comparison specifically (rankings, not magnitudes, are comparable).
**Priority**: Low.
**Recommendation**: None required; already disclosed appropriately.

## 9. Dashboard contribution

**Evidence**: Two-version comparative design (§3.9–3.11, Table 3.2) built specifically to isolate the SHAP layer's effect — a genuine experimental-design choice, not an incidental byproduct of iterative development.
**Strength**: The deliberate A/B structure is itself a methodological contribution beyond "we built a dashboard" — it enables the §5.9–5.10 between-groups comparison that produces the dissertation's most interesting finding.
**Weakness**: Object 4's evaluation is between-groups, not within-subject (§5.9's own caveat) — no participant saw both versions, so the comparison, while genuine, cannot isolate individual preference from version assignment.
**Priority**: Low (already disclosed as a limitation, §6.7).
**Recommendation**: None required beyond the existing disclosure.

## 10. User evaluation

**Evidence**: Chapter 5 in full — six real participants, 11-question structured questionnaire, thematic analysis (Braun and Clarke, 2006), verified against the actual source spreadsheet rather than a blank template (§5.1).
**Strength**: This is real primary evidence, not simulated or assumed — and, unusually for a student project, its own data-quality problems are disclosed in full (§5.13: missing response ID, P05 identical-wording anomaly, P06's Q3/Q4-5 contradiction, shared timestamps) rather than quietly cleaned up. This kind of transparency is a genuine strength that examiners specifically reward.
**Weakness**: n=6 (3/3 split) is a small, non-random convenience sample — explicitly and correctly described throughout as exploratory/indicative, never as statistically generalisable. The originally planned moderated think-aloud protocol was not delivered (self-completed questionnaire instead) — disclosed, not hidden.
**Priority**: Medium (as a scope constraint, not a fixable flaw at this stage).
**Recommendation**: None achievable before the 17 August 2026 deadline; correctly flagged as future work (§6.8, "a larger, moderated usability study").

## 11. Critical discussion

**Evidence**: §5.14 (discussion against RQs), §4.14 (critical interpretation of results), §6.3–6.4 (RQ answers and contribution, each qualified).
**Strength**: Consistently avoids overclaiming — e.g. §6.3's "positive answers with a scoped caveat, not unqualified success claims," and §5.10's explicit statement that "the evidence does not support an unqualified success claim." This is exactly the register a distinction-level critical discussion should use.
**Weakness**: The critical discussion is strong on qualifying the project's own results but has comparatively less discussion of *alternative interpretations* of the SHAP-friction finding (e.g., is the friction a SHAP-presentation problem specifically, or a general "any new interface element adds initial friction" effect that would appear with any added panel, SHAP or not?). This alternative explanation is not explicitly ruled out or considered.
**Priority**: Medium.
**Recommendation**: One additional sentence in §5.10 or §5.14 acknowledging that the friction finding cannot fully distinguish "SHAP-specific comprehension cost" from "general cost of any additional interface element" (since the comparison is between-groups on version, not on SHAP-presence holding interface complexity constant) would strengthen the critical discussion further. This is a genuine, addable point of critical nuance — not required to reach a defensible dissertation, but the kind of observation that separates a good critical discussion from a very good one.

## 12. Originality / contribution

**Evidence**: §1.7, §6.4 — a four-part contribution (integration, prescriptive design, user-facing explainability, bounded scope), explicitly framed as a systems/communication contribution, not ML novelty.
**Strength**: Honest positioning — the dissertation does not claim algorithmic novelty it doesn't have, and is explicit that Random Forest, XGBoost and SHAP are all established techniques (Chapter 2). This session added a further bounding clause to §6.4 tying the originality claim explicitly to the review's own search scope (§1.3), preventing an examiner reading Chapter 6 in isolation from over-crediting the originality claim.
**Weakness**: "Deliberately bounded scope" (contribution element 4, §1.7) is a project-management decision reframed as a contribution — an examiner may reasonably question whether scope-boundedness is itself a "contribution" in the conventional sense, as flagged in the Objective-Evidence Matrix (Objective 4 discussion).
**Priority**: Low.
**Recommendation**: Consider whether contribution element 4 is better framed as a design decision supporting rigor (which it genuinely is) rather than a fourth co-equal "contribution" alongside the other three substantive ones — a wording nuance, not a content gap.

## 13. Limitations

**Evidence**: §3.19 (7 named limitations), §4.14 (label-circularity interpretation), §5.13 (data-quality anomalies), §6.7 (consolidated limitations).
**Strength**: This is one of the dissertation's clearest strengths — limitations are disclosed at first relevant occurrence throughout the document (not reserved for a single closing section), consistent with the explicit design choice stated repeatedly ("disclosed throughout rather than reserved for this section"). The engineered-label/circularity concern in particular is treated as a first-class methodological caveat, not a footnote.
**Weakness**: None identified — this is comprehensive and honest.
**Priority**: None.
**Recommendation**: None; this is a model to be preserved, not improved.

## 14. Conclusions

**Evidence**: Chapter 6 in full — RQ answers with evidence (Table 6.1), practical/technical recommendations tied to specific participant evidence (§6.5–6.6), future work each tied to a named limitation (§6.8), final conclusion (§6.9).
**Strength**: Table 6.1's evidence matrix is a genuinely strong presentation device — Research Question → Evidence → Main Finding → Limitation → Conclusion in one traceable table is exactly the kind of end-to-end auditability a Type-3 marking scheme rewards under "Conclusions" and "Structure."
**Weakness**: None substantive; §6.9's Final Conclusion is appropriately compact rather than repetitive of §6.2's Research Summary, though there is inevitably some restatement of the aim (typical and appropriate for a conclusions chapter's closing paragraph, not a flaw).
**Priority**: Low.
**Recommendation**: None required.

## 15. Referencing

**Evidence**: 34 Harvard-style `(Author, Year)` references, alphabetised, every reference-list entry cited in-text and vice versa (verified this session — no new citations added without a matching reference-list entry, no references removed).
**Strength**: Consistent style throughout, correctly following the Style Guide's Harvard-or-numbered choice.
**Weakness**: None identified structurally; currency of the literature (2023–2026 gap) is noted under "Literature criticality" above rather than repeated here.
**Priority**: Low.
**Recommendation**: None beyond the literature-currency point already raised in §3 above.

## 16. Presentation

**Evidence (updated same-day, second pass — supersedes both entries below the line)**: Beyond the first pass's word-count fix, this pass found and fixed three further real presentation bugs: (1) only Chapter 1 had an actual page break — Chapters 2–6 relied on a markdown `---` divider that renders as a horizontal rule, not a break, so they likely did not reliably start on new pages; fixed at the `Heading1` style level (`pageBreakBefore`), which is more robust than the per-chapter manual breaks it replaced (survives future edits without re-adding markup by hand). (2) Headings were not centre-aligned; both `Heading1` and `Heading2` styles now carry `<w:jc w:val="center"/>`, applied without touching body-paragraph alignment. (3) Page numbering had collapsed to a single lower-Roman section covering the *entire* document, including the main body — the opposite of the "main body must be 1, 2, 3" requirement; restored a genuine two-section split (front matter lower-Roman, main body Arabic restarting at 1) by reusing the two footer parts already inherited via `--reference-doc`. Word count is now **10,622** (up from 10,368, after adding formulas and a new figure — see below).
**Strength**: All three fixes are structural (style/section-level), not manual per-instance patches, so they are far less likely to silently break on the next markdown edit than the per-heading raw-XML approach used in earlier sessions. The word-count resolution from the first pass holds.
**Weakness**: **No Word or LibreOffice binary is available in this sandboxed environment.** All of the above (page breaks landing correctly, headings actually rendering centred, the TOC field populating, roman-then-arabic page numbers actually appearing in the footer) has been verified structurally — the correct XML properties are present and well-formed, and python-docx confirms the *style definitions* carry the expected alignment/break/numbering values — but none of it has been visually confirmed by opening the file. This is the single largest remaining verification gap across this entire session's work, disclosed here rather than assumed away.
**Priority**: Low (word count, structural formatting fixes all applied) / Medium (visual verification still outstanding — this is now the top remaining action item).
**Recommendation**: Before submission, open the file in real Word: accept the "Update Fields?" prompt (or Ctrl+A then F9) to populate the TOC and any page-number fields, and visually check that each chapter starts on a fresh page, headings appear centred, and the front matter/body page-number formats switch correctly at the Chapter 1 boundary. This is a 5-minute check that closes the one gap this session's tooling cannot verify.

---
*Prior audit entry (superseded above, kept for history):*

**Evidence**: This session regenerated the final `.docx` with a real Word TOC field (99 headings, hyperlinked, with genuinely computed page numbers — verified by actually opening the document in Word and exporting to PDF, not just structurally inspecting the XML), List of Figures/Tables/Abbreviations, two-section page numbering (front matter lower-Roman, body Arabic restarting at 1), Calibri 12pt body text, 1.5 line spacing (all confirmed directly from `styles.xml`/`theme1.xml` and visually in the rendered PDF).
**Strength**: Heading depth is genuinely compliant with the Style Guide's "should not normally be subdivided further than X.Y" guidance — confirmed mechanically this session that the entire document uses only two heading levels (Chapter, and N.N section), never N.N.N — this had been a flagged risk in a prior audit and is now confirmed clean.
**Weakness**: Word count sits ~566 words (≈5%) over the upper end of the 9,000–11,000 target band (see `FINAL_WORD_COUNT_REPORT.txt`) — a real but much smaller gap than previously believed (~1,790–2,490 words), and one this session did not attempt to close unilaterally since the residual sits almost entirely in the protected, evidence-heavy Chapters 3–5.
**Priority**: Medium.
**Recommendation**: A structural decision (not further sentence-editing) is the only realistic way to close the remaining ~566 words, e.g. converting part of Chapter 3's screen-by-screen dashboard walkthrough (§3.9–3.16) to table-only form now that Table 3.2 already covers version parity — a decision for the student/supervisor, not applied here without authorisation.

## 17. Reproducibility

**Evidence**: Appendix A in full (A.1–A.9): environment setup, exact package versions for key libraries, hardcoded-path limitation disclosed with exact constants shown, launch commands, troubleshooting, and the manual verification log (Table 4.4, A.9) distinguishing what was actually tested from what wasn't.
**Strength**: Honest about what reproducibility actually means here — macOS-only verification stated explicitly (not implied to be cross-platform), hardcoded paths flagged as a genuine operational limitation requiring manual edits on another machine, and the absence of an automated test suite disclosed as a limitation rather than glossed over (§3.19, §4.13).
**Weakness**: No CI pipeline or single-command reproduction script exists — someone reproducing this project needs to follow Appendix A's manual steps exactly, including editing hardcoded paths.
**Priority**: Low (appropriate for MSc scope, already disclosed).
**Recommendation**: None required beyond what's disclosed; a `requirements.txt`-relative-path fix would be a nice-to-have engineering improvement but is out of scope for the dissertation text itself, and modifying the dashboard scripts was outside this session's mandate (Version A protected; Version B not to be changed without explicit justification).

---

## Overall assessment (updated 2026-08-11, second pass — "Final High-Distinction Revision")

This is a genuinely well-evidenced, unusually self-critical dissertation, and this session's two passes together closed every concretely-identified open item: word count, the two new evidence checks, mathematical foundations, and a set of real (if easy to overlook) presentation bugs. Its clearest strengths are: (1) limitations disclosed throughout rather than reserved for a closing section, (2) a real, working, evaluated system rather than a purely descriptive account, (3) an SHAP-to-user-comprehension evidence chain that closes a loop most comparable projects leave open, (4) consistently precise, non-overclaiming language around what the 99.62% accuracy figure actually means, (5) two independent checks (a 528-point near-Clyde spatial audit and a four-event historical-flood comparison) that directly probe the label-circularity concern, honestly reporting partial (2/4) real-world agreement rather than a cherry-picked success, and (6) — new this pass — the methodology chapter now states its own mathematical foundations explicitly (ensemble rule, full metric set, SHAP's additive decomposition), each tied to a stated reason specific to this project, not inserted as decoration.

Its clearest remaining risk is now singular and specific: **visual/print-layout verification of the regenerated `.docx` has still not been performed**, because no Word or LibreOffice binary exists in this sandboxed environment. This pass fixed three real, confirmed presentation bugs (chapters 2–6 not reliably starting on new pages; headings not centre-aligned; page numbering collapsed to Roman-only across the whole document, including the main body) at the structural/style level — all verified correct in the underlying XML — but none of it has been seen rendered. This is a 5-minute check the student needs to do that no amount of further XML inspection can substitute for. Secondary, unchanged risks: the single-scale spatial-block validation and literature currency (2023–2026 gap) remain minor, addressable-if-time-permits points; the historical-event check (Table 4.6) remains explicitly n=4 and illustrative, correctly scoped in the text.

**Resolved across both passes**: word count (12,711 → 10,622 words, inside 9,000–11,000, close to the 10,000 target); the near-Clyde spatial audit and four-event historical comparison (Tables 4.5/4.6, Figure 4.15); a genuine LaTeX-math rendering bug that left visible text gaps in two places; two "see below" placeholder values in Table 3.1; missing mathematical foundations (now in §3.6–3.8); an 18-stage project roadmap figure (Figure 1.3); chapter page breaks; heading centre-alignment; and page-numbering format. Confirmed clean by direct search: no `§` artefacts, no AI/tool-name references, no local filesystem paths, no "Version C" mentions, zero dangling figure/table/section cross-references, all 43 image files resolve, and the List of Figures/Tables match the body exactly (43/43, 13/13).

**No specific percentage or grade is claimed or guaranteed by this audit.** The assessment above is a candid strengths/weaknesses inventory against the marking dimensions listed, intended to help prioritise any remaining time before the 17 August 2026 submission deadline — not a prediction of the mark the dissertation will receive. Fixing presentation bugs and adding mathematical notation are real improvements against the "structure/presentation" and "methodological rigour" dimensions specifically — they do not change the dissertation's standing on originality, literature currency, or sample-size limitations, which remain exactly as characterised in dimensions 3, 7, 10 and 12 above.
