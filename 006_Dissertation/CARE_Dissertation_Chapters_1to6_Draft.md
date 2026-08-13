# Title Page

**CARE: An Interactive Machine Learning and Decision-Support Dashboard for Flood Risk Communication**

Ritesh Raju Ghorpade (202559288)

MSc Advanced Computer Science with Data Science

Department of Computer and Information Sciences, University of Strathclyde

Supervisor: Dr Daniel Thomas

Submitted: 17 August 2026

Dissertation Type: 3 (Application Based)

# Declaration

I confirm that this dissertation is my own work, that it has not been submitted for any other academic award, and that all sources have been acknowledged.

I declare that I have sought and received ethics approval via the Departmental Ethics Committee as appropriate to my research.

Word count (main body, excluding title page, declaration, abstract, acknowledgements, contents, list of illustrations, references and appendices): 10,368 words.

Dissertation Type: 3 — Application Based

Signed: Ritesh Raju Ghorpade
Date: 17 August 2026

# Abstract

Authoritative flood-risk data — SEPA flood-boundary shapefiles, Met Office HadUK-Grid rainfall, OpenStreetMap infrastructure, NASA elevation — is openly available, but rarely converted into something a non-specialist can act on: a boundary polygon does not answer whether a specific location is at risk or what to do about it. No integrated system was identified in the literature reviewed that combines a trained flood-risk classifier, live per-prediction explanation, and a structured recommendation layer inside one publicly accessible dashboard. This dissertation designs, builds and evaluates CARE (Climate Awareness and Risk Evaluation) to close that gap for a 5 km study area around the University of Strathclyde, Glasgow.

A Random Forest classifier, benchmarked against XGBoost, is trained on a 7,843-point, nine-feature grid over a three-class flood-risk label constructed from SEPA Potentially Vulnerable Area membership and elevation thresholds. The classifier achieves 99.62% test accuracy and 99.50% macro F1, stable under both random (99.26% ± 0.17%) and spatial-block (99.21% ± 0.36%) cross-validation; elevation (62.9%) and distance to the River Clyde (17.2%) dominate feature importance. Because the target label is itself constructed deterministically from elevation and PVA membership, this performance is interpreted throughout as reconstruction of an engineered, literature-grounded proxy label, not as independently validated real-world flood prediction — a distinction this dissertation treats as central rather than a closing caveat. A live, probability-space SHAP explainability layer attaches a per-prediction, plain-language explanation to each classification, and a deterministic, source-cited recommendation engine converts each risk class into differentiated guidance. Two dashboard versions were built for direct comparison: Version A (the shared core interface) and Version B (Version A plus the live SHAP explanation panel).

Six participants (three per version) evaluated the system via a structured questionnaire. All six found the recommendations relevant and useful. All three Version B participants associated the SHAP explanation with increased trust and reduced "black-box" perception; two of the same three also reported the explanation's technical presentation as the interface's one point of friction — evidence that explainability and comprehensibility are not the same thing, and that both must be reported together. Findings are exploratory and descriptive, drawn from a small convenience sample with two disclosed data-quality anomalies in the response data.

This dissertation's contribution is a systems and communication one rather than methodological novelty in the underlying machine learning: an integrated, evaluated artefact combining a benchmarked classifier, live per-prediction interpretability, and a rule-based recommendation layer, with genuine participant evidence that the explanation and recommendation layers were prominent trust drivers, while the underlying classification was generally experienced as part of the wider system rather than independently evaluated. Key limitations are disclosed throughout rather than as an afterthought: the engineered-label/circularity concern, a small non-random usability sample, absence of an automated test suite, and the need for future validation against independently observed flood outcomes rather than only the engineered proxy label used here.

# Acknowledgements

I would like to thank my supervisor, Dr Daniel Thomas, for guidance throughout this project, and the six participants who gave their time to evaluate the CARE dashboard.

# Table of Contents

```{=openxml}
<w:p>
  <w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>
  <w:r><w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText></w:r>
  <w:r><w:fldChar w:fldCharType="separate"/></w:r>
  <w:r><w:t>Right-click and select "Update Field" (or press F9) to generate the table of contents.</w:t></w:r>
  <w:r><w:fldChar w:fldCharType="end"/></w:r>
</w:p>
```

# List of Figures

**Chapter 1 — Introduction**

Figure 1.1 — CARE's five-layer system architecture.

Figure 1.2 — The research gap positioned at the intersection of three individually well-established components.

Figure 1.3 — CARE project roadmap: the eighteen stages actually carried out, from research problem to conclusions.

**Chapter 2 — Critical Literature Review**

Figure 2.1 — Literature review conceptual framework.

**Chapter 3 — Methodology, System Design and Implementation**

Figure 3.1 — SEPA Potentially Vulnerable Area zones within the 5 km Glasgow study circle.

Figure 3.2 — NASA SRTM elevation across the wider Glasgow area.

Figure 3.3 — Data integration workflow.

Figure 3.4 — Feature-engineering pipeline.

Figure 3.5 — Flood-risk label construction: engineered label vs. observed outcome.

Figure 3.6 — Feature-engineering summary.

Figure 3.7 — Machine learning pipeline.

Figure 3.8 — CARE dashboard internal architecture.

Figure 3.9 — CARE Version A, landing/overview screen.

Figure 3.10 — CARE Version B dashboard overview: postcode search, prediction summary and monthly rainfall exposure.

Figure 3.11 — CARE Version B location details panel and interactive risk map.

Figure 3.12 — CARE Version B monthly rainfall exposure panel.

Figure 3.13 — CARE Version B historical rainfall summary.

Figure 3.14 — CARE Version B seasonal rainfall overview.

Figure 3.15 — CARE Version B live SHAP explanation panel.

Figure 3.16 — Recommendation engine logic.

Figure 3.17 — CARE recommendation panel (Version A).

Figure 3.18 — CARE user journey, from postcode entry to a recommended next action.

**Chapter 4 — Results and Technical Evaluation**

Figure 4.1 — Random Forest confusion matrix.

Figure 4.2 — Random Forest per-class precision, recall and F1.

Figure 4.3 — Validation strategy comparison.

Figure 4.4 — Model accuracy and macro F1 comparison.

Figure 4.5 — One-vs-rest ROC curves per risk class.

Figure 4.6 — Random Forest feature importance.

Figure 4.7 — SHAP summary plots by risk class.

Figure 4.8 — SHAP waterfall explanation for a representative High-risk point.

Figure 4.9 — Predicted flood-risk class across the study grid.

Figure 4.10 — Spatial distribution of model prediction confidence.

Figure 4.11 — Elevation and distance-to-Clyde by risk class.

Figure 4.12 — HadUK-Grid rainfall, 1987–2025, by year.

Figure 4.13 — 39-year vs 3-year rainfall feature distributions.

Figure 4.14 — System verification coverage.

Figure 4.15 — Near-Clyde audit: recomputed risk class and PVA membership for all 528 points within 150m of the Clyde.

**Chapter 5 — User Evaluation and Discussion**

Figure 5.1 — Participant distribution by dashboard version.

Figure 5.2 — Risk levels evaluated, as recorded.

Figure 5.3 — Recommendation usefulness and action intent.

Figure 5.4 — Trust and explanation themes by version.

Figure 5.5 — SHAP explanation feedback, Version B only.

Figure 5.6 — User-suggested improvement themes.

# List of Tables

**Chapter 2 — Critical Literature Review**

Table 2.1 — Research gap matrix: literature themes, limitations and CARE design decisions.

**Chapter 3 — Methodology, System Design and Implementation**

Table 3.1 — Feature groups and definitions.

Table 3.2 — Version A vs Version B dashboard feature comparison.

Table 3.3 — Accessibility summary.

**Chapter 4 — Results and Technical Evaluation**

Table 4.1 — Random Forest test-set performance by class.

Table 4.2 — Random Forest vs XGBoost, and vs the original 3-year-rainfall model.

Table 4.3 — Random Forest feature importance (Gini-based).

Table 4.4 — System verification coverage.

Table 4.5 — Independent near-Clyde spatial audit: recomputed vs. stored `flood_risk` label.

Table 4.6 — Four historical flood events: agreement with model prediction.

**Chapter 5 — User Evaluation and Discussion**

Table 5.1 — Participant evaluation summary by dashboard version.

**Chapter 6 — Conclusions, Recommendations and Future Work**

Table 6.1 — Research-question evidence matrix.

Table 6.2 — Relative merits of key technologies and methodological choices.

# List of Abbreviations

| Abbreviation | Meaning |
|---|---|
| CARE | Climate Awareness and Risk Evaluation |
| CRS | Coordinate Reference System |
| CV | Cross-Validation |
| DSR | Design Science Research |
| DSS | Decision Support System |
| GIS | Geographic Information System |
| HCI | Human-Computer Interaction |
| ML | Machine Learning |
| PVA | Potentially Vulnerable Area (SEPA designation) |
| RF | Random Forest |
| ROC-AUC | Receiver Operating Characteristic — Area Under the Curve |
| RQ | Research Question |
| SEPA | Scottish Environment Protection Agency |
| SHAP | SHapley Additive exPlanations |
| SRTM | Shuttle Radar Topography Mission (NASA) |
| UAT | User Acceptance Testing |
| XAI | Explainable Artificial Intelligence |
| XGBoost | Extreme Gradient Boosting |

# Chapter 1: Introduction

## 1.1 Background and Motivation

Climate change has driven a marked increase in UK flooding, from fluvial, pluvial and coastal sources, often in combination (Rolnick et al., 2022). Glasgow is especially exposed: the River Clyde catchment sees frequent high-flow events, and continued urban densification has reduced natural drainage capacity. Four documented events (Table 4.6), from 1795 to 1994, confirm this is not a hypothetical risk.

The relevant environmental data is not scarce — SEPA publishes national flood-boundary shapefiles, the Met Office distributes decades of gridded rainfall through HadUK-Grid, and OpenStreetMap and NASA provide open infrastructure and elevation data. What is missing is the layer that turns this into something a resident can use: a boundary polygon does not answer *is my specific location at risk, and what should I do about it?* Technical risk mapping alone does not translate into individual action (Rizzoli and Young, 1997; Power and Sharda, 2009), the central problem examined next.

CARE (Climate Awareness and Risk Evaluation) closes this gap by training a machine learning flood-risk classifier for a defined Glasgow study area, explaining its predictions in plain language, and pairing each with source-cited guidance. Figure 1.1 sets out the five-layer architecture — data sources, data pipeline, ML model, recommendation engine, dashboard — that structures the rest of this dissertation.

