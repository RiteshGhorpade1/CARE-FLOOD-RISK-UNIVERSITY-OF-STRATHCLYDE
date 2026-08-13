# CARE Dissertation — Objective-to-Evidence Matrix

Traces every stated objective (§1.5) and research question (§1.6) through
method → evidence → result → interpretation → conclusion. Nothing here is
new evidence — every cell points to a specific section/table/figure already
in the dissertation; this file exists to make the audit trail explicit and
checkable in one place, per this session's request.

---

## Objectives (§1.5)

### Objective 1 — Train and evaluate a Random Forest flood-risk classifier, benchmarked against XGBoost

| Stage | Detail |
|---|---|
| **Method** | Random Forest (`n_estimators=100`, `random_state=42`), 80/20 stratified split (6,274 train / 1,569 test), macro F1 / AUC-ROC / confusion matrix, XGBoost on an identical split as benchmark (§3.6–3.7) |
| **Evidence** | Table 4.1 (per-class P/R/F1), Figure 4.1 (confusion matrix), Table 4.2 (RF vs XGBoost), Figure 4.5 (ROC curves) |
| **Result** | 99.62% accuracy, 99.50% macro F1; XGBoost 99.36%/99.17% (marginally lower); mean ROC-AUC 0.9998 |
| **Interpretation** | At this accuracy ceiling, the RF–XGBoost gap reflects both algorithms converging on the same near-perfect reconstruction of a deterministic label (§3.5), not evidence RF is intrinsically stronger (§4.5) |
| **Critical caveat** | `flood_risk` is constructed from elevation and PVA membership, and elevation is the model's dominant feature (62.9%, Table 4.3) — a genuine label-feature dependency. A large share of the 99.62% figure reflects rule-reconstruction, not independently validated real-world prediction (§4.14) |
| **Conclusion** | Objective 1 met technically and reported honestly against its own limitation — see RQ1 below |

### Objective 2 — Apply SHAP to identify top predictors and translate explanations into plain language

| Stage | Detail |
|---|---|
| **Method** | `TreeExplainer` on the trained RF, 500-point held-out sample, global summary + local waterfall (raw and probability-space configurations) (§3.8) |
| **Evidence** | Figure 4.6 (Gini importance), Figure 4.7 (SHAP global summary), Figure 4.8 (SHAP local waterfall), Figure 3.15 (live dashboard panel) |
| **Result** | Elevation (62.9%) and `dist_to_clyde` (17.2%) dominate both Gini and SHAP rankings; probability-space explanations decompose predictions into plain-language, per-feature contributions (e.g. "pushed High-risk probability up by twelve points") |
| **Interpretation** | SHAP explains what the trained model did with a point's inputs, not that any feature caused flooding there (§2.5, §3.15) — a distinction surfaced directly to dashboard users, not left implicit |
| **Conclusion** | Objective 2 met; the explanation is live and per-prediction (Version B), not an offline diagnostic — closing a gap Chapter 2 identifies in the wider XAI literature (§2.5, §2.8) |

### Objective 3 — Design and pilot a rule-based recommendation engine

| Stage | Detail |
|---|---|
| **Method** | Deterministic mapping from risk class to differentiated, source-cited guidance (SEPA, Ready Scotland, Scottish Flood Forum, Flood Re), placed immediately after the explanation panel in Version B (§3.16) |
| **Evidence** | Figure 3.16 (logic), Figure 3.17 (Version A panel), Table 3.2 (feature parity) |
| **Result** | All six participants (6/6) rated the recommendations relevant and useful (Q8, §5.7) |
| **Interpretation** | Recommendation usefulness held even where action intent varied (§5.7) — RQ2 anticipated this by asking about comprehensibility/relevance separately from stated behaviour |
| **Note on wording** | The objective's "pilot" phrasing describes a single evaluation round with six participants (§3.17), not a separate, larger-scale piloting phase preceding the main evaluation — a wording-precision point, not a research-integrity issue |
| **Conclusion** | Objective 3 met; evidenced directly by RQ2 (below) |

### Objective 4 — Develop a working dashboard integrating risk map, prediction, SHAP panel and recommendations, ready for usability evaluation

