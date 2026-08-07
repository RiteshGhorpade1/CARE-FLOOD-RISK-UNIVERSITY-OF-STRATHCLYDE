# Chapter 4: Results and Discussion

*[SKELETON — fill in after usability sessions are run and transcribed. Structure and cross-references are aligned with Chapter 3 (§3.7 Usability Evaluation Design) and Chapter 1 (§1.3 Research Questions) as drafted. Do not present any numbers here until they come from actual session data — placeholders are marked in square brackets.]*

## 4.1 Introduction

This chapter reports the results of the usability evaluation whose design was set out in Section 3.7, and discusses what those results mean for the three research questions established in Section 1.3. Section 4.2 presents the evaluation results themselves — participant and session overview, Nielsen heuristic severity scores, and thematic analysis findings. Section 4.3 discusses those results against RQ1 (already substantially answered by the model results in Section 3.4, revisited briefly here for completeness), RQ2 and RQ3, and against the Version A / Version B comparison the two dashboard variants were built to support. Section 4.4 summarises the chapter.

## 4.2 Usability Evaluation Results

### 4.2.1 Participant sample and session overview

*[Insert: final participant count and how it compares to the planned three-to-five convenience sample (§3.7); brief anonymised participant description — role/background, familiarity with flood risk or data tools, which dashboard version(s) each participant used if versions were split across participants or each participant saw both. Note any deviations from the planned procedure (e.g., session length, remote vs in-person, technical issues) and their effect on the data, per the transparency convention used throughout Chapter 3.]*

### 4.2.2 Nielsen heuristic severity scores (RQ3)

*[Insert: table of the ten Nielsen heuristics with severity ratings (0–4 scale, per §3.7) per participant/session, plus a summary column (mean, or count of issues per severity band). Call out the heuristics with the highest reported severity by name, and quote or paraphrase 1–2 representative think-aloud moments that illustrate each significant finding — consistent with how Chapter 3 pairs every quantitative claim with a concrete grounding. Compare Version A and Version B scores if the same heuristic set was scored for both.]*

### 4.2.3 Thematic analysis findings (RQ2)

*[Insert: the inductively generated themes/codes from Braun and Clarke's method (§3.7), focused specifically on participant commentary around the recommendation panel and, for Version B, the SHAP explanation panel. For each theme: a short definition, supporting quotes, and frequency/prevalence across participants. Explicitly address comprehensibility, applicability and personal relevance — the three qualities RQ2 asks about — rather than usability in general, to keep this section distinct from 4.2.2.]*

## 4.3 Discussion

### 4.3.1 RQ1 — Model accuracy and predictors

Briefly revisit the Section 3.4 findings (99.62% test accuracy, 99.21% ± 0.36% spatial-block accuracy, elevation and distance-to-Clyde as the dominant predictors) in light of the limitations already disclosed in Section 3.8 (label construction, spatial autocorrelation). *[Insert: any new perspective the usability sessions themselves indirectly offer on RQ1 — e.g., did participants trust or question the model's stated confidence, did any participant's local knowledge surface a case worth noting — otherwise keep this subsection short, since RQ1 is primarily a Chapter 3 result. Consistency check: describe the model as reconstructing the engineered proxy label, not as validated flood prediction — see the language established in §1.4/§2.6/§3.4.3/§3.9.]*

### 4.3.2 RQ2 — Recommendation comprehensibility, applicability and relevance

*[Insert: direct discussion answering RQ2 using the themes from 4.2.3 — did participants find the rule-based, source-cited guidance comprehensible and personally relevant, as the risk-communication literature in Section 2.5 predicted it should be (Spiegelhalter [10], Renn [11])? Note any disconfirming evidence as prominently as confirming evidence.]*

### 4.3.3 RQ3 — Dashboard usability

*[Insert: direct discussion answering RQ3 using the severity scores from 4.2.2, referenced against Nielsen's and Shneiderman et al.'s frameworks as introduced in Section 2.5. Identify which specific interface elements (colour convention, confidence indicator, error messages — as previewed in §2.5) performed well or poorly.]*

### 4.3.4 Version A vs Version B — does the explanation panel help?

*[Insert: the comparison the two-version design (§3.6.2) exists to support — did participants using Version B (with SHAP explanation) report higher trust, comprehension or satisfaction than those using Version A? This is the empirical payoff of building two versions rather than one, so give it explicit space even if the sample size (§3.7, §3.8) limits how strong a claim can be made.]*

## 4.4 Chapter Summary

*[Insert: 1 paragraph, written last, summarising the answer to each of RQ1–RQ3 in one or two sentences each, mirroring the summary style used in Section 3.9.]*

---

# Chapter 5: Conclusion

## 5.1 Summary of Contribution

*[Insert: restate the contribution from Section 1.4 in past tense — what was actually built and evaluated, not what was planned. Keep the same "systems and communication contribution, not ML novelty" framing already established, since Chapter 2's positioning (§2.6) and Chapter 4's results should now support it directly. Consistency check: use the corrected, non-overclaiming language established in §1.4, §2.6 and §3.9 — "an evaluated classifier reconstructing an engineered flood-risk proxy label", "evaluated using random and spatial-block cross-validation", "not independently validated against observed flood outcomes". Do not reintroduce "a validated classifier" / "a validated flood-risk classifier" / "validated by cross-validation" phrasing here.]*

## 5.2 Revisiting Research Objectives and Questions

*[Insert: short table or paragraph mapping each SMART objective (§1.3) and each RQ to where it was addressed and what was found — objectives to Chapter 3 sections, RQs to Chapter 4 findings. This is a signpost/scorecard, not new analysis.]*

## 5.3 Limitations Recap

*[Insert: 1 short paragraph pointing back to Section 3.8 rather than repeating it in full — add only what the completed usability evaluation itself revealed as a limitation (e.g., sample composition, session conditions) that Section 3.8 could not have anticipated since it was written before the sessions ran.]*

## 5.4 Future Work

*[Insert: concrete, scoped extensions the Limitations sections (3.8, 5.3) point toward — e.g., real-time data ingestion, multi-city generalisation, accessible/screen-reader-navigable SHAP charts (flagged already in §3.8), a larger statistically powered usability sample. Keep each suggestion tied to the specific limitation it addresses rather than a generic wish list.]*

## 5.5 Concluding Remarks

*[Insert: 1 short closing paragraph. No new claims — restate, briefly, that the project met its aim (§1.3) of building and evaluating an interactive, explainable, prescriptive flood-risk dashboard for a non-specialist audience.]*