![Figure 1.1 — CARE's five-layer system architecture: open data sources feed a spatial pipeline, a Random Forest model, a rule-based recommendation engine, and the interactive dashboard. Documented layer-by-layer in Chapters 3 and 4.](006_Dissertation/figures/figure_1_1_conceptual_framework.png){width=68%}

## 1.2 Problem Statement

The core problem is a translation gap, not a data gap. SEPA's PVA boundaries and HadUK-Grid rainfall are authoritative and freely accessible, but neither converts into an individually actionable answer for a non-specialist resident, community group, or local decision-maker; existing public tools remain descriptive, showing a boundary or statistic rather than a recommendation. This shifts the success criterion away from maximising raw predictive accuracy and toward whether the system is comprehensible and actionable to its audience — the standard Chapters 4 and 5 both report against.

## 1.3 Research Gap

A systematic literature review (Chapter 2) identified three specific gaps.

**Gap 1 — No integrated system.** No system was found — for Glasgow or, within the review's search terms, more generally — combining a trained flood-risk classifier, a structured recommendation layer, and an interactive public dashboard in one artefact, though each component is well established in isolation (Sections 2.2, 2.3, 2.6). Figure 1.2 makes this positioning concrete.

![Figure 1.2 — The research gap positioned at the intersection of three individually well-established components; no prior system was identified combining all three.](006_Dissertation/figures/figure_1_2_research_gap.png){width=52%}

**Gap 2 — Descriptive, not prescriptive, tools.** Publicly available tools remain overwhelmingly *descriptive*: SEPA's flood boundaries and HadUK-Grid rainfall show risk without converting it into a *prescriptive* recommendation (Rizzoli and Young, 1997; Biesbroek, Dupuis and Wellstead, 2017) — a design requirement here (Section 2.3), not an abstraction.

**Gap 3 — Explanation as a diagnostic tool, not a user-facing feature.** No reported work was found using SHAP-based attribution to connect individual flood-risk predictions to human-understandable, per-prediction explanations inside an interactive dashboard, rather than as an offline model-diagnostic exercise (Lundberg and Lee, 2017); this project surfaces explainability live, per prediction.

Together these gaps define this project's contribution: not a more accurate model in the abstract, but a genuinely integrated, explained, prescriptive system (Section 1.7) — a deliberately narrow claim, establishing only that no directly comparable system was identified, not that integration is necessarily where the greatest value lies; Chapter 5's evaluation tests that assumption directly.

## 1.4 Aim

To design, build and evaluate an interactive, machine-learning-driven flood-risk dashboard for Glasgow that predicts neighbourhood-level flood risk, explains each prediction, converts it into plain-language guidance, and is demonstrated usable by non-specialist users.

## 1.5 Objectives

1. Train a Random Forest flood-risk classifier and evaluate it on a held-out test set using macro F1, AUC-ROC and a confusion matrix, benchmarked against XGBoost (methodology Section 3.6–3.7, results Chapter 4).
2. Apply SHAP analysis to identify the top environmental predictors and translate per-prediction explanations into plain language (methodology Section 3.8, results Chapter 4).
3. Design and pilot a rule-based recommendation engine mapping each risk category to differentiated, source-cited guidance (Section 3.16).
4. Develop a working Streamlit dashboard integrating the risk map, live prediction, SHAP panel and recommendations, ready for usability evaluation (Sections 3.9–3.17).

All four objectives were addressed; outcomes are reported in Chapters 3–4, and, for Objective 4's usability component, in Chapter 5.

## 1.6 Research Questions

Three research questions, each mapping onto one objective above (RQ1↔Objectives 1–2, RQ2↔Objective 3, RQ3↔Objective 4), structure the evaluation in Chapters 3–5:

- **RQ1.** How accurately can a machine learning classifier predict neighbourhood-level flood risk in Glasgow, and which environmental factors are the strongest predictors?
- **RQ2.** Does the rule-based recommendation engine produce guidance that a non-specialist audience rates as comprehensible, applicable and personally relevant?
- **RQ3.** How do non-specialist users perceive the usability and accessibility of the CARE dashboard, including the additional explanation functionality provided by Version B?

RQ3 is scoped to what this project's evaluation instrument can support: an earlier formulation referenced assessment "against a recognised ten-heuristic evaluation framework," implying a formal Nielsen walkthrough, but the evaluation actually conducted (Section 3.17, Chapter 5) is a structured questionnaire analysed thematically — RQ3 is stated here to match the evidence this dissertation can produce.

## 1.7 Research Contribution

Four elements, each responding to a gap in Section 1.3:

1. **Integration.** A single artefact combining an evaluated classifier reconstructing an engineered flood-risk proxy label, SHAP interpretability, and a rule-based recommendation layer — no directly comparable precedent found (Gap 1).
2. **Prescriptive design.** The dashboard leaves a user not only informed of risk but aware of *why* and *what to do next* (Gap 2).
3. **User-facing explainability.** SHAP applied live, per prediction, to the end user rather than retained offline (Gap 3).
4. **Deliberately bounded scope.** Batch data, single case-study city — attainable and rigorously evaluable within an MSc timeframe.

This is a systems and communication contribution, not methodological novelty: Random Forest, gradient-boosted trees and SHAP are established techniques (Chapter 2); the contribution lies in combining them with local data and evaluating for usability with an audience the literature addresses comparatively thinly.

## 1.8 Scope and Boundaries

The system is bounded to a 5 km radius around the University of Strathclyde, Glasgow, using batch (not real-time) environmental data current at collection time (Section 3.2–3.3). It classifies risk into three categories using an engineered proxy label (Section 3.5), not observed historical flood events; predictions are framed as research classifications, not official flood-risk assessments (Section 3.10–3.11). Usability evidence is drawn from a six-participant convenience sample (Chapter 5), not a statistically powered study. These boundaries keep the project attainable within a single MSc timeframe, and are revisited as limitations in Sections 3.19 and 6.7.

## 1.9 Dissertation Structure

Chapter 2 reviews the literature and synthesises it against the three gaps above. Chapter 3 documents the system built in response, screen by screen, plus usability design, ethics and limitations. Chapter 4 reports the quantitative results (RQ1); Chapter 5 reports the usability evaluation's findings (RQ2–RQ3). Chapter 6 answers all three research questions and sets out conclusions and future work. Figure 1.3 traces this same sequence as the actual project workflow, from research problem through to conclusions.

![Figure 1.3 — CARE project roadmap: the eighteen stages actually carried out, from research problem to conclusions, matching the chapter structure above.](006_Dissertation/figures/figure_1_3_project_roadmap.png){width=85%}

# Chapter 2: Critical Literature Review

## 2.1 Review Scope and Method

A systematic search was conducted across IEEE Xplore, Google Scholar and Web of Science using combinations of *flood risk prediction machine learning*, *geospatial decision support*, *climate risk communication*, *random forest hydrology*, *explainable AI*, and *public understanding environmental data*. Sources were retained where they addressed a method applicable to hazard classification, environmental decision-support design/evaluation, spatial data integration, explanation/recommendation delivery, or risk communication to non-experts; sources addressing flooding only from a physical-science or policy perspective, without a methodological contribution, were excluded as outside this project's scope as a software artefact rather than a hydrological study. The literature is synthesised around six themes (Figure 2.1), each connected at the end of its section to the specific CARE design decision it informed, so the link to Chapter 3 is traceable rather than implicit.

![Figure 2.1 — Literature review conceptual framework: the reviewed themes, each converging on a specific CARE design decision.](006_Dissertation/figures/figure_2_1_literature_framework.png){width=55%}

## 2.2 Machine Learning for Flood-Risk Prediction

Ensemble tree-based classifiers, particularly Random Forests, repeatedly outperform single classifiers on flood-susceptibility mapping: Tehrany, Pradhan and Jebur (2014) show ensembles recall minority flood-event classes far more effectively than logistic regression or SVM baselines, which Breiman's (2001) formulation explains — bootstrap-aggregated decorrelated trees reduce variance without added bias and need little preprocessing for mixed-scale inputs. Chen and Guestrin's (2016) XGBoost is a strong gradient-boosted benchmark; Abedi et al. (2021), comparing CART, Random Forest, boosted trees and XGBoost on flood-susceptibility mapping specifically, similarly find ensembles strongest, though the best variant varies by study area. Deep architectures were not benchmarked: nine structured features with no spatial-grid structure and only 7,843 rows once split favour ensemble trees. Class imbalance is endemic — Tehrany et al. (2014) show plain accuracy is unreliable here, recommending macro-F1 and AUC-ROC instead. Transferability is a further limitation: these algorithms are benchmarked on different catchments than Glasgow's Clyde-dominated setting, so the literature justifies Random Forest as an *algorithmic* starting point, not an expectation that this project's accuracy (Chapter 4) will replicate theirs. **Gap**: this literature addresses model performance in isolation; little considers how output should reach a non-specialist decision-maker (Sections 2.5–2.7).

## 2.3 Environmental Decision-Support Systems

The DSS literature distinguishes systems that *describe* from systems that *prescribe*: Rizzoli and Young (1997) identify this shift as the field's central unresolved challenge; Power and Sharda (2009) situate it as a recurring gap in DSS design generally. Design Science Research (DSR, Hevner et al., 2004) supplies this project's methodology: an artefact is evaluated not only on technical correctness but on demonstrated usefulness with representative users, separating a *rigor cycle* (Section 2.2) from a *relevance cycle* (Section 3.17) — a cycle the literature repeatedly under-executes, the imbalance Chapter 5 is intended to correct. Biesbroek, Dupuis and Wellstead (2017) similarly find well-resourced adaptation programmes fail to convert technical outputs into behavioural change without a communication layer — the gap this project's recommendation engine addresses.

## 2.4 Geospatial Analysis for Urban Flood Risk

Urban flood-risk analysis requires integrating spatial data at markedly different scales — the challenge this project's pipeline confronts across vector boundaries, vector infrastructure, and two gridded rasters. Tomaszewski (2015) sets out both the technical requirement (consistent CRS, resolved topology) and the cognitive requirement (interpretability to a non-specialist), motivating this project's explicit CRS verification and single regular 100 m grid. Vector sources (SEPA, OSM) support exact containment/distance operations; raster sources (NASA elevation, HadUK-Grid) support only nearest-cell lookup, capping spatial variation regardless of grid fineness — met directly in the rainfall features (Section 3.4) and disclosed as a limitation (Section 3.19). Singleton and Spielman (2014) find interactive web maps improve public understanding over static equivalents, supporting this project's interactive Folium map.

## 2.5 Explainable Artificial Intelligence

Model interpretability is not a diagnostic convenience but a driver of trust where output informs public decisions (Adadi and Berrada, 2018). Lundberg and Lee's (2017) SHAP framework, grounded in Shapley values, is the standard for explaining individual tree-model predictions; Lundberg et al. (2020) extend this to tree ensembles at scale, distinguishing raw-margin from calibrated-probability output — engaged directly in Section 3.8, including a library limitation for XGBoost's multiclass objective (Section 4.5). SHAP is not the only post-hoc technique: Ribeiro, Singh and Guestrin's (2016) LIME fits a local surrogate faster in principle but without SHAP's consistency guarantees; permutation importance (Fisher, Rudin and Dominici, 2019) is simpler but *global*, so cannot answer "why did *my* location get this result?"; Random Forest's native Gini importance (Section 4.6) needs no extra library but is global and biased toward correlated features (Barredo Arrieta et al., 2020). Only SHAP offers per-prediction, model-agnostic, probability-space attribution — what the live dashboard requires. Its weakness: it explains *model behaviour*, not causal reality — a bar showing "elevation pushed risk up" describes what the model did, not that low elevation causes flooding (Barredo Arrieta et al., 2020), load-bearing throughout (Sections 3.8, 4.7–4.8). The XAI literature is largely authored within ML venues concerned with developer-side auditing; almost none address presenting SHAP to a non-specialist — a question this project's evaluation speaks to directly (Section 2.8, Chapter 5).

## 2.6 Recommendation Systems and Actionable Risk Communication

Ricci, Rokach and Shapira (2015) distinguish rule-based recommendation from content-based/collaborative approaches that *learn* from historical data. Zhang and Chen's (2020) survey finds pairing a recommendation with a reason for it measurably improves trust and perceived usefulness, supporting placing explanation immediately before recommendation (Section 3.16). A rule-based approach is appropriate here: the correct response to a risk level is civil-protection guidance, not inferred preference, and no interaction log exists to learn from regardless. **Gap**: rule-based recommendation is well understood but rarely paired with a live ML classifier's output inside one integrated, evaluated tool (Section 3.16, Chapter 5).

## 2.7 Risk Communication, Trust and Human-Centred Design

Spiegelhalter (2017) finds non-experts systematically misread probabilistic output as implicit certainty unless carefully presented — justifying this project's categorical label over a bare probability. Renn (2008) adds that risk communication is most effective when connected to personally relevant situations and delivered by a trusted source — reflected in differentiating guidance by risk class and citing every recommendation to SEPA/Ready Scotland. Nielsen's (1994) usability heuristics and Braun and Clarke's (2006, 2019, 2021) thematic analysis are both established evaluation approaches: this project draws on Braun and Clarke's inductive coding (Section 3.17, Chapter 5), treating Nielsen's heuristics as an interpretive lens rather than a formally administered instrument, since the evaluation was a questionnaire, not a moderated walkthrough (Section 1.6). Shneiderman et al.'s (2017) HCI strategies inform concrete choices (fixed colour convention, always-visible confidence, specific error messages); accessibility is addressed against WCAG (W3C, 2018) in Section 3.19/Table 3.3.

## 2.8 Critical Synthesis and Research Gap

This literature establishes three things: imbalance-aware ensemble classifiers with SHAP interpretability are literature-supported here, though the XAI literature rarely addresses presentation to non-specialists; the descriptive/prescriptive gap is a long-standing DSS problem only a genuinely integrated system closes; and risk-communication/recommender-systems literature together specify how that prescriptive layer should be built — rule-based, categorical, evaluated for comprehensibility, which Section 2.3 shows is frequently under-executed relative to construction.

No work identified integrates all three — an evaluated classifier reconstructing an engineered proxy label, per-prediction SHAP interpretability, and a rule-based, source-cited recommendation layer — inside one publicly accessible, evaluated dashboard, the gap Chapter 3 documents CARE addressing. A plausible reason is disciplinary separation: interpretability literature (Section 2.5) sits largely within ML venues concerned with model auditing, while risk-communication literature (Section 2.7) sits largely within psychology and governance, concerned with how lay audiences process uncertainty — the two rarely cite each other. This project's own evaluation (Chapter 5) speaks directly to that gap: SHAP-enhanced-version participants consistently linked it to increased trust, but two of the same three also named its technical presentation as the interface's one point of friction — precisely the intersection the two literatures, read separately, would not have anticipated.

Table 2.1 makes this gap concrete: each theme reviewed above, its limitation in existing work, the CARE design decision built in response, and where it is documented.

**Table 2.1 — Research gap matrix**

| Literature theme | Limitation in existing work | CARE design decision | Documented in |
|---|---|---|---|
| ML for flood-risk prediction (Tehrany, Pradhan and Jebur, 2014; Breiman, 2001; Chen and Guestrin, 2016) | Evaluated as standalone models, not embedded in a public-facing decision tool | Random Forest primary model, benchmarked against XGBoost; macro F1/per-class metrics | §3.6, §3.7 |
| Environmental DSS theory (Rizzoli and Young, 1997; Power and Sharda, 2009; Biesbroek, Dupuis and Wellstead, 2017) | Remains descriptive, not prescriptive | Prescriptive dashboard output; DSR methodology | §3.16, §3.17 |
| Geospatial data integration (Tomaszewski, 2015) | Vector/raster scale mismatch rarely made explicit | Explicit CRS verification; single regular modelling grid | §3.2–§3.4 |
| Interactive cartography (Singleton and Spielman, 2014) | Static equivalents impair public understanding | Interactive Folium map, not a static risk image | §3.13 |
| Explainable AI (Lundberg and Lee, 2017; Lundberg et al., 2020; Ribeiro, Singh and Guestrin, 2016) | Applied almost exclusively offline, by model developers, not shown to end users | Live, probability-space SHAP explanation per prediction | §3.8, §3.15 |
| Recommender systems (Ricci, Rokach and Shapira, 2015; Zhang and Chen, 2020) | Rarely paired with a live ML classifier's output inside one integrated tool | Rule-based, not learned, recommendation engine | §3.16 |
| Risk communication psychology (Spiegelhalter, 2017; Renn, 2008) | Bare probabilities easily misread as certainty | Categorical risk labels; differentiated, source-cited guidance | §3.15, §3.16 |
| Usability evaluation (Shneiderman et al., 2017; Braun and Clarke, 2006, 2019, 2021; Nielsen, 1994) | Representative non-specialist users rarely involved in evaluation | Structured questionnaire, thematic analysis (not a formal Nielsen severity walkthrough) | §3.17 |

# Chapter 3: Methodology, System Design and Implementation

## 3.1 Research Design

This project follows Design Science Research (Hevner et al., 2004; Section 2.3): the CARE dashboard is built in response to the Chapter 2 gap, then evaluated both technically (Chapter 4, RQ1) and with representative non-specialist users (Chapter 5, RQ2–RQ3). This chapter documents construction around the five-layer architecture from Figure 1.1 (§3.2–3.16), then evaluation design, ethics and limitations (§3.17–3.19); resulting numbers are reported separately, in Chapter 4. Unless stated otherwise, conceptual/architecture diagrams and screenshots are the author's own work; figures derived from external datasets (SEPA, NASA SRTM, HadUK-Grid) are the author's own processing of that data, credited in the caption.

## 3.2 Study Area

The system is scoped to a 5 km radius circle centred on the University of Strathclyde (easting 260,983, northing 665,006, EPSG:27700) — data-rich, relevant to the intended user base, and genuinely flood-exposed via the River Clyde. All spatial processing uses EPSG:27700 (British National Grid, metres); conversion to WGS84 is deferred to map rendering only, avoiding the distortion an unprojected CRS would introduce into every buffer/distance calculation (Figure 3.1).

![Figure 3.1 — SEPA Potentially Vulnerable Area zones within the 5 km Glasgow study circle (red dashed boundary), coloured by zone, with the University of Strathclyde as study centre. Source: SEPA PVA data, author's map.](002_Dataset/outputs/eda_sepa_pva.png){width=75%}

## 3.3 Data Sources

Four open datasets, each at a different native scale and format, are combined.

**SEPA's Potentially Vulnerable Areas (PVA)** (SEPA, 2023) identifies 235 flood-vulnerable zones nationally (GeoPackage, EPSG:27700, mean zone area 59.4 km², zero missing values); intersecting the 5 km study buffer isolates seven Glasgow zones (4.3–209.2 km²), the spatial basis of the flood-risk label (Section 3.5).

**OpenStreetMap** (OpenStreetMap contributors, 2026) contributes buildings (55,638), roads (38,218, 37 highway types), and water (195 polygons, including three "River Clyde" polygons merged into a 217.7-hectare geometry underlying `dist_to_clyde`).

**NASA SRTM elevation** (NASA JPL, 2013) provides 259,200 point measurements (−23 m to 132 m, mean 41.6 m; 282 points below sea level, reflecting the reclaimed lower Clyde valley). The 15 m/35 m risk-labelling thresholds (Section 3.5) each bisect the distribution with a meaningful population on both sides (17.4% ≤15 m, 50.2% ≤35 m; Figure 3.2).

![Figure 3.2 — NASA SRTM elevation across the wider Glasgow area: distribution (left, 15 m/35 m thresholds marked) and spatial map (right). Source: NASA SRTM data, author's map.](002_Dataset/outputs/eda_elevation.png){width=80%}

**Met Office HadUK-Grid daily rainfall** (Hollis et al., 2019) combines two archives (431 files 1987–2022, 36 files 2023–2025) into one 39-year series — 111,480,402 observations once extracted to the study grid (182.6 MB Parquet).

Distance to the Clyde is a substantially stronger flood-risk correlate than distance to any water body (r = −0.74 vs. −0.28), motivating `dist_to_clyde` as distinct from `dist_to_water` — later confirmed as the second most important predictor (Section 4.6); the two are not redundant (18.2% share an identical value, correlating only weakly overall, r = 0.25). CRS discrepancy was a flagged risk, mitigated by verifying each source's CRS before every join.

## 3.4 Data Integration and Feature Engineering

Nine features, in four categories, are engineered onto a regular 100 m grid across the 5 km radius (7,843 points, the fixed unit of analysis throughout), combining the four sources above via a harmonised-CRS, spatially-joined pipeline (Figure 3.3; feature groups in Table 3.1, pipeline in Figure 3.4).

![Figure 3.3 — Data integration workflow: four sources in four native formats, harmonised to a common coordinate system and combined via spatial joins onto the single 100m study grid.](006_Dissertation/figures/figure_3_data_integration_workflow.png){width=55%}

![Figure 3.4 — Feature-engineering pipeline: nine features grouped into terrain, hydrology, built-environment and rainfall/climate categories, attached to the 7,843-point study grid.](006_Dissertation/figures/figure_3_feature_pipeline.png){width=75%}

**Table 3.1 — Feature groups and definitions**

| Group | Feature | Description | Range |
|---|---|---|---|
| Terrain | `elevation` | NASA SRTM elevation, nearest-neighbour join | −15 to 127 m |
| Hydrology | `dist_to_water` | Distance to nearest OSM water polygon | 0–2,258.8 m |
| Hydrology | `dist_to_clyde` | Distance to the River Clyde specifically | 0–6,161.5 m |
| Built environment | `building_count` | OSM buildings within 250 m | 0–419 |
| Built environment | `road_count` | OSM roads within 250 m | 0–680 |
| Rainfall / climate | `mean_annual_mm_day` | 39-year mean daily rainfall | 2.71–3.08 mm/day |
| Rainfall / climate | `mean_winter_mm_day` | 39-year mean daily rainfall, Dec–Feb | 3.33–3.73 mm/day |
| Rainfall / climate | `wet_days_per_year` | Days ≥1.0mm/year, 39-year average | 165–176 |
| Rainfall / climate | `max_daily_mm` | Average annual peak daily rainfall | 31.72–33.32 mm |

Elevation uses a nearest-neighbour join (zero missing values); the two distance features are Euclidean distances to merged OSM geometries; `building_count`/`road_count` within 250 m use a spatial-index shortlist then exact containment test, capturing that dense impermeable surfaces drain more poorly independent of elevation or river proximity; the four rainfall features are aggregated from the 111.5M-row daily table (peak daily rainfall uses the mean of each year's single wettest day, so one storm year doesn't dominate). Rainfall's narrow spatial range (Table 3.1) reflects HadUK-Grid's native 5 km resolution, where nearby points often share a raster cell (Section 3.19); the year-by-year trend is reported separately (Section 4.12).

## 3.5 Flood-Risk Label Construction

The target variable, `flood_risk`, combines SEPA PVA membership with elevation:

```
flood_risk = 2 (High)    if inside a PVA zone AND elevation ≤ 15m
flood_risk = 1 (Medium)  if inside a PVA zone AND elevation ≤ 35m
flood_risk = 0 (Low)     otherwise
```

This encodes a defensible hydrological intuition, not an arbitrary threshold: PVA membership identifies *where* flooding is plausible, elevation refines *how severe*. Figure 3.5 deliberately labels the result an **engineered label**, not an observed outcome: the classifier (Section 3.6, Chapter 4) learns to reconstruct this rule from continuous inputs, not from independently observed historical flooding. This is central throughout: since elevation is both a label input and a feature the model sees directly, a share of the headline accuracy (Chapter 4) necessarily reflects rule-recovery, not independent predictive discovery (Section 3.19, 4.14) — the caveat Section 4.14's near-Clyde and historical-event checks probe directly.

![Figure 3.5 — Flood-risk label construction: the exact rule combining PVA membership and elevation thresholds, with an explicit statement that the result is an engineered label, not an observed outcome.](006_Dissertation/figures/figure_3_risk_label_construction.png){width=60%}

Applied across the grid: 3,790 Low (48.3%), 2,698 Medium (34.4%), 1,355 High (17.3%) — a moderate imbalance motivating macro-averaged metrics (Section 3.7). Figure 3.6 summarises the resulting feature matrix (zero missing values throughout).

![Figure 3.6 — Feature-engineering summary: risk-class distribution, elevation/Clyde-distance by class, feature correlation, the resulting risk map, and rainfall variation across the grid. Source: SEPA, NASA SRTM, OSM and HadUK-Grid data, integrated and mapped by the author.](002_Dataset/outputs/feature_engineering_summary.png){width=85%}

## 3.6 Machine Learning Methodology

A Random Forest classifier (`n_estimators=100`, `random_state=42`) was trained as primary model, consistent with Section 2.2, with XGBoost as benchmark rather than candidate replacement (Table 6.2). Its ensemble principle:

```
f(x) = majority_vote{ T_1(x), T_2(x), ..., T_B(x) }
```

where each `T_b` is one of `B`=100 decision trees trained on a bootstrap sample, and the forest's output is the modal class across all trees — the variance-reduction mechanism behind Breiman's (2001) result (Section 2.2). The nine-feature matrix was split 80/20 (stratified, `random_state=42`) into 6,274 training and 1,569 test points. Figure 3.7 summarises this pipeline end to end.

![Figure 3.7 — Machine learning pipeline: feature matrix, stratified split, Random Forest training (benchmarked against XGBoost), four evaluation strategies, and the metrics reported in Chapter 4.](006_Dissertation/figures/figure_3_ml_pipeline.png){width=50%}

## 3.7 Model Evaluation Methodology

Evaluation uses standard classification metrics, computed per class (TP/TN/FP/FN = true/false positive/negative counts) and macro-averaged across the three risk classes:

```
Accuracy  = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 × (Precision × Recall) / (Precision + Recall)
Macro-F1  = (1/K) × Σ F1_k,  K = 3 classes
```

Macro F1, not accuracy, is the headline metric: it weights each class equally regardless of size, appropriate given the 48/34/17% class split (Section 3.5), per Tehrany et al.'s recommendation (Section 2.2). One-vs-rest ROC-AUC complements these fixed-threshold metrics with a threshold-independent view: for each class treated as positive-vs-rest, it summarises separability across every possible confidence cut-point, not just the classifier's default one, as the area under the resulting true-positive-vs-false-positive-rate curve. A confusion matrix reports the raw per-class error pattern underlying all of the above. Two cross-validation strategies check this is not a single-split artefact: five-fold stratified CV, and a `GroupKFold` scheme withholding complete 500 m spatial tiles, testing whether spatial autocorrelation between neighbouring 100 m points (Section 3.19) inflates the score. XGBoost is trained on an identical split, and the pipeline is re-run against a frozen 3-year (2023–2025) rainfall snapshot to isolate the 39-year climatology's effect. Because the label is constructed deterministically from elevation and PVA membership (Section 3.5), every Chapter 4 result is interpreted against this caveat.

## 3.8 SHAP Explainability Methodology

Interpretability is a design requirement, not an optional diagnostic (Section 1.4): an accurate score alone does not close the communication gap unless a user can see *why*. SHAP's additive formulation:

```
f(x) = φ₀ + Σ φᵢ
```

decomposes a prediction `f(x)` into a baseline `φ₀` (the model's average output) plus each feature `i`'s signed contribution `φᵢ` for that specific point — the exact decomposition the dashboard's waterfall/bar charts render (Section 3.15). A `TreeExplainer` is fitted to the trained Random Forest, with SHAP values computed for a fixed 500-point held-out sample, reused across every SHAP output for comparability (Section 4.7).

Local waterfall explanations are generated for representative points per class — the sample point with the model's highest predicted probability for that class — in two configurations: raw additive output, and probability-space (`model_output="probability"`, training partition as background). The probability-space version is carried into the live dashboard, decomposing a predicted class *probability* directly interpretable by a non-specialist (e.g. "pushed High-risk probability up by twelve points"), responding directly to Spiegelhalter's finding (Section 2.7) that raw probabilities are easily misread as certainty. This runs live — around 2 ms to build the explainer, 5–10 ms per point — so every click triggers a fresh computation. SHAP explains what the trained model did with a given point's inputs, not that any feature caused flooding there (Section 2.5), surfaced directly to users (Section 3.15).

## 3.9 CARE Dashboard Architecture

The dashboard is built in Streamlit, with `folium`/`streamlit_folium` for the interactive map, `pyproj` for EPSG:27700↔WGS84 conversion, and the free `postcodes.io` API (Ideal Postcodes, n.d.) for postcode search. Model and feature matrix load once at startup; predictions and confidence are computed for all 7,843 points and cached (`st.cache_data`, `st.cache_resource`); selection and filter state persist in `session_state`. Figure 3.8 sets this out as five layers, mirroring Figure 1.1, separating cleanly into two tiers: a **model layer** (pipeline, Random Forest, SHAP — identical for both versions) and a **communication/visualisation layer** (frontend, recommendation phrasing) — the only layer that differs between Version A and B.

![Figure 3.8 — CARE dashboard internal architecture: data/API, model, SHAP, recommendation and frontend layers, and the caching mechanism each relies on.](006_Dissertation/figures/figure_3_dashboard_architecture.png){width=55%}

Two versions are maintained side by side rather than one replacing the other, so any behavioural difference between them is presentation, not a different classifier or inputs. Neither the dashboard format nor postcode search is a neutral choice against static reporting or map-only exploration — both trade-offs are discussed in Table 6.2.

## 3.10 Dashboard Version A — Baseline Interface

Version A (Figure 3.9) is the deliberately minimal baseline: postcode search, a district/landmark browse control, the risk badge/confidence/nearest-zone/compass/context cards, the recommendation engine (Section 3.16), and a research-classification disclaimer, in a light theme with a sidebar rainfall-trend and citywide risk-mix summary.

![Figure 3.9 — CARE Version A, landing/overview screen: postcode search, orientation panel, and the baseline interface elements.](006_Dissertation/figures/screenshots/versionA_landing.jpg){width=88%}

## 3.11 Dashboard Version B — Advanced Explainable Interface

Version B (Figure 3.10) is a fixed nine-section, two-column, dark-themed layout on the same prediction pipeline as Version A, adding a live per-prediction SHAP explanation ("Why this result?", Section 3.15) and three historical-rainfall panels (Section 3.14). Table 3.2 compares both directly.

![Figure 3.10 — CARE Version B, dashboard overview: postcode search and prediction summary (left) and the monthly rainfall exposure panel (right).](006_Dissertation/figures/screenshots/versionB_landing_current.jpg){width=90%}

**Table 3.2 — Version A vs Version B dashboard feature comparison**

| Feature | Version A | Version B |
|---|:---:|:---:|
| Postcode search, risk badge, confidence, recommendation engine | ✓ | ✓ |
| Interactive risk map, seven-dimension filtering, historical event markers | ✓ | ✓ |
| Compass indicator, district/landmark browse control | ✓ | — |
| Sidebar rainfall-trend and citywide risk-mix summary | ✓ | — |
| Monthly rainfall exposure, historical rainfall summary, seasonal rainfall overview (Section 3.14) | — | ✓ |
| Live SHAP "Why this result?" explanation panel (Section 3.15) | — | ✓ |
| Visual theme | Light | Dark |

Both versions filter the map across the same seven dimensions and mark the same four documented historical flood events (Table 4.6), styled distinctly from model output as passive context, applying Shneiderman et al.'s (Section 2.7) HCI strategies: a fixed colour convention (`#639922`/`#EF9F27`/`#E24B4A`), always-visible confidence, graceful error handling. Version B's rainfall panels postdate the Chapter 5 evaluation sample (Section 3.17).

## 3.12 Prediction Summary and Location Details

The prediction summary communicates a categorical result without implying false certainty (Section 2.7): confidence is labelled classification confidence, not a calibrated probability, and the interpretation card names the top driving feature(s) in hedged, non-causal language (Section 3.15). Location Details (Figure 3.11, left) lists postcode, coordinates, elevation, distance to the Clyde, nearest grid point, local authority and data sources, with a standing disclaimer that results are the nearest 100 m grid point, not a property-level assessment.

![Figure 3.11 — CARE Version B: location details panel and the interactive risk map with its filter controls.](006_Dissertation/figures/screenshots/versionB_locationmap_crop.jpg){width=44%}

## 3.13 Interactive Risk Map

The interactive risk map (Figure 3.11, right) is the dashboard's principal chart in both versions: every study-grid point coloured by predicted risk class, filterable across seven dimensions, click-to-inspect — consistent with interactive cartography improving public understanding over a static image (Section 2.4).

## 3.14 Historical and Seasonal Rainfall Context

Version B adds three panels built from an additive offline aggregation of the same 39-year HadUK-Grid archive used for the model's rainfall features (Section 3.4) — no new data, no model change: Monthly Rainfall Exposure (Figure 3.12), Historical Rainfall Summary (Figure 3.13), and Seasonal Rainfall Overview (Figure 3.14). Terminology is deliberately restricted to *historical rainfall exposure*: the classifier has no temporal dimension (its rainfall features are themselves 39-year averages), so no panel is worded as a forecast or probability.

![Figure 3.12 — CARE Version B monthly rainfall exposure panel: highest/lowest-exposure months, current season, and the twelve-month relative exposure chart and table.](006_Dissertation/figures/screenshots/versionB_monthlyrainfall_crop.jpg){width=44%}

![Figure 3.13 — CARE Version B historical rainfall summary: the 39-year area-averaged annual series with wettest/driest year and mean annual total.](006_Dissertation/figures/screenshots/versionB_historicalannual_crop.jpg){width=44%}

![Figure 3.14 — CARE Version B seasonal rainfall overview: four meteorological seasons each tagged with a relative exposure category.](006_Dissertation/figures/screenshots/versionB_seasonal_crop.jpg){width=88%}

## 3.15 SHAP Explanation Interface

Version B's "Why this result?" panel (Figure 3.15) names the top one or two driving features in hedged language, states an explicit non-causal caveat above the chart — "These bars show what influenced this model classification. They do not prove what caused flooding." — and ranks all nine features by SHAP contribution (red = pushes risk up, blue = pushes risk down) with plain-English tiered labels (e.g. "Low elevation" rather than a bare metre value).

![Figure 3.15 — CARE Version B live SHAP explanation panel: diverging bar chart of all nine features' contribution to the predicted class, non-causal caveat, and feature definitions.](006_Dissertation/figures/screenshots/versionB_shap_crop.jpg){width=88%}

## 3.16 Recommendation Engine

The recommendation engine — the fourth architecture layer (Figure 1.1), Objective 3 (Section 1.7) — is a deterministic, source-cited mapping (Figure 3.16) from risk class to differentiated guidance, cited to SEPA and Ready Scotland rather than presented as CARE's own advice: High centres on SEPA's official maps (SEPA, 2023), Floodline registration, Scottish Flood Forum measures and Flood Re; Medium is precautionary; Low differs in *kind*, framing map-checking around planning rather than immediate risk (Figure 3.17). Explanation precedes recommendation in Version B to build perceived legitimacy — the basis on which RQ2 is assessed (Chapter 5).

![Figure 3.16 — Recommendation engine logic: the deterministic mapping from predicted risk class to differentiated, source-cited guidance.](006_Dissertation/figures/figure_3_recommendation_logic.png){width=58%}

![Figure 3.17 — CARE recommendation panel (Version A), showing risk-specific, source-cited "Precautions and next steps" guidance for a Medium-risk result.](006_Dissertation/figures/screenshots/versionA_recommendations_full.png){width=75%}

Figure 3.18 traces the intended user journey in the order participants encountered each screen during evaluation (Section 3.17).

![Figure 3.18 — CARE user journey, from postcode entry through to a recommended next action.](006_Dissertation/figures/figure_3_user_journey.png){width=48%}

## 3.17 Usability Evaluation

Per Section 2.3's relevance-cycle requirement, the dashboard is assessed through usability with representative non-experts: a convenience sample of six participants (three per version, no flood-risk or data-science background), each completing an 11-question questionnaire covering risk classification, explanation understanding, trust, action intent, recommendation usefulness and improvements, analysed using Braun and Clarke's (2006) inductive thematic analysis (Section 2.7), targeting RQ2 and RQ3 directly.

## 3.18 Ethical Considerations

No participant activity proceeded before Departmental Ethics Committee approval; every participant received a Participant Information Sheet and gave informed consent before their session (Section 5.2; no names or demographics beyond version assignment were collected). All environmental data used elsewhere (Sections 3.3–3.5) is open-access with no personally identifiable information; the only personal data collected is the questionnaire responses, handled under the approved protocol and anonymised as P01–P06 throughout Chapter 5.

## 3.19 Limitations

**Label construction and apparent accuracy.** Chapter 4's near-ceiling accuracy reflects recovering a deterministic, literature-grounded labelling rule, not validation against independently observed flood outcomes — the label is partly derived from the model's own inputs (Section 3.5).

**Spatial autocorrelation and rainfall resolution.** The 100 m grid is far finer than HadUK-Grid's native 5 km resolution, so nearby points often share a raster cell, limiting spatial variation the rainfall features can carry relative to elevation/distance.

**Single-city scope; batch data.** Scoped to one 5 km radius, one city, by deliberate MSc-timeframe design choice (Section 1.8); thresholds and historical-event context are Glasgow-specific, and all inputs are static snapshots.

**XGBoost SHAP comparability.** Valid only at feature-ranking level, not magnitude, due to a library constraint on probability-space explanation for XGBoost's multiclass objective (Section 4.5).

**Usability sample size.** The six-participant convenience sample (Section 3.17) does not support statistically generalisable claims; findings are indicative, not conclusive.

**Accessibility.** No formal accessibility audit or assistive-technology testing was performed; the dashboard's position against WCAG (W3C, 2018) is set out honestly in Table 3.3 (Appendix A.5).

**No automated test suite.** Verification (Section 4.13) was informal and manual/notebook-based — appropriate to this project's scale, but a genuine limitation against professional practice.

# Chapter 4: Results and Technical Evaluation

## 4.1 Experimental Setup

This chapter reports the quantitative results produced by Chapter 3's methodology, answering RQ1 directly. All results use the Random Forest trained in Section 3.6 (`n_estimators=100`, `random_state=42`) on the 80/20 stratified split (6,274 train / 1,569 test points). Every result should be read against Sections 3.5 and 3.7's caveat: `flood_risk` is an engineered label, not an observed flood outcome, so accuracy measures rule-reconstruction, not validated real-world prediction — a point returned to explicitly in Section 4.14.

## 4.2 Classification Performance

On the held-out test set, the Random Forest achieved 99.62% accuracy, 99.50% macro F1, and 99.62% weighted F1. Table 4.1 gives the per-class breakdown; Figure 4.1 shows the confusion matrix, in which only six of 1,569 test points are misclassified, all Low↔High — no confusion at all between Medium risk and either neighbour.

**Table 4.1 — Random Forest test-set performance by class**

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Low risk | 0.996 | 0.996 | 0.996 | 758 |
| Medium risk | 1.000 | 1.000 | 1.000 | 540 |
| High risk | 0.989 | 0.989 | 0.989 | 271 |

![Figure 4.1 — Random Forest confusion matrix on the held-out test set.](002_Dataset/outputs/confusion_matrix.png){width=50%}

This near-ceiling accuracy warrants a direct caveat, developed fully in Section 4.14: because the label is constructed deterministically from elevation and PVA membership — closely related to several model inputs — a substantial share of this performance reflects recovering a known labelling rule, not validating against independently observed flood outcomes. This does not invalidate the exercise: the classifier still has to learn the correct thresholds and combine them with continuous, unthresholded proximity information, exactly what the SHAP layer (Sections 4.7–4.8) needs for faithful attributions. In summary: **CARE achieves 99.62% accuracy in reconstructing the engineered flood-risk proxy label — not 99.62% real-world flood-prediction accuracy.**

## 4.3 Class-Level Performance

Figure 4.2 visualises Table 4.1. All three classes score above 98.9% on every metric; the class imbalance identified in Section 3.5 (48.3%/34.4%/17.3%) does not translate into materially worse performance on the minority High-risk class — the specific failure mode macro-averaged metrics were chosen (Section 3.7) to detect.

![Figure 4.2 — Random Forest per-class precision, recall and F1 on the held-out test set.](002_Dataset/outputs/per_class_prf1.png){width=62%}

## 4.4 Cross-Validation and Spatial Validation

Five-fold stratified cross-validation across the full dataset gave a mean accuracy of 99.26% (± 0.17%) and mean macro F1 of 99.04% (± 0.22%), confirming Section 4.2's result is not an artefact of a favourable train/test split. This still leaves a concern given the study grid's 100 m spacing: neighbouring points are spatially autocorrelated (Section 3.19), so a random split could place near-duplicates on both sides of the boundary, inflating the score. A second five-fold `GroupKFold` evaluation withholding complete 500 m spatial tiles tests this directly (Figure 4.3): mean accuracy 99.21% (±0.36%), macro F1 98.97% (±0.47%).

![Figure 4.3 — Validation strategy comparison: held-out test split, random 5-fold CV, and spatial-block 5-fold CV (500m tiles) produce closely similar accuracy, suggesting spatial autocorrelation does not materially inflate the reported score.](002_Dataset/outputs/validation_strategy_comparison.png){width=60%}

## 4.5 Model Comparison

XGBoost trained on an identical split achieved 99.36% accuracy and 99.17% macro F1 — consistently, if marginally, below Random Forest (Table 4.2, Figure 4.4). At this accuracy ceiling, a 0.26-point gap is better read as both algorithms converging on the same near-perfect reconstruction of a deterministic label (Section 3.5) than as evidence Random Forest is intrinsically stronger. Native feature-importance rankings agree closely (elevation dominant, `dist_to_clyde` second in both), but SHAP rankings diverge for `dist_to_clyde` specifically: `TreeExplainer` supports calibrated probability-space output for Random Forest but not XGBoost's multiclass objective, so SHAP magnitudes aren't directly comparable. The accuracy margin therefore played little part in the choice of live model — native probability-space SHAP support is what determined Random Forest was retained. Retraining against a frozen 3-year (2023–2025) snapshot shows the 39-year climatology produced a small, consistent improvement — modest given elevation's dominance, but making rainfall more defensibly *typical* rather than merely recent.

**Table 4.2 — Random Forest vs XGBoost, and vs the original 3-year-rainfall model**

| Metric | RF (39yr, primary) | XGBoost (39yr) | RF (3yr rainfall) |
|---|---:|---:|---:|
| Accuracy | 99.62% | 99.36% | 99.55% |
| F1 macro | 99.50% | 99.17% | 99.42% |

![Figure 4.4 — Model accuracy and macro F1: Random Forest (39-year rainfall, primary model) vs XGBoost vs Random Forest retrained on the earlier 3-year rainfall snapshot.](002_Dataset/outputs/model_accuracy_f1_comparison.png){width=60%}

Figure 4.5 shows one-vs-rest ROC curves, regenerated from the saved train/test split for traceability (the original computation was not retained in notebook history), using the identical Section 3.6 methodology (`RandomForestClassifier(n_estimators=100, random_state=42)`, the same stratified 80/20 split on `feature_matrix.csv`) and `label_binarize`-based one-vs-rest ROC/AUC on the held-out 1,569-point test set — fixing model, seed, split and held-out set together pins down an exact, repeatable result. Mean ROC-AUC is 0.9998 (Low 0.9998, Medium 1.0000, High 0.9996), matching the original figure's values exactly.

![Figure 4.5 — One-vs-rest ROC curves per risk class.](002_Dataset/outputs/roc_curves.png){width=58%}

## 4.6 Feature Importance

Feature importance (Table 4.3, visualised in Figure 4.6) confirms the exploratory finding from Section 3.3: elevation dominates at 62.9%, with `dist_to_clyde` a clear second at 17.2%; the remaining seven features each contribute under 6% individually, with the four rainfall features and the two infrastructure-density features clustered in a long tail.

**Table 4.3 — Random Forest feature importance (Gini-based)**

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | `elevation` | 62.92% |
| 2 | `dist_to_clyde` | 17.16% |
| 3 | `wet_days_per_year` | 5.26% |
| 4 | `mean_annual_mm_day` | 4.18% |
| 5 | `building_count` | 2.38% |
| 6 | `mean_winter_mm_day` | 2.36% |
| 7 | `dist_to_water` | 2.25% |
| 8 | `road_count` | 2.09% |
| 9 | `max_daily_mm` | 1.42% |

![Figure 4.6 — Random Forest feature importance.](002_Dataset/outputs/feature_importance.png){width=68%}

## 4.7 SHAP Global Analysis

A `TreeExplainer` fitted to the trained Random Forest, with SHAP values computed for a fixed random sample of 500 held-out test points (Section 3.8), produces the per-class summary plots in Figure 4.7, confirming at the distributional level what Section 4.6's Gini importances already showed: elevation dominates every class's explanation, with `dist_to_clyde` a consistent second.

![Figure 4.7 — SHAP summary plots by risk class (500-point test sample).](002_Dataset/outputs/shap_summary.png){width=90%}

## 4.8 SHAP Local Analysis

Beyond this aggregate view, individual waterfall explanations were generated for representative points per class, following the Section 3.8 methodology. Figure 4.8 shows one example: the probability-space explanation for a representative High-risk point, decomposing its predicted probability into each feature's contribution — the same style surfaced live in Version B's "Why this result?" panel (Section 3.15) for whichever point a user selects. This decomposition explains the model's own reasoning; it is not evidence of what physically caused flood risk there (Section 2.5).

![Figure 4.8 — SHAP waterfall explanation (probability space) for a representative High-risk point; a real CARE prediction, not a fabricated illustration.](003_Code/shap_waterfall_high_risk_proba.png){width=62%}

## 4.9 Spatial Risk Results

Figure 4.9 maps the Random Forest's predicted risk class across the full 7,843-point study grid, using the model saved in Section 3.6, applied identically to how the live dashboard computes predictions at startup (Section 3.9). High-risk predictions cluster tightly around the River Clyde corridor through central Glasgow, consistent with `dist_to_clyde`'s position as the second most important predictor (Section 4.6); Low-risk predictions dominate the higher-elevation north and south.

![Figure 4.9 — Predicted flood-risk class across the 7,843-point study grid. Source: author's analysis, model output over the study grid (Section 3.3).](002_Dataset/outputs/spatial_risk_map.png){width=68%}

## 4.10 Prediction Confidence

Figure 4.10 maps the same grid, coloured by maximum predicted-class probability. Mean confidence is 99.2%, minimum 52.0% — the least confident points cluster, as expected, near the boundary between adjacent risk classes, where feature values sit close to the elevation/PVA thresholds defining the label (Section 3.5). This is a useful diagnostic: a well-fitted model on a deterministic rule should show near-certainty away from a threshold and reduced confidence only around it; broadly scattered, uncorrelated confidence would instead suggest the classifier was struggling to recover the rule — a check the aggregate accuracy figure (Section 4.2) cannot make visible.

![Figure 4.10 — Spatial distribution of model prediction confidence (maximum predicted-class probability per point). Source: author's analysis, model output over the study grid (Section 3.3).](002_Dataset/outputs/spatial_confidence_map.png){width=68%}

## 4.11 Elevation and Distance-to-Clyde Analysis

Figure 4.11 plots both dominant predictors (Section 4.6) against risk class. Elevation separates the three classes almost completely, High-risk points concentrated at the lowest elevations with little overlap; distance to the Clyde shows the same ordering with more overlap, consistent with its smaller but still substantial Gini importance (17.2% vs 62.9%).

![Figure 4.11 — Elevation and distance-to-Clyde by risk class, across the 7,843-point study grid.](002_Dataset/outputs/elevation_distance_vs_risk.png){width=78%}

## 4.12 Rainfall Analysis

Section 3.4 reported the rainfall features' spatial range at a single point in time; Figure 4.12 instead aggregates the same 111.5-million-row daily record temporally, year by year from 1987 to 2025: mean daily rainfall, estimated wet days (≥1.0mm) per year, and domain-wide maximum daily rainfall each year. Mean daily rainfall across the 39 years ranges from 2.16 to 3.91 mm/day **with no clear monotonic trend visible at this length of record** — reported honestly rather than implying a worsening-climate narrative the data does not support; rainfall history, the engineered flood-risk classification, and observed flood occurrence are three distinct things (Section 3.5), and only the first two are addressed here.

![Figure 4.12 — HadUK-Grid rainfall over the Glasgow study area, 1987–2025: mean daily rainfall, wet-day frequency, and domain-wide maximum daily rainfall, by year. Source: Met Office HadUK-Grid data, author's chart.](002_Dataset/outputs/rainfall_39yr_trend.png){width=60%}

Figure 4.4 (Section 4.5) already showed the 39-year climatology's small downstream effect on model accuracy; Figure 4.13 shows why more directly, comparing the distribution of all four rainfall features under the 39-year climatology against the original, frozen 3-year snapshot. The 3-year window, drawn from a comparatively short and potentially unrepresentative recent period, shows a visibly different — not merely noisier — distribution for several features, supporting the 39-year climatology as more defensibly *typical* rather than only more recent (Section 3.4).

![Figure 4.13 — 39-year vs 3-year rainfall feature distributions across the study grid.](002_Dataset/outputs/rainfall_39yr_vs_3yr_features.png){width=90%}

## 4.13 System Verification

No automated test suite, CI pipeline, or logged PASS/FAIL matrix exists — a genuine limitation, already disclosed in Section 3.19, appropriate to a single-developer MSc project built primarily in interactive notebooks. Ten components spanning the dashboard's core interactions and the ML pipeline's reproducibility were each manually verified, by direct execution or source-code review, evidence type stated explicitly per row so the two are never conflated; the full matrix (Table 4.4) is in Appendix A.6 rather than a fabricated formal test report.

![Figure 4.14 — System verification coverage: informal, manual/notebook-based verification actually performed, honestly distinguished from a formal automated test suite, which does not exist for this project.](006_Dissertation/figures/figure_4_testing_coverage.png){width=70%}

## 4.14 Critical Interpretation of Results

Read together, Sections 4.2–4.13 answer RQ1 but require one integrating caveat: `flood_risk` is constructed from elevation and PVA membership (Section 3.5), and elevation is simultaneously the model's most important feature (Section 4.6) — a genuine label-feature dependency, not a coincidence. A large share of the 99.62% figure reflects the classifier reconstructing a known, deterministic rule from continuous inputs — non-trivial, since it is never told the exact thresholds, only continuous values, and still recovers the rule almost perfectly — but this is not the same claim as validating flood prediction against independently observed outcomes, which this evaluation does not attempt. Spatial-block cross-validation (Section 4.4) rules out one alternative explanation (near-duplicate points inflating the score) without ruling in real-world predictive validity; future work (Section 6.8) would need genuinely observed flood-event records, not the SEPA/elevation proxy used throughout. Within that scope, Sections 4.6–4.12 are trustworthy as descriptions of the model's behaviour and the underlying data. Two further checks probe this caveat directly: an independent spatial audit near the Clyde, and agreement with four real historical flood events.

Every grid point within 150 m of the Clyde was independently re-checked: PVA membership recomputed from scratch via point-in-polygon against the raw `PVAv2.gpkg` boundaries (not the stored label), the same elevation-threshold rule reapplied, and the result compared against what is actually stored.

| Distance threshold | Points checked | Correctly labelled | Mismatched | Match rate |
|---|---|---|---|---|
| < 50 m | 238 | 238 | 0 | 100% |
| < 100 m | 396 | 396 | 0 | 100% |
| < 150 m | 528 | 528 | 0 | 100% |

**Table 4.5 — Independent near-Clyde spatial audit: recomputed vs. stored `flood_risk` label.**

Zero mismatches at every threshold confirms the label was constructed correctly, not merely plausible. Of the 528 points, 81 are Low risk despite river proximity; all 81 sit outside every PVA polygon — Figure 4.15 plots this directly. This is expected, not a defect: SEPA's zones do not cover every metre of riverbank, so a near-river point can legitimately fall outside a PVA and still be low elevation (several sit at 0 m from the water with elevation under 5 m, one as low as −2 m, likely a DEM artefact). The audit narrows, rather than removes, the Section 3.5 circularity concern: membership itself is applied correctly, but boundaries — not the classifier — are the source of any near-river disagreement with intuition.

![Figure 4.15 — Near-Clyde audit: recomputed risk class and PVA membership for all 528 points within 150m of the Clyde, against elevation and distance to river.](002_Dataset/outputs/clyde_pva_audit_scatter.png){width=85%}

The second check is external: agreement with four documented historical events (Table 4.6), independently geocoded and matched to their nearest grid point.

| Event | Date | Nearest grid point | Model prediction | Consistent? | Why |
|---|---|---|---|---|---|
| Glasgow East End (Greenfield) | 30 Jul 2002 | 37m away | Medium, 100% conf. | Yes | Elevated risk correctly reflects a documented surface flood |
| SEC Centre | 12 Dec 1994 | 50m away | High, 99% conf. | Yes | Elevated risk correctly reflects a documented surface flood |
| Glasgow Central, Low Level | 12 Dec 1994 | 57m away | Low, 97% conf. | No | Same event as SEC Centre, but water reached the station via disused rail tunnels, not a surface pathway |
| Saltmarket bridge | 18 Nov 1795 | 46m away | Low, 88% conf. | No | Outside the nearest PVA polygon (Table 4.5 shows this is common near the river) — a label-boundary limitation, not a model error |

**Table 4.6 — Four historical flood events: agreement with model prediction.**

Two of four agree; both disagreements trace to a named cause, not unexplained noise — an underground pathway surface features cannot represent, and a PVA-boundary gap of the kind Table 4.5 shows is common near the river. Four points is too small to generalise from, but the pattern is consistent with the audit above: where the label and its inputs can see the mechanism, they agree with history; where flooding travels underground or the SEPA zone stops short, they do not, predictably.

# Chapter 5: User Evaluation and Discussion

## 5.1 Evaluation Design

This chapter reports the usability evaluation designed in Section 3.17, using genuine responses from six participants (three per version), collected via the approved Participant Questionnaire and verified against the source spreadsheet, not the blank template. Each participant completed the 11-question instrument independently after using their assigned version — self-completed, not a moderated think-aloud session, a deviation from the originally planned protocol disclosed here rather than smoothed over. The chapter addresses RQ2 and RQ3, and revisits RQ1 briefly. Given the small, non-random sample, findings are reported descriptively and exploratorily, not as statistically generalisable conclusions (Section 3.19).

## 5.2 Participant Profile

Six participants completed the study: three used Version A, three used Version B, matching the planned allocation (Figure 5.1). Responses are anonymised P01–P06 (P01–P03: Version A; P04–P06: Version B); no demographic data was collected beyond version assignment, consistent with the approved, minimal-personal-data protocol (Section 3.18).

![Figure 5.1 — Participant distribution by dashboard version (n=6).](002_Dataset/outputs/usability_participant_distribution.png){width=42%}

## 5.3 Risk Understanding

Five participants consistently articulated the displayed risk level. P06's Q3 response recorded "High," while Q4–Q5 described a "Low" result; this inconsistency is retained as a data-quality anomaly (Section 5.13), not silently corrected (Figure 5.2). Version A participants described drivers in general terms — rainfall, nearby water, historical flooding (P02, P03); Version B participants named model input features — elevation, distance to the Clyde (P04) — indicating the SHAP panel (Section 3.15) added feature-level specificity beyond Version A's context cards alone.

![Figure 5.2 — Risk levels evaluated, as recorded in Q3 (n=6). P06 recorded "High" in Q3 but described "Low" throughout Q4–Q5 — see Section 5.13.](002_Dataset/outputs/usability_risk_levels_evaluated.png){width=50%}

## 5.4 Prediction Summary and Dashboard Comprehension

The prediction summary screen (Section 3.12), shared by both versions, functioned as intended: every participant could state their result's risk category and confidence-adjacent context without difficulty, and no one reported confusion about the risk badge itself — only, for two Version B participants, about the SHAP chart beneath it (Section 5.10). The comprehension cost discussed below is specific to the added explanation content.

## 5.5 Charts and Contextual Information

The interactive risk map (Section 3.13) drew specific positive comment in both versions — P01 highlighted the risk-level filters, P05 and P06 the map and postcode search generally — with no participant reporting difficulty, consistent with the map being identical in both versions (Table 3.2).

## 5.6 Location Details

The location details panel (Section 3.12) was not named directly, but its content — elevation, nearest SEPA zone, citywide risk context — is exactly what Version A participants cited when explaining their result's basis (P01's "rainfall data, elevation," P02/P03's "nearby water bodies," "previous flooding"). This is indirect but genuine evidence the panel succeeds as *context* even without an explanation layer (Section 2.7).

## 5.7 Recommendation Usefulness

All six participants found the recommendations relevant and useful (Q8, 6/6 "Yes"; Figure 5.3, left), citing practicality (P02, P03, P05) and direct linkage to the displayed risk class (P04, P06) — supporting RQ2. Action intent was more varied (Figure 5.3, right): three affirmed a behaviour change (P02, P03, P05), one gave a qualified answer (P06: would check official information but not act on a Low-risk result alone), one said "Maybe" (P04), and one said no, already feeling informed (P01) — relevance and stated intent to act are not the same thing, and RQ2 asked about them separately for this reason.

![Figure 5.3 — Recommendation usefulness (Q8) and action intent (Q7), n=6.](002_Dataset/outputs/usability_recommendation_action.png){width=78%}

## 5.8 Trust and Transparency

Figure 5.4 compares thematic content across versions. Both groups cited explanation/reasoning as their trust driver (3/3 each) — but only Version B participants used explicit transparency language ("black box," 2/3) or referred directly to the explanation panel as the reason for their trust (P04), and only Version B participants reported technical-terminology friction (2/3). This is descriptive, not statistical (n=3 per group), but directionally consistent with the explanation layer adding both perceived transparency and a small comprehension cost.

![Figure 5.4 — Trust and explanation themes by version (thematic tally), n=3 per group.](002_Dataset/outputs/usability_trust_explanation_themes.png){width=70%}

## 5.9 Version A versus Version B

Table 5.1 summarises the evaluation across both versions dimension by dimension, drawn only from the qualitative tallies already presented — no comparison invented beyond these counts, consistent with the small-n, descriptive framing (Section 5.1).

**Table 5.1 — Participant evaluation summary by dashboard version**

| Dimension | Version A (n=3) | Version B (n=3) |
|---|---|---|
| Risk understanding (Section 5.3) | All 3 correctly stated risk level and general basis | Two participants consistently stated the displayed risk level and basis; P06 contained a documented Q3/Q4–5 inconsistency (Section 5.13). Version B responses nevertheless showed greater feature-level specificity |
| Recommendation usefulness (Section 5.7) | 3/3 "Yes" | 3/3 "Yes" |
| Action intent (Section 5.7) | 2 Yes, 1 No | 1 Yes, 1 Maybe, 1 qualified |
| Trust driver cited (Section 5.8) | 3/3 cite explanation/reasoning | 3/3 cite explanation; 2/3 use explicit "black box" language |
| Technical/terminology friction (Section 5.10) | 0/3 | 2/3 |
| Specific improvement suggested (Section 5.12) | 3/3 | 1/3 |

A between-groups caveat applies throughout: participants were assigned to one version only, so the table shows what each group experienced, not a controlled within-subject comparison.

## 5.10 SHAP Explainability: Benefits and Comprehension Cost

Among Version B participants, all three (3/3) reported the explanation reduced "black box" perception and increased trust (P04, P05, P06). Two of three (P04, P06) also found the SHAP chart harder to follow than the rest of the interface, and P06 proposed a legend/tooltip plus a simple/detailed toggle (Figure 5.5). The same participants who associated the explanation with increased trust are also the only ones reporting comprehension friction: explainability and comprehensibility are not the same thing, and both must be reported together.

![Figure 5.5 — SHAP explanation feedback, Version B only (n=3).](002_Dataset/outputs/usability_shap_feedback.png){width=58%}

## 5.11 Usability and Accessibility

All six participants described the dashboard as easy or straightforward to navigate, with no blocking usability problem reported — positively answering the navigation half of RQ3 for both versions. The accessibility half is more qualified: two Version B participants flagged the SHAP chart's technical presentation as a barrier for non-technical users, echoing the limitation already disclosed in Section 3.19. No other barrier (text size, colour contrast, navigation) was reported, though this evaluation did not specifically recruit assistive-technology users (Section 6.7).

## 5.12 Participant-Identified Improvements

Figure 5.6 tallies improvement suggestions. Live/real-time weather data and wider geographic coverage beyond Glasgow were each raised twice, both by Version A participants (P02, P03) — an evidence-based pointer for future work (Section 6.8). One Version B participant (P06) suggested a SHAP legend/tooltip and a simple/detailed toggle; two (P04, P05) offered no specific suggestion.

![Figure 5.6 — User-suggested improvement themes, Q10 (n=6).](002_Dataset/outputs/usability_improvement_themes.png){width=70%}

## 5.13 Data-Quality Issues and Evaluation Limitations

Beyond the small, non-random sample (Section 3.17), the response dataset itself contains genuine data-quality issues, reported transparently rather than corrected: response IDs in the export run 2, 3, 4, 6, 7, 8 — ID 5 is absent, unexplained by any available record. P05's answers to the confidence and trust questions (Q5, Q6) are word-for-word identical, suggesting a copy-paste artifact rather than two independently composed answers. P06's Q3 field records "High Flood Risk," but this participant's own Q4 and Q5 answers both describe a "Low risk" result throughout — an internal contradiction within a single response; Q3 is reported as recorded in Figure 5.2, with this discrepancy flagged rather than silently resolved. P05 and P06 additionally share identical start/completion timestamps (17:46:38–17:54:19) despite differing free-text content, an unexplained and unresolved anomaly. None of these issues were corrected, removed, or reinterpreted in the analysis above.

## 5.14 Discussion Against Research Questions

Briefly, ahead of the full evidence matrix in Table 6.1: **RQ1 (indirect)** — no participant questioned or distrusted the underlying classification, only how it was explained, though n=6 cannot validate real-world accuracy (Sections 3.19, 4.14). **RQ2** — answered positively: all six found recommendations relevant and useful (Section 5.7), P05 describing the dashboard as helping "translate the technical result into information that a normal user could act upon." **RQ3** — positive with a scoped caveat: both versions were rated easy to navigate (Section 5.11), and Version B's explanation layer increased trust and reduced "black-box" perception for all three of its participants (Section 5.10) alongside a named comprehension cost for two of the same three, consistent with Hevner et al.'s relevance cycle (Section 2.3). Since Version A participants were never shown a SHAP panel, their responses cannot establish they would have found one unhelpful (Table 5.1's between-groups caveat).

## 5.15 Chapter Summary

These findings are exploratory, drawn from a small convenience sample with disclosed data-quality issues, and should be read as indicative rather than conclusive (Section 3.19). Chapter 6 draws them together with Chapters 1–4 to answer all three research questions.

# Chapter 6: Conclusions, Recommendations and Future Work

## 6.1 Introduction

This chapter summarises the research, answers the three research questions with their evidence, restates CARE's contribution, and sets out recommendations, limitations and future work.

## 6.2 Research Summary

CARE closes a gap identified in Chapter 2: authoritative flood-risk data exists — SEPA's boundaries, HadUK-Grid rainfall, OSM infrastructure, NASA elevation — but is rarely converted into something a non-specialist can act on, since no integrated system combining a trained classifier, structured recommendation and public dashboard was identified, existing tools remain descriptive, and SHAP is applied almost exclusively offline. The system combines four open datasets into a 7,843-point, nine-feature grid; trains and evaluates a Random Forest benchmarked against XGBoost; attaches a live, probability-space SHAP layer; and pairs each prediction with a deterministic, source-cited recommendation inside two dashboard versions built to isolate whether explanation helps. Six participants evaluated the result (Chapter 5); limitations were disclosed throughout rather than reserved for a closing section.

## 6.3 Answers to RQ1, RQ2 and RQ3

RQ1 is answered technically (Sections 4.2–4.6, 4.14): near-ceiling accuracy that reconstructs an engineered proxy label, not independently validated real-world prediction — a caveat the near-Clyde audit and historical-event check narrow but do not remove. RQ2 and RQ3 come from Chapter 5: positive, scoped answers on recommendation usefulness and usability, not unqualified success claims. Table 6.1 traces each question end to end against its evidence, finding, limitation and conclusion.

**Table 6.1 — Research-question evidence matrix**

| Research Question | Evidence | Main Finding | Limitation | Conclusion |
|---|---|---|---|---|
| RQ1: model accuracy and predictors | Chapter 4 (Sections 4.2–4.6): confusion matrix, cross-validation, feature importance | 99.62% test accuracy, 99.50% macro F1; elevation and distance-to-Clyde dominant | Label is engineered from elevation/PVA membership, not independently observed flood outcomes (Section 4.14) | Model reconstructs the engineered proxy label reliably; real-world predictive validity remains future work (Section 6.8) |
| RQ2: recommendation comprehensibility | Chapter 5 (Section 5.7): Q7–Q8 responses, all 6 participants | 6/6 found recommendations relevant and useful | Small, non-random sample (n=6); self-completed questionnaire, not moderated interview | Positive, exploratory support; not statistically generalisable |
| RQ3: usability and explainability (incl. Version B) | Chapter 5 (Sections 5.8, 5.10–5.11): trust/explanation themes, SHAP feedback | Both versions easy to navigate; Version B increased trust for 3/3 but introduced technical friction for 2/3 | Between-groups design (Table 5.1), two data-quality anomalies in response data (Section 5.13) | Usability supported; explainability improves trust but is not automatically comprehensible without further design work |

## 6.4 Research Contribution

Consistent with Section 1.7, the contribution is a systems and communication one, not methodological novelty: established techniques (Chapter 2) combined into an artefact with no directly comparable precedent identified (Section 1.3) — bounding the originality claim to integration and evaluation, not any single technique. Chapter 5's evidence supports this as demonstrated, not only claimed: explanation and recommendation were prominent trust drivers, while the underlying classification was generally experienced as part of the wider system, not independently evaluated (Section 5.14). Table 6.2 sets out the relative merits behind this contribution, rather than leaving the justification implicit across Chapters 2–4.

**Table 6.2 — Relative merits of key technologies and methodological choices**

| Choice | Why selected | Advantage | Limitation | Fit to CARE |
|---|---|---|---|---|
| Random Forest vs XGBoost | Strongest on comparable tasks (§2.2); native probability-space SHAP | Robust to unscaled inputs, minimal tuning | XGBoost marginally higher on some folds; both share the label dependency (§4.14) | Primary model; XGBoost as benchmark (§3.6, §4.5) |
| SHAP vs LIME/permutation/Gini | Only per-prediction, model-agnostic, probability-space capable (§2.5) | Theoretically grounded, consistent, fast enough live | Explains behaviour not causation; XGBoost multiclass unsupported (§4.5) | Live "Why this result?" panel (§3.8, §3.15) |
| Spatial-block vs random CV | Random splits risk inflated scores from autocorrelated neighbours (§3.19) | Tests generalisation across independent 500 m tiles | Does not, alone, validate against observed floods (§4.14) | Reported alongside random CV (§4.4) |
| Batch vs live environmental data | A live feed adds complexity disproportionate to an MSc prototype (§1.8) | Reproducible, versioned, no API dependency | Reflects data current at collection, not real time | Disclosed limitation (§3.19) |
| Rule-based vs learned recommendations | Correct guidance is civil-protection practice, not inferred preference; no interaction log exists (§2.6) | Predictable, auditable, source-cited | Limited personalisation beyond risk class | Recommendation engine (§3.16) |
| Interactive dashboard vs static reporting | A static report can't answer a specific postcode or explain interactively (§3.9) | Integrates prediction, context, explanation, action | Needs a running app, unlike a shareable file | Both versions (§3.9–§3.11) |
| Postcode search vs map-only exploration | A map-only interface assumes spatial literacy some users lack (§1.1) | Near-zero-friction entry via `postcodes.io` | External API dependency; map still available | Primary entry point, both versions (§3.9) |

## 6.5 Practical Recommendations

For users: treat CARE as contextual research information, not an official flood risk assessment, and cross-check against SEPA's own maps (Section 3.10). For prospective adopters elsewhere: the pipeline generalises, but thresholds and historical-event context need re-fitting to local topography and hydrology (Section 3.19). For the targeted university/community groups (Section 1.1): the evaluation (Chapter 5) indicates explanation and recommendation were prominent trust drivers, more so than the risk map alone.

## 6.6 Technical Recommendations

Two participant-identified improvements stand out: a legend or simple/detailed toggle for the SHAP chart (Section 5.10), and live/wider-coverage data (Section 5.12) — both scoped and traceable to specific evidence rather than generic suggestions.

## 6.7 Limitations

Limitations were disclosed throughout rather than reserved for this section (Sections 3.19, 4.14, 5.13). Technically: the engineered-label/circularity concern governing how 99.62% should be read; spatial autocorrelation given the fine grid relative to HadUK-Grid's native resolution; single-city scope; batch, not real-time, data; an XGBoost SHAP comparability constraint. Operationally: no automated test suite, only informal manual verification (Section 4.13). On evaluation: a six-participant convenience sample; a self-completed questionnaire rather than the originally planned moderated think-aloud protocol; a between-groups, not within-subject, comparison; two disclosed data-quality anomalies (Section 5.13); accessibility not specifically tested with assistive-technology users. None were hidden, and none invalidate the contribution (Section 6.4) — they scope what it demonstrates.

## 6.8 Future Work

Each direction ties to a specific limitation (Section 6.7): validating predictions against independently observed historical flood outcomes beyond the engineered proxy label — the change that would most strengthen any future real-world accuracy claim (Section 4.14); a larger, moderated usability study; an automated test suite; accessible, screen-reader-navigable SHAP output (Sections 3.19, 5.10); multi-city generalisation with locally re-fitted thresholds; and a moderated questionnaire format to resolve this evaluation's data-quality anomalies (Section 5.13) in any repeat study.

## 6.9 Final Conclusion

CARE met its aim (Section 1.4): an interactive, explainable, prescriptive flood-risk dashboard for Glasgow, evaluated both technically (Chapter 4) and with real, exploratory user evidence (Chapter 5). The classifier reconstructs a defensible, literature-grounded labelling rule rather than independently validated flood prediction, reported throughout with that caveat; within that honestly-stated scope, participant responses indicate the explanation and recommendation layers were prominent trust drivers, carrying a specific, addressable comprehension cost any future iteration should treat as a design requirement, not an afterthought.

## References

Abedi, R., Costache, R., Shafizadeh-Moghadam, H. and Pham, Q.B. (2021) Flash-flood susceptibility mapping based on XGBoost, random forest and boosted regression trees. *Geocarto International*, 37(19), pp.5479–5496. doi: 10.1080/10106049.2021.1920636

Adadi, A. and Berrada, M. (2018) Peeking Inside the Black-Box: A Survey on Explainable Artificial Intelligence (XAI). *IEEE Access*, 6, pp.52138–52160. doi: 10.1109/ACCESS.2018.2870052

Barredo Arrieta, A., Díaz-Rodríguez, N., Del Ser, J., Bennetot, A., Tabik, S., Barbado, A., García, S., Gil-López, S., Molina, D., Benjamins, R., Chatila, R. and Herrera, F. (2020) Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI. *Information Fusion*, 58, pp.82–115. doi: 10.1016/j.inffus.2019.12.012

Biesbroek, R., Dupuis, J. and Wellstead, A. (2017) Explaining through causal mechanisms: resilience and governance of social-ecological systems. *Current Opinion in Environmental Sustainability*, 28, pp.64–70. doi: 10.1016/j.cosust.2017.07.007

Braun, V. and Clarke, V. (2006) Using thematic analysis in psychology. *Qualitative Research in Psychology*, 3(2), pp.77–101. doi: 10.1191/1478088706qp063oa

Braun, V. and Clarke, V. (2019) Reflecting on reflexive thematic analysis. *Qualitative Research in Sport, Exercise and Health*, 11(4), pp.589–597. doi: 10.1080/2159676X.2019.1628806

Braun, V. and Clarke, V. (2021) Can I use TA? Should I use TA? Should I not use TA? Comparing reflexive thematic analysis and other pattern-based qualitative analytic approaches. *Counselling and Psychotherapy Research*, 21(1), pp.37–47. doi: 10.1002/capr.12360

Breiman, L. (2001) Random forests. *Machine Learning*, 45(1), pp.5–32. doi: 10.1023/A:1010933404324

Chen, T. and Guestrin, C. (2016) XGBoost: A scalable tree boosting system. In: *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp.785–794. doi: 10.1145/2939672.2939785

Fisher, A., Rudin, C. and Dominici, F. (2019) All Models are Wrong, but Many are Useful: Learning a Variable's Importance by Studying an Entire Class of Prediction Models Simultaneously. *Journal of Machine Learning Research*, 20, pp.1–81.

Hevner, A.R., March, S.T., Park, J. and Ram, S. (2004) Design science in information systems research. *MIS Quarterly*, 28(1), pp.75–105. doi: 10.2307/25148625

Hollis, D., McCarthy, M., Kendon, M., Legg, T. and Simpson, I. (2019) HadUK-Grid — A new UK dataset of gridded climate observations. *Geoscience Data Journal*, 6(2), pp.151–159. doi: 10.1002/gdj3.78

Ideal Postcodes (n.d.) *Postcodes.io: Postcode and geolocation API for the UK*. Available at: https://postcodes.io (Accessed: August 2026).

Lundberg, S.M. and Lee, S.-I. (2017) A unified approach to interpreting model predictions. In: *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30.

Lundberg, S.M., Erion, G., Chen, H., DeGrave, A., Prutkin, J.M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N. and Lee, S.-I. (2020) From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2(1), pp.56–67. doi: 10.1038/s42256-019-0138-9

NASA JPL (2013) *NASA Shuttle Radar Topography Mission Global 1 arc second* [Dataset]. NASA EOSDIS Land Processes Distributed Active Archive Center. doi: 10.5067/MEASURES/SRTM/SRTMGL1.003

Nielsen, J. (1994) *Usability Engineering*. San Francisco: Morgan Kaufmann. ISBN: 978-0125184069

OpenStreetMap contributors (2026) *Planet dump* [Data file]. Available at: https://planet.openstreetmap.org (Accessed: August 2026). © OpenStreetMap contributors, available under the Open Database Licence.

Power, D.J. and Sharda, R. (2009) Decision support systems. In: *Springer Handbook of Automation*. Berlin: Springer, pp.1521–1536. doi: 10.1007/978-3-540-78831-7_87

Renn, O. (2008) *Risk Governance: Coping with Uncertainty in a Complex World*. London: Earthscan. ISBN: 978-1-84407-291-0

Ribeiro, M.T., Singh, S. and Guestrin, C. (2016) "Why should I trust you?": Explaining the predictions of any classifier. In: *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp.1135–1144. doi: 10.1145/2939672.2939778

Ricci, F., Rokach, L. and Shapira, B. (2015) Recommender systems: Introduction and challenges. In: *Recommender Systems Handbook*. Springer, pp.1–34. doi: 10.1007/978-1-4899-7637-6_1

Rizzoli, A. and Young, W. (1997) Delivering environmental decision support systems: Experience and challenges. *Environmental Modelling & Software*, 12(2–3), pp.237–247. doi: 10.1016/S1364-8152(97)00016-9

Rolnick, D., Donti, P.L., Kaack, L.H., Kochanski, K., Lacoste, A., Sankaran, K., Ross, A.S., Milojevic-Dupont, N., Jaques, N., Waldman-Brown, A., Luccioni, A., Maharaj, T., Sherwin, E.D., Mukkavilli, S.K., Kording, K.P., Gomes, C., Ng, A.Y., Hassabis, D., Platt, J.C., Creutzig, F., Chayes, J. and Bengio, Y. (2022) Tackling climate change with machine learning. *ACM Computing Surveys*, 55(2), pp.1–96. doi: 10.1145/3485128

SEC (n.d.) *History of the SEC*. Available at: https://www.sec.co.uk/about-the-sec/history-of-the-sec (Accessed: August 2026).

SEPA (2023) *Flood maps for Scotland*. Scottish Environment Protection Agency. Available at: https://www.sepa.org.uk/hazards/flood-risk/ (Accessed: August 2026).

Shneiderman, B., Plaisant, C., Cohen, M., Jacobs, S., Elmqvist, N. and Diakopoulos, N. (2017) *Designing the User Interface: Strategies for Effective Human-Computer Interaction*. 6th ed. Pearson. ISBN: 978-0134380391

Singleton, A. and Spielman, S. (2014) The past, present, and future of geodemographic research in the United States and United Kingdom. *The Professional Geographer*, 66(4), pp.558–567. doi: 10.1080/00330124.2013.837591

Spiegelhalter, D. (2017) Risk and uncertainty communication. *Annual Review of Statistics and Its Application*, 4, pp.31–60. doi: 10.1146/annurev-statistics-010814-020148

Tehrany, M.S., Pradhan, B. and Jebur, M.N. (2014) Flood susceptibility mapping using a novel ensemble weights-of-evidence and support vector machine models in GIS. *Journal of Hydrology*, 512, pp.332–343. doi: 10.1016/j.jhydrol.2014.03.008

The Scotsman (2017) Remembering Glasgow's floods of 2002. *The Scotsman*, [online]. Available at: https://www.scotsman.com/news/remembering-glasgows-floods-of-2002-1485828 (Accessed: August 2026).

Tomaszewski, B. (2015) *Geographic Information Systems (GIS) for Disaster Management*. CRC Press. doi: 10.4324/9781315770635

W3C (2018) *Web Content Accessibility Guidelines (WCAG) 2.1*. W3C Recommendation. Available at: https://www.w3.org/TR/WCAG21/ (Accessed: August 2026).

Zhang, Y. and Chen, X. (2020) Explainable Recommendation: A Survey and New Perspectives. *Foundations and Trends in Information Retrieval*, 14(1), pp.1–101. doi: 10.1561/1500000066

# Appendix A: Reproducibility and Project Repository

The complete CARE implementation — source code, both dashboard versions, data-processing scripts, dependency information, and supporting implementation artefacts — is available through the project's GitHub repository. External datasets are referenced according to their respective sources (Section 3.3); restricted, licensed or very large datasets are not redistributed in the repository where appropriate, with acquisition and source information provided through the project materials.

**Repository**: [https://github.com/RiteshGhorpade1/Flood-Risk-Prediction-Glasgow](https://github.com/RiteshGhorpade1/Flood-Risk-Prediction-Glasgow)

## A.1 Repository

The GitHub repository above is the primary technical reference accompanying this dissertation, containing the full implementation documented in Chapter 3.

## A.2 Data

The datasets used and their sources are described in Chapter 3 (Section 3.3). Acquisition and source information for each dataset is available in the repository.

## A.3 Reproduction

Dependency requirements and reproduction instructions, including how to launch both dashboard versions, are provided in the repository.

## A.4 Dashboard

The repository contains the final Version A and Version B dashboard implementations evaluated in this dissertation (Chapter 3, Chapter 5).

## A.5 Accessibility Summary (Table 3.3)

Referenced from Section 3.19's accessibility limitation. No formal accessibility audit or assistive-technology testing was performed; each row below states plainly what was and was not done, rather than implying a testing pass that did not happen.

**Table 3.3 — Accessibility summary**

| Dimension | Current state | Formally tested? |
|---|---|:---:|
| Colour convention | Fixed Low/Medium/High colours; every colour-coded result also has a plain-text label | No |
| Text alternatives | Every chart paired with a plain-text sentence stating its core finding (Section 3.15) | No |
| Screen-reader support | SHAP/evaluation charts are static images; surrounding text is readable but charts are not interrogable | No — known gap |
| Keyboard interaction | Standard Streamlit widgets are keyboard-navigable by default; no custom trap identified in manual use | No |
| Assistive-technology evaluation | Not conducted; Chapter 5's evaluation did not specifically recruit assistive-technology users | No — known gap |
| Known limitations | Chart accessibility and assistive-technology testing are the two gaps, carried into future work (Section 6.8) | — |

## A.6 Manual System Verification Log (Table 4.4)

Referenced from Section 4.13. None of the checks below are automated tests; all were performed manually, either by direct interactive execution against the live dashboard/notebooks or by source-code review.

**Table 4.4 — Manual system verification matrix**

| ID | Component | Input | Expected | Observed | Evidence |
|---|---|---|---|---|---|
| V1 | Postcode search | "G1 1XQ" | Nearest grid point located; risk badge and confidence populate (both versions); compass updates (Version A) | As expected | Live dashboard |
| V2 | Postcode error handling | Invalid postcode; network failure | Specific error, no crash | Branches confirmed by source inspection | Code review |
| V3 | Explanation panel co-location | Select a new location, Version B | "Why this result?" panel recomputes for the new point on the same page, no separate navigation required | As expected | Live dashboard |
| V4 | SHAP rendering | Selected point, Version B | Narrative, caveat, 9-feature chart | As expected (Figure 3.15) | Live dashboard |
| V5 | Recommendation panel | Selected point, both versions | Risk-specific, source-cited guidance | As expected (Figure 3.17) | Live dashboard |
| V6 | Data path availability | Four raw sources | All resolve, none missing | Confirmed (`01_Data_Collection.ipynb`) | Notebook |
| V7 | Feature-join integrity | Full 7,843-point grid | Zero missing values | Confirmed (3.4) | Notebook |
| V8 | Model reproducibility | Fixed `random_state=42`, saved split | Reproduces 99.62% exactly | Exact match (4.2, 4.5) | Regeneration script |
| V9 | SHAP waterfall consistency | Representative High-risk point | Contributions sum to predicted probability | Confirmed | Notebook |
| V10 | Recommendation coverage | All three classes | Distinct, source-cited guidance each | Confirmed by source inspection | Code review |