| Stage | Detail |
|---|---|
| **Method** | Two dashboard versions built for direct comparison: Version A (baseline) and Version B (Version A plus live SHAP panel and rainfall-context panels) (§3.9–3.17) |
| **Evidence** | Figure 3.8 (architecture), Figure 3.9/3.10 (Version A/B overview), Table 3.2 (feature comparison), Appendix A.9 (manual verification log, Table 4.4) |
| **Result** | Both versions runnable and verified against the live repository (Appendix A); ten components manually verified (Table 4.4) in the absence of an automated test suite (disclosed limitation, §3.19, §4.13) |
| **Interpretation** | The two-version structure is itself a deliberate experimental design choice — built specifically to isolate the SHAP layer's effect for RQ3, not an incidental by-product of iterative development |
| **Conclusion** | Objective 4 met for the technical build; its usability component is evidenced by RQ3 (below) |

---

## Research Questions (§1.6)

### RQ1 — How accurately can a classifier predict neighbourhood-level flood risk, and which factors are strongest predictors?

| Stage | Detail |
|---|---|
| **Method** | §4.1–§4.6 (classification performance, cross-validation, feature importance); §4.14 adds two independent checks: a 528-point near-Clyde spatial audit (Table 4.5) and a four-event historical-flood comparison (Table 4.6) |
| **Evidence** | 99.62% accuracy / 99.50% macro F1; 99.26% (±0.17%) random CV; 99.21% (±0.36%) spatial-block CV (Figure 4.3); elevation 62.9%, `dist_to_clyde` 17.2% (Table 4.3); Table 4.5 (0 mismatches at 50/100/150m); Table 4.6 (2/4 historical events agree with model prediction) |
| **Result** | Answered technically: near-ceiling, stable performance under both validation regimes, dominant predictors identified and stable across Gini and SHAP rankings |
| **Interpretation** | The result is reconstruction of an engineered proxy label, not independently validated real-world prediction (§4.14) — a caveat the near-Clyde audit and historical-event check *narrow* (both disagreements traced to specific, named causes: underground/tunnel-transmitted flooding, and a PVA-boundary gap) but explicitly do not remove, given n=4 is too small to generalise from |
| **Conclusion** | RQ1 answered with a scoped, evidence-backed caveat — not an unqualified accuracy claim |

### RQ2 — Does the recommendation engine produce comprehensible, applicable, personally relevant guidance?

| Stage | Detail |
|---|---|
| **Method** | Q7–Q8 of the Participant Questionnaire, six participants (§3.17, §5.7) |
| **Evidence** | Figure 5.3 (usefulness/action intent); Table 5.1 (dimension-by-dimension summary) |
| **Result** | 6/6 "Yes" on recommendation usefulness; action intent more varied (3 yes, 1 maybe, 1 qualified, 1 no) |
| **Interpretation** | Relevance and stated intent to act are not the same thing — the varied action-intent answers do not undercut the unanimous usefulness finding, since RQ2 asked about both separately (§5.7) |
| **Conclusion** | RQ2 answered positively, with the qualification that this is exploratory evidence from n=6, not a statistically generalisable claim (§5.1, §3.19) |

### RQ3 — How do non-specialist users perceive usability and accessibility, including Version B's explanation layer?

| Stage | Detail |
|---|---|
| **Method** | §5.8, §5.10–§5.11 (trust/explanation themes, SHAP feedback, accessibility); between-groups design, three participants per version (§3.17) |
| **Evidence** | Figure 5.4 (trust/explanation themes), Figure 5.5 (SHAP feedback, Version B only), Table 5.1 |
| **Result** | Both versions rated easy to navigate (6/6); all three Version B participants (3/3) reported SHAP increased trust and reduced "black-box" perception; two of the same three (2/3) also reported the SHAP chart's technical presentation as harder to follow than the rest of the interface |
| **Interpretation** | Explainability and comprehensibility are not the same thing, and both must be reported together (§5.10) — the same participants who found the explanation trust-building are the only ones reporting friction with it. This is treated as the dissertation's most non-obvious, nuanced finding, not smoothed into a simple success story |
| **Conclusion** | RQ3 answered positively with a scoped, named caveat: usability supported; explainability improves trust but is not automatically comprehensible without further design work (Table 6.1) |

---

## Cross-reference to Chapter 6

Table 6.1 (§6.3) presents this same Research Question → Evidence → Main Finding → Limitation → Conclusion structure in the dissertation body itself, in more compressed form. This file is the fuller working version behind that table, included as a standalone audit artefact per this session's request — it does not introduce any evidence not already present in Chapters 3–6.
