---
title: "An Interactive Machine Learning and Decision Support Dashboard for Flood Risk Communication"
subtitle: "Dissertation Draft — Chapters 1–3"
author: "Ritesh Raju Ghorpade (202559288)"
---

# Chapter 1: Introduction

**MSc Advanced Computer Science with Data Science, University of Strathclyde**
**Supervisor: Dr Daniel Thomas**

## 1.1 Background and Motivation

The United Kingdom has been affected by climate change in ways that include a marked increase in flooding, one of its most disruptive effects, driven by changing precipitation patterns and rising sea levels [1]. Flooding is not a hazard confined to a single mechanism: fluvial flooding from rivers bursting their banks, pluvial (surface-water) flooding from rainfall overwhelming urban drainage, and coastal flooding from tidal surge each contribute, and a given location's overall risk is typically shaped by some combination of the three rather than by any one in isolation. Glasgow and the west of Scotland are especially exposed on this combined basis: the River Clyde catchment is subject to frequent high-flow events, and the continued densification of the city's built-up areas — more roofs, more roads, less permeable ground — has steadily reduced its natural drainage capacity, worsening surface-water risk even where fluvial risk from the Clyde itself is unchanged. Two documented events discussed later in this dissertation, the 2002 East End floods and the 1994 SEC Centre floods, illustrate that this is not a hypothetical or purely statistical risk for the city.

At the same time, the environmental data needed to understand this risk is not scarce. The Scottish Environment Protection Agency (SEPA) publishes national flood-boundary shapefiles identifying areas assessed as vulnerable to flooding from any source; the Met Office distributes decades of gridded daily rainfall through HadUK-Grid; OpenStreetMap and NASA both provide open infrastructure and elevation data at national scale, free to access and machine-readable. What is missing is not the data but the layer that turns it into something a resident, a community group, or a local decision-maker can actually use. A national flood-boundary shapefile, opened in GIS software, is genuinely authoritative — but it is not something most residents of a city will ever open, and even if they did, a boundary polygon does not on its own answer the two questions a non-specialist actually has: *is my specific location at risk, and if so, what should I do about it?* Technical risk mapping, on its own, does not translate into individual or group action [2], [3]. Closing that specific gap — between authoritative, open, technically correct data and an individual resident's ability to act on it — is the problem this project addresses.

This project — CARE, Climate Awareness and Risk Evaluation — was conceived to close that gap directly, by building an interactive dashboard that trains a machine learning flood-risk classifier on public data for a defined study area, explains its own predictions in plain language, and pairs each prediction with concrete, source-cited guidance. Figure 1.1 sets out the five-layer system architecture that structures the remainder of this dissertation: four open data sources feed a spatial data pipeline, which supplies a machine learning model, whose predictions pass through a rule-based recommendation engine before reaching the user through an interactive dashboard. This architecture was fixed at the project's outset and is referenced throughout Chapter 3, where each layer is documented in turn.

![Figure 1.1 — CARE's five-layer system architecture: open data sources feed a spatial data pipeline, a Random Forest model, a rule-based recommendation engine, and finally the interactive dashboard. Established at the project's outset and documented layer-by-layer in Chapter 3.](/Users/riteshghorpade/Documents/010_Project/006_Dissertation/figures/figure_1_1_conceptual_framework.png){width=78%}

The remainder of this chapter sets out the specific problem this addresses (Section 1.2), the aim, objectives and research questions that structure the rest of the project (Section 1.3), the contribution claimed (Section 1.4), and the structure of the remaining chapters (Section 1.5).

## 1.2 Problem Statement and Research Gap

A systematic review of the literature relevant to this project (conducted in full in Chapter 2) identified three specific gaps that motivate the work.

**Gap 1 — No integrated system.** No integrated system was found — for Glasgow or, as far as the review established, more generally — that combines a trained machine learning flood-risk classifier, a structured recommendation layer, and an interactive public-facing dashboard in one artefact. Individually, each of these three components is well established in isolation: flood-susceptibility classifiers are a mature research area in their own right (Section 2.2), decision-support dashboards are common in environmental applications generally (Section 2.3), and rule-based recommendation is a well-understood pattern from the wider recommender-systems literature (Section 2.5). Figure 1.2 makes this positioning concrete: what the review did not find is a system occupying the intersection of all three, rather than stopping after the first.

![Figure 1.2 — The research gap positioned at the intersection of three individually well-established components. No prior system was found combining all three in one publicly accessible artefact.](/Users/riteshghorpade/Documents/010_Project/006_Dissertation/figures/figure_1_2_research_gap.png){width=62%}

**Gap 2 — Descriptive, not prescriptive, tools.** The existing tools that are publicly available remain overwhelmingly *descriptive*: SEPA's own flood-boundary shapefiles and the Met Office's HadUK-Grid data, introduced above as exactly the kind of authoritative open data this project builds on, are themselves clear examples — they show a flood boundary or a rainfall statistic, without converting that information into a *prescriptive* recommendation a non-specialist user can act on [2], [6]. This descriptive/prescriptive distinction, developed fully in Section 2.3, is treated in this project not as an abstract theoretical framing but as a direct, testable design requirement: a system that only visualises risk has not, on this project's own terms, closed the gap identified above, however accurate its underlying model might be.

**Gap 3 — Explanation as a diagnostic tool, not a user-facing feature.** No reported work was found that uses SHAP-based feature attribution to connect individual machine learning flood-risk predictions to human-understandable, per-prediction explanations inside an interactive dashboard, rather than only as a static, offline model-diagnostic exercise [14]. SHAP and similar explainability techniques are by now common in the machine learning literature as a way for a *model developer* to audit a model's behaviour; this project instead treats explainability as something to be surfaced directly to the *end user*, live, for the specific prediction relevant to them, which is a materially different design target from the offline diagnostic use case the technique is more commonly applied to.

Taken together, these three gaps define the specific, narrow contribution this project targets: not a more accurate flood-risk model in the abstract, but a genuinely integrated, explained, and prescriptive system, built and evaluated as a single artefact — the four-part contribution set out in Section 1.4.

## 1.3 Research Aim, Objectives and Questions

**Research aim.** To design, build and evaluate an interactive, machine-learning-driven flood-risk dashboard for Glasgow that predicts neighbourhood-level flood risk from open environmental data, explains each prediction, converts it into plain-language guidance, and is demonstrated to be usable by non-specialist users.

**Research objectives.** Four objectives translate this aim into specific, measurable outcomes, refined from the project's original proposal so that each names both the artefact to be produced and the criterion against which it is judged, rather than only a point in the project schedule:

1. To train a Random Forest flood-risk classifier for the Glasgow study area and evaluate it on a held-out test set using macro-averaged F1-score, AUC-ROC and a confusion matrix, benchmarked against an XGBoost comparator (Section 3.4).
2. To apply SHAP analysis to the trained classifier, identifying the top three environmental predictors of flood risk and translating per-prediction explanations into plain language suitable for a non-specialist dashboard user (Section 3.5).
3. To design and pilot a rule-based recommendation engine mapping each of the three risk categories — Low, Medium and High — to differentiated, source-cited guidance drawn from SEPA and Ready Scotland (Section 3.6.3).
4. To develop a working Streamlit dashboard integrating the interactive risk map, the model's live prediction, the SHAP explanation panel and the recommendation panel in one interface, ready for usability evaluation (Section 3.6).

All four objectives were addressed within the project's implementation phase; their outcomes are reported in Chapter 3 and, for the usability evaluation objective 4 anticipates, in Chapter 4.

**Research questions.** Three research questions, established in the original proposal and tested directly by the system documented in this dissertation, structure the evaluation in Chapter 3 and the results and discussion that follow it:

- **RQ1.** How accurately can a machine learning classifier predict neighbourhood-level flood risk in Glasgow, and which environmental factors are the strongest predictors?
- **RQ2.** Does the rule-based recommendation engine produce guidance that a non-specialist audience rates as comprehensible, applicable and personally relevant?
- **RQ3.** Does the resulting dashboard meet an acceptable standard of usability against a recognised ten-heuristic evaluation framework?

Each research question maps directly onto one objective above — RQ1 onto Objectives 1 and 2, RQ2 onto Objective 3, and RQ3 onto Objective 4 — so that the evaluation in Chapter 3 and the findings in Chapter 4 can be read back against a single, consistent set of success criteria rather than a separate, looser notion of "did the project work."

## 1.4 Research Contribution

This project's contribution comprises four elements, each built in direct response to a gap identified in Section 1.2 and shown in Figure 1.1's architecture:

1. **Integration.** A single publicly-usable artefact combining an evaluated machine learning classifier that reconstructs an engineered flood-risk proxy label, SHAP-based per-prediction interpretability, and a structured, rule-based recommendation layer — a combination the literature review in Chapter 2 finds no directly comparable precedent for (Gap 1).
2. **Prescriptive design.** Where existing tools stop at showing risk information, this project's dashboard is designed to be prescriptive: it aims to leave a non-specialist user not only informed of their flood risk, but aware of *why* the model reached that conclusion and *what* a credible, source-backed next step looks like (Gap 2).
3. **User-facing explainability.** SHAP is applied live, per prediction, and surfaced directly to the end user rather than retained as an offline model-diagnostic tool, closing the third gap identified above (Gap 3).
4. **A deliberately bounded scope.** The contribution is scoped to batch (not real-time) data and to a single case-study city, so that the resulting system is realistically attainable and rigorously evaluable within a single MSc dissertation timeframe, rather than attempting broader geographic coverage at the cost of depth or evaluation quality.

This contribution is deliberately positioned as a systems and communication contribution rather than as a claim of methodological novelty in the underlying machine learning itself. Random Forests, gradient-boosted trees and SHAP are all established techniques (Chapter 2), applied here largely as the literature already recommends applying them; the project's contribution is in how these established techniques are combined, integrated with genuinely local multi-source data, and — critically — evaluated for usability with the non-specialist audience they are ultimately intended to serve, which is where Chapter 2 finds the literature to be comparatively thin.

## 1.5 Dissertation Structure

Chapter 2 presents the literature review underpinning the design decisions summarised above, organised around five themes — machine learning for flood-risk prediction, environmental decision support systems, geospatial analysis for urban flood risk, recommendation systems, and the psychology of public risk communication — closing with an explicit synthesis positioning this project against the three gaps identified in Section 1.2. Building directly on that review, Chapter 3 documents the system built in response to it: the study area and its four data sources; the feature-engineering pipeline that converts them into a single modelling dataset; the training, evaluation and comparison of the Random Forest classifier against the criteria set out in Objective 1; the SHAP-based explainability layer implementing Objective 2; the dashboard itself, including the recommendation engine implementing Objective 3 and the two versions built for direct comparison under Objective 4; the design of the usability evaluation that will test RQ2 and RQ3; and a transparent account of the system's limitations. Subsequent chapters, outside the scope of this draft, will report that usability evaluation's actual findings, discuss their implications for all three research questions together, and set out the project's overall conclusions and recommendations for future work.

---

# Chapter 2: Literature Review

## 2.1 Review Scope and Method

A systematic literature search was conducted across IEEE Xplore, Google Scholar and Web of Science, using combinations of the search terms *flood risk prediction machine learning*, *geospatial decision support*, *climate risk communication*, *random forest hydrology*, and *public understanding environmental data*. Sources were retained where they addressed at least one of: a machine learning or statistical method directly applicable to environmental hazard classification; the design or evaluation of environmental or public-facing decision-support software; spatial data integration methods relevant to combining heterogeneous GIS sources; recommendation or explanation-delivery mechanisms; or the psychology and practice of communicating quantitative risk to non-expert audiences. Sources addressing flooding or climate change only from a physical-science or policy perspective, without a methodological or design-relevant contribution to how such information should be modelled, integrated or communicated, were excluded as outside this project's scope, which is a software and data-science artefact rather than a hydrological or policy study in its own right.

The resulting literature is synthesised below around five themes directly relevant to this project's design: machine learning approaches to flood-risk prediction; environmental decision support systems; geospatial analysis for urban flood risk; recommendation systems; and the psychology of public risk communication. Each theme is connected explicitly, at the end of its section, to the specific design decision in this project that it informed, so that the link between the reviewed literature and the system documented in Chapter 3 is traceable rather than left implicit.

## 2.2 Machine Learning for Flood Risk Prediction

Ensemble tree-based classifiers, and Random Forests in particular, have repeatedly outperformed single classifiers on flood-susceptibility mapping tasks. Tehrany, Pradhan and Jebur demonstrate that ensemble approaches recall minority flood-event classes substantially more effectively than logistic regression or support vector machine baselines [5], a finding of direct relevance to any flood classification task, where genuinely hazardous locations are typically the minority class. Breiman's original formulation of the Random Forest algorithm establishes the theoretical basis for this advantage: bootstrap-aggregated ensembles of decorrelated decision trees reduce variance without a corresponding increase in bias, and require comparatively little feature preprocessing to handle correlated, mixed-scale inputs [12] — a property directly relevant to this project's nine engineered features, which span metres, counts and millimetres-per-day on very different numeric scales. Chen and Guestrin's XGBoost, a gradient-boosted tree ensemble, is identified in the literature as a strong contemporary alternative worth benchmarking against Random Forests on structured, tabular prediction tasks of exactly this kind [13].

A second recurring theme is the handling of class imbalance, which is endemic to environmental hazard data: genuinely high-risk locations are, almost by definition, less common than low-risk ones. Tehrany et al. show that plain accuracy is an unreliable metric under this kind of imbalance, and recommend macro-averaged F1-score and Area Under the ROC Curve (AUC-ROC) as more informative primary evaluation metrics, since both remain sensitive to poor performance on a minority class in a way that overall accuracy does not [5].

A third theme, and the one most directly load-bearing for this project's design, is interpretability. Model interpretability is not merely a diagnostic convenience; it has direct implications for user trust and adoption, particularly where a model's output is meant to inform a member of the public's own decisions rather than only an expert analyst's. Lundberg and Lee's SHAP (SHapley Additive exPlanations) framework, grounded in cooperative game theory's Shapley values, has become the standard approach for explaining individual predictions from otherwise opaque tree-based models [14], and Lundberg et al.'s subsequent work extends this specifically to tree ensembles at scale, including guidance on interpreting SHAP output in raw margin space versus calibrated probability space — a distinction this project's own SHAP implementation (Chapter 3, Section 3.5) engages with directly, including a specific library-level limitation encountered when applying it to XGBoost's multiclass objective [15].

This project's use of machine learning also sits within a much broader movement, surveyed comprehensively by Rolnick et al., applying machine learning across the full span of climate change mitigation and adaptation problems — from emissions monitoring to renewable-grid optimisation to, as here, hazard prediction and risk communication [1]. That survey's broader argument, that machine learning's greatest near-term climate value often lies not in prediction accuracy alone but in making existing climate-relevant data more usable by the people and institutions who need it, is echoed closely by this project's own emphasis on communication and interpretability over incremental gains in raw predictive performance.

Where Random Forest and XGBoost specifically diverge, beyond raw accuracy, is in how directly each supports the interpretability requirement above. Random Forest's individual trees are grown independently on bootstrap samples and averaged, and — for classification — each leaf directly stores an empirical class-probability distribution; XGBoost instead grows trees sequentially, each correcting the residual error of the ensemble so far, with leaves storing additive log-odds-style margins rather than probabilities directly. This architectural difference, developed further as a concrete implementation finding in Chapter 3 (Section 3.4.5), turns out to have a direct, practical consequence for SHAP-based explanation specifically: it is what allows SHAP output to be transformed into calibrated probability space for a Random Forest but not, without additional approximation, for XGBoost's multiclass objective.

*Design link.* This body of literature directly justifies the project's primary model choice (Random Forest, benchmarked against XGBoost), its evaluation metrics (macro F1 and per-class precision/recall alongside accuracy, given the moderate class imbalance in the constructed flood-risk label), and its central design commitment to SHAP-based, per-prediction explainability rather than a global, static feature-importance chart alone.

## 2.3 Environmental Decision Support Systems

The decision-support-systems literature draws a sharp and consequential distinction between systems that *describe* a situation and systems that *prescribe* a course of action. Rizzoli and Young, reviewing experience across a range of environmental decision-support deployments, identify the shift from descriptive to prescriptive support as the central unresolved challenge in the field: the majority of tools facing the public remain descriptive, presenting risk maps or boundary layers without translating them into a recommended response [2]. Power and Sharda's broader treatment of decision support systems situates this challenge within a longer history of DSS design, reinforcing that the gap between presenting information and supporting an actual decision is a structural, recurring one rather than one specific to flood risk [3].

Design Science Research (DSR), as formalised by Hevner, March, Park and Ram, offers a methodological response to this challenge that this project adopts directly: a DSR study evaluates its central artefact — here, the dashboard itself — not solely on technical correctness, but on demonstrated usefulness and fit to the problem environment, assessed through structured evaluation with representative users [4]. This framing is precisely why the project's third research question concerns heuristic usability evaluation rather than only predictive accuracy, and why Chapter 3's account of the dashboard treats every design decision as something to be justified against the planned evaluation, not only against technical elegance.

Hevner et al.'s framework is specifically useful to this project because it separates two concerns this dissertation must satisfy simultaneously: a *rigor cycle*, grounding the artefact's construction in an existing knowledge base (the machine learning and interpretability literature of Section 2.2), and a *relevance cycle*, grounding the artefact's evaluation in the needs of its problem environment (the non-specialist users targeted by Section 2.5 and evaluated in Chapter 3, Section 3.7). A DSR study that satisfied only the rigor cycle — building a technically sound classifier without evaluating whether it is usable by its intended audience — would, on this framework's own terms, be an incomplete piece of design science, however strong its accuracy metrics; this is the specific methodological reason the usability evaluation in Section 3.7 is treated as integral to the project rather than as an optional final validation step appended after the "real" technical work was complete.

A parallel strand of literature addresses why descriptive tools persist despite this well-established critique. Biesbroek, Dupuis and Wellstead, examining climate adaptation governance more broadly, find that even well-resourced adaptation programmes routinely fail to convert technical outputs into behavioural change, specifically because they lack a communication layer designed for non-specialist audiences [6]. This project treats the construction of exactly that missing communication layer — not the underlying flood-risk model itself — as its central technical contribution.

*Design link.* This theme motivates the project's insistence on a prescriptive, not merely descriptive, output (the rule-based recommendation engine, Chapter 3, Section 3.6.3), and its adoption of Design Science Research as the overarching methodology governing how the dashboard is built and, subsequently, evaluated.

## 2.4 Geospatial Analysis for Urban Flood Risk

Urban flood-risk analysis characteristically requires integrating spatial data captured at markedly different scales and in different formats — precisely the challenge this project's own pipeline confronts, combining vector flood boundaries, vector infrastructure layers, a gridded elevation raster, and a gridded climate raster. Tomaszewski sets out both the technical requirements (consistent coordinate reference systems, resolved topological relationships between layers) and the cognitive requirements (that the integrated output remain interpretable to a non-specialist decision-maker, not only correctly computed) of this kind of multi-source spatial integration for disaster management applications specifically [7]. This project's early, explicit verification of coordinate reference systems across all four raw data sources, and its choice to model at a single regular 100-metre grid resolution rather than at the mismatched native resolutions of the source layers, are both direct responses to the technical half of this requirement.

The vector/raster distinction specifically is a recurring source of integration difficulty in this kind of pipeline, and is worth noting as a design consideration in its own right, separately from the coordinate-system issue. Vector sources (SEPA's flood boundaries, OSM's buildings, roads and water bodies) represent discrete features with exact geometry, naturally supporting operations such as exact containment ("is this point inside this polygon?") or precise distance-to-boundary calculation. Raster sources (the NASA elevation grid and the HadUK-Grid rainfall archive) instead represent a regularly sampled surface, for which the natural operation is nearest-cell lookup rather than exact containment, and for which the raster's native resolution imposes a hard lower bound on how much genuine spatial variation the resulting feature can carry, however fine a modelling grid is later built on top of it — a constraint this project encounters directly with its rainfall features (Chapter 3, Section 3.3) and reports transparently as a limitation (Section 3.8) rather than allowing the fine resolution of the modelling grid to imply a spatial precision the underlying raster data does not actually support.

On the presentation side, Singleton and Spielman's review of geodemographic research practice finds consistent evidence that interactive web maps improve public understanding of spatial information relative to static, printed equivalents [8], supporting this project's choice of an interactive, clickable Streamlit/Folium map — rather than a static risk-map image — as the dashboard's primary interface element.

*Design link.* This theme underlies the project's coordinate-reference-system discipline during data integration and its choice of an interactive rather than static map as the dashboard's central interaction surface.

## 2.5 Recommendation Systems and the Communication of Risk

Ricci, Rokach and Shapira's standard treatment of recommender systems distinguishes rule-based recommendation, in which the mapping between situation and recommendation is set directly by domain expertise, from content-based and collaborative-filtering approaches, which instead *learn* recommendations from historical item or user data [9]. For this project, a rule-based approach is judged the only appropriate choice: the correct response to a given flood-risk level is a matter of established civil-protection guidance, not of inferred individual preference, and no historical log of user interactions exists for a learned approach to train on in any case.

Two further findings from the risk-communication literature shape how that rule-based guidance, and the model's underlying risk classification, are actually presented to a user. Spiegelhalter's review of risk and uncertainty communication finds that non-experts systematically misread probabilistic outputs — treating a stated percentage risk as an implicit binary certainty — unless that output is presented with careful supporting context [10]. This finding is the direct justification for this project's decision to surface risk as a categorical Low/Medium/High label accompanied by plain-language explanation, rather than as a bare percentage probability. Renn's work on risk governance adds that risk communication is most effective when it connects aggregate risk information to a situation the recipient finds personally relevant, and when it is delivered by a source the recipient can trust [11] — a finding reflected directly in this project's decision to differentiate its recommendation content by risk class rather than issuing a single generic guidance list, and to cite every piece of guidance to its original authoritative source (SEPA, Ready Scotland) rather than presenting it as the dashboard's own unsupported advice.

Finally, Nielsen's ten usability heuristics provide the structured evaluation framework this project uses to assess the resulting interface [19], and Braun and Clarke's thematic-analysis method provides the qualitative analysis approach applied to the accompanying user walkthroughs [17] — both discussed further as evaluation methodology in Chapter 3, Section 3.7. Complementing Nielsen's heuristics, Shneiderman et al.'s broader treatment of human-computer interaction design strategy — consistency and standards, visibility of system status, recognition over recall, and graceful error handling among them — provides a second, more general lens against which the dashboard's concrete interface choices (a single fixed colour convention for risk level across every chart and marker; an always-visible confidence indicator; specific, actionable error messages on a failed postcode lookup) can be justified individually, not only assessed after the fact against Nielsen's ten headline categories [16]. Applying both frameworks together, rather than relying on Nielsen's heuristics alone, was a deliberate choice: Shneiderman et al.'s strategies are pitched at the level of concrete interface decisions during design, while Nielsen's heuristics are better suited to structured, retrospective evaluation of a finished interface — the two are complementary rather than redundant, and this project uses each for the purpose it is better suited to.

*Design link.* This theme directly shapes three concrete design decisions documented in Chapter 3: the rule-based (not learned) recommendation engine; the categorical, plain-language presentation of risk rather than raw probability; and the choice of Nielsen's heuristic framework, evaluated via thematic analysis of think-aloud walkthroughs, as the project's usability evaluation methodology.

## 2.6 Synthesis and Positioning of This Study

Read together, this literature establishes three things clearly. First, ensemble tree-based classifiers, evaluated with imbalance-aware metrics, are an appropriate and literature-supported choice for a flood-risk classification task of this kind, and SHAP is the corresponding standard for making such a model's predictions individually interpretable. Second, the decision-support-systems literature identifies the gap between descriptive and prescriptive tools as a long-standing, unresolved problem — one that a genuinely integrated system, rather than a purely predictive model, is needed to close. Third, the risk-communication and recommender-systems literature together specify *how* that prescriptive layer should be built: as a rule-based mapping, expressed in categorical rather than raw-probabilistic terms, and evaluated for comprehensibility with the non-specialist users it is intended for, not only for technical correctness.

No work identified in this review integrates all three elements — an evaluated classifier reconstructing an engineered flood-risk proxy label, attached per-prediction SHAP interpretability, and a rule-based, source-cited recommendation layer — inside one publicly accessible, interactively evaluated dashboard. This is the specific gap this project positions itself to address, and Chapter 3 documents the system built in direct response to it.

Table 2.1 summarises this positioning directly, mapping each of the five themes reviewed above to the specific project decision it grounds, and forward to the section of Chapter 3 where that decision is documented in full.

**Table 2.1 — Literature themes and their corresponding project design decisions**

| Literature theme | Key sources | Project design decision | Documented in |
|---|---|---|---|
| ML for flood-risk prediction | [5], [12], [13] | Random Forest primary model, benchmarked against XGBoost; macro F1/per-class metrics | §3.4 |
| Model interpretability | [14], [15] | Live, probability-space SHAP explanation per prediction | §3.5 |
| Environmental DSS theory | [2], [3], [6] | Prescriptive, not merely descriptive, dashboard output | §3.6.3 |
| Design Science Research | [4] | Artefact-plus-evaluation methodology governing the whole project | §3.7 |
| Geospatial data integration | [7] | Explicit CRS verification; single regular modelling grid | §3.2, §3.3 |
| Interactive cartography | [8] | Interactive Folium map, not a static risk image | §3.6 |
| Recommender systems | [9] | Rule-based, not learned, recommendation engine | §3.6.3 |
| Risk communication psychology | [10], [11] | Categorical risk labels; differentiated, source-cited guidance | §3.5, §3.6.3 |
| Usability evaluation | [16], [17], [19] | Nielsen heuristics + thematic analysis of think-aloud walkthroughs | §3.7 |

---

# Chapter 3: System Development and Evaluation

## 3.1 Introduction

This chapter documents the system built in response to the research gap identified in Chapter 2, structured around the five-layer architecture proposed at the project's outset — data sources, data pipeline, ML modelling, recommendation engine, and dashboard output. Section 3.2 describes the study area and the four raw data sources. Section 3.3 details the feature-engineering pipeline. Section 3.4 covers the training and evaluation of the Random Forest classifier, including a comparison against XGBoost and a comparison of two rainfall-climatology windows. Section 3.5 describes the SHAP explainability layer. Section 3.6 documents the dashboard itself, including its recommendation engine and the two versions built for the planned usability study. Section 3.7 sets out that evaluation's design, and Section 3.8 discusses the system's limitations transparently before Section 3.9 closes the chapter.

## 3.2 Study Area and Data Sources

### 3.2.1 Study area

The system is scoped to a 5 km radius circle centred on the University of Strathclyde (easting 260,983, northing 665,006, EPSG:27700) — an area that is simultaneously data-rich, relevant to the project's initial intended user base, and genuinely flood-exposed, with the River Clyde running directly through it. All spatial processing is carried out in EPSG:27700 (British National Grid, in metres); conversion to WGS84 latitude/longitude is deferred to the map-rendering layer only, avoiding the distance and area distortion that an unprojected coordinate system would otherwise introduce into every buffer and distance calculation in the pipeline.

### 3.2.2 Data sources

Four open datasets, illustrated in Figure 3.1 and Figure 3.2, are combined, each distributed at a different native scale, format and coordinate convention.

**SEPA's Potentially Vulnerable Areas (PVA)** dataset identifies 235 flood-vulnerable zones nationally, distributed as a GeoPackage in EPSG:27700, with a mean zone area of 59.4 km² and zero missing values across its eight columns. Intersecting the national layer with the 5 km study buffer isolates seven Glasgow zones — River Kelvin (by far the largest, at 186.0 km², reflecting its role as a national-scale catchment designation rather than a strictly local one), Glasgow City centre (4.3 km²), Glasgow City north (24.7 km²), Luggie Water catchment (112.7 km²), East of Glasgow to Strathaven (150.2 km²), Rutherglen (12.4 km²), and White Cart Water catchment (209.2 km²) — which together form the spatial basis of the flood-risk label constructed in Section 3.3.

**OpenStreetMap** contributes three separate extracts. The buildings layer contains 55,638 features across 91 distinct building types, dominated by unclassified "yes" tags (28,798), "house" (10,344), "residential" (6,269) and "apartments" (5,427); secondary attributes such as building height are populated for under 1% of records, which is immaterial since the pipeline uses only feature location, not these attributes. The roads layer contains 38,218 features across 37 highway types, dominated by footways (9,437), service roads (7,927) and residential roads (5,133). The water layer is much smaller — 195 polygon features, only 34 of them named — but includes the three polygons tagged "River Clyde" that, merged into a single 217.7-hectare geometry, become the basis of the `dist_to_clyde` feature discussed in Section 3.2.3.

**NASA SRTM elevation** provides 259,200 point measurements across the wider Glasgow area, ranging from −23 m to 132 m (mean 41.6 m, median 35.0 m); 282 points fall below sea level, reflecting the low-lying reclaimed land characteristic of the lower Clyde valley. Two thresholds identified during exploratory analysis, 15 m and 35 m, later become the elevation cut-points in the risk-labelling rule (Section 3.3): 17.4% of all elevation points sit at or below 15 m, and 50.2% sit at or below 35 m, confirming both thresholds bisect the distribution at points with a meaningful population on either side.

**Met Office HadUK-Grid daily rainfall** required combining two archives — 431 files (1987–2022) and 36 files (2023–2025), 467 in total, first confirmed to share an identical raster structure and fill value before being concatenated — into one continuous 39-year daily series, yielding 111,480,402 daily observations once extracted to the study grid and stored as a 182.6 MB Parquet file for aggregation.

![Figure 3.1 — SEPA Potentially Vulnerable Area zones within the 5 km Glasgow study circle (red dashed boundary), coloured by zone, with the University of Strathclyde marked as the study centre.](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/eda_sepa_pva.png){width=85%}

![Figure 3.2 — NASA SRTM elevation across the wider Glasgow area: distribution (left, with the 15 m and 35 m risk-labelling thresholds marked) and spatial map (right).](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/eda_elevation.png){width=90%}

### 3.2.3 Exploratory findings shaping feature design

Exploratory correlation analysis found that distance to the River Clyde specifically was a substantially stronger flood-risk correlate than distance to the nearest water body of any kind ($r = -0.74$ versus $r = -0.28$) — an unsurprising result for Glasgow, where the Clyde is the dominant flood driver and a generic water-proximity measure is diluted by many small, hydrologically minor ponds and burns. This directly motivated engineering `dist_to_clyde` as a feature distinct from the more general `dist_to_water`, a decision later confirmed in the trained model, where `dist_to_clyde` emerges as the second most important predictor by a wide margin (Section 3.4.4). A post-hoc sanity check confirmed the two distance features are not redundant duplicates of one another: 1,426 of 7,843 points (18.2%) have identical values for both (points whose nearest water feature of any kind *is* the Clyde), but the two columns correlate only weakly overall ($r = 0.25$), confirming most of the study area's water-proximity signal comes from features other than the Clyde.

### 3.2.4 Coordinate reference system alignment

The project's risk and contingency plan identified coordinate-reference-system discrepancy across data sources as a medium-likelihood, high-impact risk, to be mitigated by testing every spatial join early rather than discovering a silent alignment failure once feature engineering was already underway. This risk was concrete, not theoretical: the four sources arrive in genuinely different native formats — SEPA and both OSM extracts as EPSG:27700 GeoPackages directly; the NASA elevation extract with its reprojected geometry column checked, not assumed, to already be in EPSG:27700; and the HadUK-Grid archive as NetCDF rasters carrying their own projection dimensions, confirmed identical across all 467 files before being treated as one continuous grid (Section 3.2.2). Each source's coordinate system was verified explicitly before use in any join, buffer or distance calculation, and every join was checked on a small sample before being run across the full 7,843-point grid — a discipline attributed directly to why no coordinate misalignment issues were in fact encountered during development.

## 3.3 Feature Engineering Methodology

### 3.3.1 Study grid and terrain/proximity features

A regular grid of points spaced 100 m apart is generated across the bounding square of the 5 km study radius, then filtered to points within 5,000 m of the university centre point, producing a circular, not square, coverage area of 7,843 points — the fixed unit of analysis for every downstream step in the pipeline, from exploratory analysis through to live dashboard inference. **Elevation** is attached to each point via a GeoPandas nearest-neighbour spatial join against the NASA SRTM extract (zero missing values after the join; grid-level elevation ranges from −15 m to 127 m, mean 42.1 m). **Distance to water** (`dist_to_water`) is the Euclidean distance from each point to the boundary of all 195 OSM water polygons merged into a single geometry (0 m to 2,258.8 m, mean 506.7 m). **Distance to the River Clyde** (`dist_to_clyde`) is computed identically but against the three Clyde-tagged polygons merged separately (0 m to 6,161.5 m, mean 2,094.6 m), following the exploratory finding in Section 3.2.3 that this Clyde-specific measure carries substantially more flood-risk signal than the general water-proximity measure.

### 3.3.2 Built-environment density features

**Building count** and **road count** within 250 m of each point capture the intuition that dense, impermeable, built surfaces drain more poorly than open ground, independent of elevation or river proximity. Both are computed via a two-stage process — a spatial-index bounding-box shortlist, then an exact geometric containment test against a 250 m buffer — necessary for tractability given the underlying dataset sizes (55,638 building features, 38,218 road features), with each full pass across all 7,843 grid points taking approximately two to three minutes. Building counts range from 0 to 419 (mean 92.0); road counts range from 0 to 680 (mean 60.2).

### 3.3.3 Rainfall climatology features

Four rainfall features are aggregated from the 111.5-million-row daily rainfall table (Section 3.2.2): **mean annual rainfall** (the simple mean of daily rainfall across the full 39-year record); **mean winter rainfall** (the same mean, restricted to December–February); **wet days per year** (the count of days meeting a ≥ 1.0 mm threshold, established during exploratory analysis of the original 3-year rainfall window, computed per calendar year and averaged across all 39 years); and **average annual peak daily rainfall** (the mean, across all 39 years, of each individual year's single wettest day — deliberately not the all-time maximum, so that one exceptional storm year does not dominate what is meant to represent a *typical* annual extreme). After aggregation, these four features show a notably narrow spatial range across the 7,843 points (mean annual rainfall from 2.71 to 3.08 mm/day; wet days from 165 to 176 per year), a direct consequence of HadUK-Grid's native 5 km raster resolution meaning many nearby grid points share an identical nearest raster cell — a limitation returned to in Section 3.8.

### 3.3.4 Flood risk label construction

The target variable, `flood_risk`, is a three-class label combining SEPA PVA zone membership with elevation:

$$
\text{flood\_risk} =
\begin{cases}
2 \ (\text{High})   & \text{if inside a PVA zone AND elevation} \le 15\text{m} \\
1 \ (\text{Medium}) & \text{if inside a PVA zone AND elevation} \le 35\text{m} \\
0 \ (\text{Low})    & \text{otherwise}
\end{cases}
$$

PVA membership is determined by an exact within-polygon spatial join against the seven Glasgow zones (Section 3.2.2). This rule encodes a specific, defensible hydrological intuition rather than an arbitrary threshold: SEPA's own designation already identifies *where* flooding is plausible from any source, and elevation refines *how severe* that plausible risk is likely to be — low-lying land inside a vulnerable zone is treated as categorically worse than moderately elevated land in the same zone, and land outside any vulnerable zone is treated as low risk regardless of elevation. Applied across the full grid, this produces a class split of 3,790 Low (48.3%), 2,698 Medium (34.4%) and 1,355 High (17.3%) points — a moderate imbalance that motivates the use of macro-averaged, not only overall, evaluation metrics in Section 3.4. Figure 3.3 summarises the resulting feature matrix; it contains zero missing values across all columns, a direct consequence of every attachment step above using nearest-neighbour or containment-based joins, which always return a value, rather than exact-match joins, which can fail to.

![Figure 3.3 — Feature-engineering summary: risk-class distribution, elevation and Clyde-distance by class, feature correlation with flood risk, the resulting risk map, and rainfall variation across the study grid's raster cells.](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/feature_engineering_summary.png){width=95%}

## 3.4 Predictive Model Development

### 3.4.1 Model choice and training

Consistent with the literature reviewed in Section 2.2, a Random Forest classifier (`n_estimators=100`, `random_state=42`) was trained as the primary model, with XGBoost retained as a benchmark comparison rather than a candidate replacement. The nine-feature matrix was split 80/20 (stratified, `random_state=42`) into 6,274 training and 1,569 held-out test points, preserving the class proportions above exactly in both partitions.

### 3.4.2 Results

On the held-out test set, the Random Forest achieved 99.62% accuracy, 99.50% macro F1, and 99.62% weighted F1. Table 3.1 gives the per-class breakdown; Figure 3.4 shows the resulting confusion matrix, in which only six of 1,569 test points are misclassified, all of them Low↔High confusions — the model shows no confusion at all between Medium risk and either neighbouring class. Five-fold stratified cross-validation across the full dataset gave a mean accuracy of 99.26% (± 0.17%) and mean macro F1 of 99.04% (± 0.22%), confirming this is not an artefact of a favourable train/test split; mean one-vs-rest ROC-AUC (Figure 3.5) was 0.9998.

**Table 3.1 — Random Forest test-set performance by class**

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Low risk | 0.996 | 0.996 | 0.996 | 758 |
| Medium risk | 1.000 | 1.000 | 1.000 | 540 |
| High risk | 0.989 | 0.989 | 0.989 | 271 |

![Figure 3.4 — Random Forest confusion matrix on the held-out test set.](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/confusion_matrix.png){width=55%}

![Figure 3.5 — One-vs-rest ROC curves per risk class.](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/roc_curves.png){width=65%}

This near-ceiling accuracy warrants a direct methodological caveat, developed further in Section 3.8: because the label is itself constructed deterministically from elevation and PVA membership — two quantities closely related to several of the model's own inputs — a substantial share of this performance reflects the classifier recovering a known, defensible labelling rule from continuous inputs, rather than validating against independently observed historical flood outcomes.

This does not invalidate the exercise — the classifier still has to learn the correct elevation thresholds and combine them correctly with proximity information from continuous, unthresholded inputs, and the resulting model is exactly what the SHAP explainability layer (Section 3.5) needs to produce model-faithful, probability-space attributions for each proxy-risk classification — but it should be read as a system that faithfully reconstructs a defensible, literature-grounded risk-labelling rule, rather than as a model independently validated against observed historical flood outcomes.

### 3.4.3 Spatial-block validation

The random 80/20 split and five-fold cross-validation reported in Section 3.4.2 both partition the data point-by-point, which leaves open a specific concern given the study grid's 100 m spacing: neighbouring points are spatially autocorrelated (Section 3.8), so a random split can place near-duplicate points on both sides of the train/test boundary, potentially inflating the reported score relative to how the model would generalise to a genuinely unseen area. To test whether the random split was materially affected by spatial dependence between nearby 100 m grid points, a second five-fold GroupKFold evaluation withheld complete 500 m spatial tiles. This produced mean accuracy of 99.21% (±0.36%) and mean macro F1 of 98.97% (±0.47%), compared with 99.26% (±0.17%) and 99.04% (±0.22%) under random stratified cross-validation. At the tested 500 m block scale, the similar results suggest that local spatial dependence does not materially alter performance for reconstruction of the engineered label; they do not validate prediction against observed flood outcomes. This spatial-block comparison is also surfaced live in Version B's Model evaluation tab, alongside the same caveat.

### 3.4.4 Feature importance

Feature importance (Table 3.3, visualised in Figure 3.6) confirms the exploratory finding from Section 3.2.3: elevation dominates at 62.9%, with `dist_to_clyde` a clear second at 17.2%; the remaining seven features each contribute under 6% individually, with the four rainfall features and the two infrastructure-density features clustered in a long tail.

**Table 3.3 — Random Forest feature importance (Gini-based)**

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

![Figure 3.6 — Random Forest feature importance.](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/feature_importance.png){width=75%}

### 3.4.5 Comparison against XGBoost, and against the original 3-year rainfall model

An XGBoost classifier trained on an identical split achieved 99.36% accuracy and 99.17% macro F1 — consistently, if marginally, below the Random Forest (Table 3.2). Native feature-importance rankings agree closely between the two models (elevation dominant in both, `dist_to_clyde` second in both by native importance), but their SHAP rankings diverge somewhat for `dist_to_clyde` specifically, which is attributable in part to a genuine library limitation: SHAP's `TreeExplainer` supports calibrated probability-space output for the Random Forest directly, but has no equivalent transform for XGBoost's multiclass objective, so the two models' SHAP magnitudes — though not their rankings — are not directly comparable. Combined with this probability-space support, which the live dashboard explanation panel depends on directly, the Random Forest was retained as the sole live model.

**Table 3.2 — Random Forest vs XGBoost, and vs the original 3-year-rainfall model**

| Metric | RF (39yr, primary) | XGBoost (39yr) | RF (3yr rainfall) |
|---|---:|---:|---:|
| Accuracy | 99.62% | 99.36% | 99.55% |
| F1 macro | 99.50% | 99.17% | 99.42% |

A separate comparison, retraining the identical pipeline against a frozen 3-year-rainfall (2023–2025) feature snapshot, shows the 39-year climatology rework produced a small, consistent accuracy and F1 improvement (Table 3.2, right column) — a modest gain given how dominant elevation already is, but one that also makes the resulting rainfall features substantively more defensible as representing *typical*, rather than merely recent, conditions.

## 3.5 Explainability: SHAP Analysis

### 3.5.1 Global explanation

Model interpretability is treated in this project not as an optional diagnostic but as a design requirement directly serving the research aim (Section 1.3): a black-box risk score, however accurate, does nothing to close the communication gap motivating this project unless a user can also see *why* their location was scored as it was. Following the interpretability literature reviewed in Section 2.2, a `TreeExplainer` was fitted to the trained Random Forest and SHAP values computed for a fixed random sample of 500 held-out test points, reused consistently across every SHAP output for comparability. Figure 3.7 shows the resulting per-class summary plots, confirming at the distributional level what Section 3.4.4's aggregate Gini importances already showed at the single-number level: elevation dominates every class's explanation, with `dist_to_clyde` a consistent second contributor.

![Figure 3.7 — SHAP summary plots by risk class (500-point test sample).](/Users/riteshghorpade/Documents/010_Project/002_Dataset/004_Maps/shap_summary.png){width=95%}

### 3.5.2 Local explanation and probability-space calibration

Beyond this aggregate view, individual waterfall explanations (Figure 3.8) were generated for representative points in each risk class — selected as the test-sample point with the model's single highest predicted probability for that class. Two versions of these explanations were produced: one in the Random Forest's raw, additive output space, and a second using an explainer rebuilt with `model_output="probability"` against the model's own training partition as background. This second, probability-space configuration is the one carried into the live dashboard, decomposing a predicted class *probability* — a quantity a non-specialist user can interpret directly, e.g. "this pushed the High-risk probability up by twelve percentage points" — rather than an internal model score, and is a direct response to Spiegelhalter's finding (Section 2.5) that raw probabilistic output is easily misread as false certainty without careful presentation.

![Figure 3.8 — SHAP waterfall explanation (probability space) for a representative High-risk point.](/Users/riteshghorpade/Documents/010_Project/003_Code/shap_waterfall_high_risk_proba.png){width=70%}

### 3.5.3 Live, per-point computation

A key implementation finding, reported here because it directly shaped the dashboard's architecture, is that this probability-space SHAP computation is fast enough to run live, on demand, rather than requiring precomputation: building the explainer takes approximately 2 ms, and computing SHAP values for a single selected point takes approximately 5–10 ms. Both figures sit well under the 1–2 second threshold generally considered acceptable for an interactive UI response, and this benchmark is the reason no SHAP values are precomputed or cached anywhere in the dashboard beyond the explainer object itself: every map click or postcode search triggers a fresh, exact SHAP computation for that specific location, guaranteeing the explanation shown always corresponds precisely to the currently selected point's exact feature values.

## 3.6 Dashboard Design and Implementation

### 3.6.1 Architecture

The dashboard is implemented in Streamlit, with `folium`/`streamlit_folium` for the interactive map, `pyproj` for coordinate transformation between the pipeline's native EPSG:27700 and the WGS84 latitude/longitude required by web-map tiles, and the free `postcodes.io` API for postcode search. The trained model and feature matrix are loaded once at startup, with predictions and confidence scores (`model.predict`/`model.predict_proba`) computed for all 7,843 points and cached, so map rendering and filtering require no repeated inference. Two caching mechanisms are used deliberately: `st.cache_data` for expensive-but-serialisable results (the loaded feature matrix, derived latitude/longitude, feature terciles for the SHAP panel's plain-English tiering), and `st.cache_resource` for the model and SHAP `TreeExplainer` objects themselves, since a fitted Random Forest cannot be safely hashed or copied the way a dataframe can. Per-user interaction state — which point is selected, whether via map click or postcode search, and the active filter values — is held in Streamlit's `session_state`, persisted across the framework's rerun-on-interaction execution model.

### 3.6.2 Build history and two evaluation versions

The dashboard was built incrementally rather than as a single monolithic implementation. An initial version confirmed the core click-to-inspect map interaction using a precomputed risk label with no live inference, to test the interaction design before adding modelling complexity. A second stage introduced genuine live model inference, postcode search (resolving to the nearest grid point), and a compass indicator reporting direction and distance to both the River Clyde and the university. Two final versions were then built directly on top of this stage for the planned usability comparison. A later simplification pass, driven by the principle that the two versions should differ only in what is genuinely under test and not incidentally, brought the shared feature set to near-parity. Both versions now present: the postcode search, alongside a privacy notice explaining that a searched postcode is sent only to the free `postcodes.io` lookup service and is not stored by the dashboard itself; a single merged "browse a district or landmark" control, collapsed from two separate dropdowns that had previously competed with the primary postcode search for attention; a "Reset search and filters" control; a "What should I do now?" orientation panel directing a user to SEPA's official maps and Floodline before anything else; the risk badge, classification confidence, nearest SEPA flood zone, the compass indicator, and a set of "more about this location" context cards; the recommendation engine (Section 3.6.3); a caveat noting that results represent the nearest 100 m grid point rather than an exact property-level assessment; and an explicit disclaimer that the dashboard's outputs are research classifications, not validated predictions of real-world flooding or an official flood risk assessment.

**Version A** adds nothing beyond this shared set. **Version B** adds exactly three things: a live SHAP explanation panel (Section 3.6.3); a "Why am I seeing this result?" control next to the risk badge that jumps directly to that panel; and a separate "Model evaluation" tab, explicitly labelled a technical dashboard, surfacing the Section 3.4 results (accuracy, F1, random and spatial-block cross-validation, ROC-AUC, feature importance and the SHAP summary) directly within the application rather than only in this report. Both versions also share a sidebar risk-distribution summary across all 7,843 points, a 39-year rainfall-trend comparison (annual totals essentially flat across the two halves of the HadUK-Grid record, up only around 2%, with wet-day frequency and peak daily rainfall both slightly down — the record does not itself show a clear directional trend), and two fixed markers for documented historical flood events — the 2002 Glasgow East End floods (approximately 75 mm of rain in ten hours overwhelming Victorian-era storm drains, around 200 people evacuated) and the 1994 SEC Centre floods (the River Kelvin bursting its banks via old railway tunnels, two fatalities, over £100 million in damage) — styled distinctly from model output and shown as passive map context rather than a filterable or comparable dimension (Section 3.6.4), so a user cannot mistake historical record for live prediction.

### 3.6.3 SHAP explanation and recommendation engine

Version B's "Why this prediction?" panel is the user-facing implementation of Section 3.5: a one-sentence plain-English narrative naming the top one or two driving features, an explicit plain-language caveat directly above the chart — "These bars show what influenced this model classification. They do not prove what caused flooding." — then a diverging horizontal bar chart ranking all nine features by SHAP contribution (red pushing risk up, blue pushing risk down, against a zero baseline), and inline plain-English definitions for the top two features, with the remaining seven available behind a collapsed control. Every numeric feature value is tiered (low/moderate/high, by that feature's tercile across the full dataset) and translated into a plain-English label, so an elevation value is shown as "Low elevation" rather than a bare metre figure. A "Why am I seeing this result?" control sits next to the risk badge on the Overview tab (Section 3.6.2) and jumps directly to this panel, so the explanation is never more than one click away from the prediction it explains.

Directly beneath it sits the recommendation engine — the fourth layer of the system architecture (Section 3.1), and one of the project's four named deliverables. Consistent with the rule-based design justified in Section 2.5, this is a deterministic, source-cited mapping from each of the three risk classes to differentiated guidance (cited to SEPA and Ready Scotland, not presented as the dashboard's own advice), rather than a single list reused across all three classes at only cosmetic difference in urgency: High-risk guidance centres on checking SEPA's official maps, registering with Floodline (SEPA's 24-hour flood-warning phone service, number displayed directly), considering flood-resilience measures via the Scottish Flood Forum, and discussing insurance including Flood Re; Medium-risk guidance is a precautionary version of the same content; Low-risk guidance is deliberately different in kind rather than degree, noting that a Low classification for the property does not guarantee unaffected roads or transport access, and framing map-checking around business or long-term investment planning rather than immediate personal risk. This ordering — explanation immediately before recommendation — is deliberate, intended to build the recommendation's perceived legitimacy on the explanation that precedes it, and is the basis on which RQ2 will be assessed (Section 3.7).

### 3.6.4 Filtering, comparisons, and interface principles

Both versions support combinable filtering across seven dimensions simultaneously (risk level, Clyde distance, postcode district, elevation, minimum confidence, building/road density, and rainfall pattern — wet days per year and peak daily rainfall), applied as a single joint boolean mask so a user can, for example, restrict the map to high-confidence, High-risk predictions in one district. An earlier iteration also filtered by proximity to the two historical flood events; this was removed in the simplification pass introduced in Section 3.6.2, since it added a filtering dimension most users did not need alongside the seven retained above — the two events remain visible as passive, always-on map markers (Section 3.6.2), but no longer participate in the filter mask. A separate "Comparisons" tab in an earlier iteration of Version B additionally offered a postcode-district risk-composition table, a confidence histogram, and ranked bar charts for districts and individual points by risk; these were removed in the same pass, since they did not match Version A and were not essential technical detail, so that the only structural difference between the two versions is the content named in Section 3.6.2. The one aggregate view judged worth retaining — a risk-versus-elevation scatter across all 7,843 points, which visually reinforces the Section 3.4.4 feature-importance finding — was relocated into Version B's Model evaluation tab as supporting technical detail rather than kept as user-facing comparison content.

Interface design follows the human-computer-interaction strategies reviewed in Section 2.5 directly [16]: a single colour convention (Low `#639922`, Medium `#EF9F27`, High `#E24B4A`) is used identically across every chart, marker and badge in both versions, so a user never has to re-learn what a colour means between views; model confidence is always visible alongside a prediction via a progress-bar indicator; the same postcode-search-then-inspect interaction pattern occupies the same screen position across both versions; postcode search fails gracefully — invalid postcodes, network failures, and postcodes resolving implausibly far from the study area are each caught and reported with a specific, actionable message rather than allowed to fail silently or crash the application; and the merged district/landmark dropdown and the "Reset search and filters" control (Section 3.6.2) apply Shneiderman et al.'s emphasis on reducing incidental choice and supporting easy reversal of actions, respectively.

## 3.7 Usability Evaluation Design

As set out in Section 2.3, the dashboard's value is to be assessed principally through demonstrated usability with representative non-expert users, evaluated against Nielsen's ten usability heuristics [19] on a 0–4 severity scale, alongside qualitative notes captured during participant sessions. This evaluation had not yet been conducted at the time of writing this chapter, so what follows documents the planned design rather than reported results, which will be presented in the following chapter.

**Participants.** A convenience sample of three to five participants will be recruited from the university community, deliberately selected to have no background in flood risk assessment or data science, so the evaluation reflects the system's intended non-specialist audience rather than a technically literate one. Nielsen's own methodological work indicates three to five evaluators are sufficient to surface approximately 75% of usability issues in a system of this scale, while explicitly not supporting statistically generalisable conclusions — a limitation this project accepts, given its scope, and reports transparently rather than overstating the evaluation's external validity.

**Procedure.** Each participant will complete a guided, task-based walkthrough (for example: find the flood risk level at a given postcode, and identify what the dashboard recommends doing about it) under a concurrent think-aloud protocol, audio-recorded with explicit informed consent, conducted individually to avoid participants influencing one another's responses.

**Analysis.** Transcripts and think-aloud notes will be analysed using Braun and Clarke's thematic analysis method [17], with codes generated inductively from the walkthrough data rather than from a predetermined coding frame, allowing genuinely unanticipated usability issues to surface.

**Research questions addressed.** This design targets RQ2 directly, via think-aloud commentary specifically around the recommendation and SHAP explanation panels, and RQ3 directly, via the structured Nielsen score sheet.

**Ethics.** No participant activity will be conducted before written approval from the University's Departmental Ethics Committee. Every participant will receive a Participant Information Sheet and provide informed consent before their session begins. All environmental data used elsewhere in the system is open-access and contains no personally identifiable information; the only personal data collected at any stage is the session recordings and transcripts, handled under the approved protocol.

## 3.8 Limitations and Threats to Validity

**Label construction and apparent accuracy.** The near-ceiling test accuracy reported in Section 3.4.2 should be read as the classifier successfully recovering a deterministic, literature-grounded labelling rule from continuous inputs, not as validation against independently observed flood outcomes, since the label is itself partly derived from the model's own input features (elevation directly, and PVA membership closely correlated with the two distance features).

**Spatial autocorrelation and rainfall resolution.** The 100 m study grid is considerably finer than HadUK-Grid's native 5 km resolution, so nearby points frequently share an identical nearest rainfall raster cell — an accurate reflection of the underlying data's true spatial resolution, not an engineering error, but one that limits how much genuine spatial variation the rainfall features can carry relative to elevation and the two distance features.

**Single-city scope.** The system is scoped to one 5 km radius around one Scottish city, by deliberate design choice made to keep the project attainable within a twelve-week timeframe, and its trained thresholds, labelling rule and historical-event context are specific to Glasgow and should not be assumed to transfer elsewhere without re-fitting against local topography and hydrology.

**Batch, not real-time, data.** All environmental inputs are static snapshots; elevation, infrastructure counts and the rainfall climatology do not update automatically as new source data becomes available, so predictions reflect each source's state at collection time rather than a continuously current picture.

**XGBoost SHAP comparability.** As reported in Section 3.4.5, the SHAP comparison between the two models is valid only at the level of feature ranking, not magnitude, owing to a library-level constraint on probability-space explanation for XGBoost's multiclass objective — disclosed prominently rather than smoothed over.

**Usability evaluation sample size.** The planned three-to-five-participant convenience sample (Section 3.7), while methodologically appropriate for exploratory heuristic evaluation at this project's scale, does not support statistically generalisable usability claims, and any findings should be read as indicative rather than conclusive.

**Accessibility of explanation charts.** The SHAP and model-evaluation visualisations are rendered as static images, not accessible, screen-reader-navigable chart elements; colour and position encode meaning, and while every chart is paired with an equivalent plain-text sentence specifically so the core finding is never conveyed by colour alone, a user relying on assistive technology cannot currently interrogate the chart itself — a genuine limitation, not a considered trade-off, and a direction for future work.

## 3.9 Chapter Summary

This chapter has documented the system built in direct response to the gap identified in Chapter 2, organised around the five-layer architecture proposed at the project's outset: a data pipeline combining four open datasets (SEPA flood boundaries, OSM buildings/roads/water, NASA elevation, and 39 years of HadUK-Grid rainfall) into a 7,843-point, nine-feature dataset over a defensible flood-risk label (Sections 3.2–3.3); a Random Forest classifier reaching 99.62% test accuracy and 99.50% macro F1, evaluated using random and spatial-block cross-validation and benchmarked directly against XGBoost (Section 3.4); a live, probability-space SHAP explainability layer computing calibrated per-prediction explanations in single-digit milliseconds (Section 3.5); a differentiated, source-cited recommendation engine translating each predicted risk class into personally relevant guidance (Section 3.6.3); and two parallel dashboard versions, differing specifically in whether they expose that SHAP and recommendation content, built to support a structured heuristic usability comparison (Section 3.6).

Together, these five components instantiate directly the four-part contribution claimed in Chapter 1: an evaluated classifier reconstructing an engineered flood-risk proxy label, attached SHAP interpretability, a rule-based recommendation layer, and an interactive dashboard artefact ready for formal evaluation. Section 3.8's transparent account of this system's limitations — above all, the extent to which its headline accuracy reflects the model recovering a known labelling rule rather than validating independently against observed real-world flood outcomes — is deliberately not relegated to a brief closing caveat, since how confidently a reader treats the results in the following chapter depends directly on understanding what, precisely, that 99.62% figure does and does not demonstrate. RQ1 (Section 1.3), concerning the model's predictive accuracy and its dominant environmental predictors, is accordingly answered by this chapter with that caveat attached; RQ2 and RQ3, concerning the comprehensibility of the recommendation engine and the dashboard's overall usability, remain open questions that only the evaluation reported in the next chapter can answer. That chapter presents the usability evaluation itself — its execution against the design set out in Section 3.7, its findings, and their implications for the project's three research questions read together.

---

## References

[1] D. Rolnick et al., "Tackling climate change with machine learning," *ACM Computing Surveys*, vol. 55, no. 2, pp. 1–96, 2022. doi: 10.1145/3485128

[2] A. Rizzoli and W. Young, "Delivering environmental decision support systems: Experience and challenges," *Environmental Modelling & Software*, vol. 12, no. 2–3, pp. 237–247, 1997. doi: 10.1016/S1364-8152(97)00016-9

[3] D. J. Power and R. Sharda, "Decision support systems," in *Springer Handbook of Automation*, Springer, Berlin, 2009, pp. 1521–1536. doi: 10.1007/978-3-540-78831-7_87

[4] A. R. Hevner, S. T. March, J. Park and S. Ram, "Design science in information systems research," *MIS Quarterly*, vol. 28, no. 1, pp. 75–105, 2004. doi: 10.2307/25148625

[5] M. S. Tehrany, B. Pradhan and M. N. Jebur, "Flood susceptibility mapping using a novel ensemble weights-of-evidence and support vector machine models in GIS," *Journal of Hydrology*, vol. 512, pp. 332–343, 2014. doi: 10.1016/j.jhydrol.2014.03.008

[6] R. Biesbroek, J. Dupuis and A. Wellstead, "Explaining through causal mechanisms: resilience and governance of social-ecological systems," *Current Opinion in Environmental Sustainability*, vol. 28, pp. 64–70, 2017. doi: 10.1016/j.cosust.2017.07.007

[7] B. Tomaszewski, *Geographic Information Systems (GIS) for Disaster Management*. CRC Press, 2015. doi: 10.4324/9781315770635

[8] A. Singleton and S. Spielman, "The past, present, and future of geodemographic research in the United States and United Kingdom," *The Professional Geographer*, vol. 66, no. 4, pp. 558–567, 2014. doi: 10.1080/00330124.2013.837591

[9] F. Ricci, L. Rokach and B. Shapira, "Recommender systems: Introduction and challenges," in *Recommender Systems Handbook*, Springer, 2015, pp. 1–34. doi: 10.1007/978-1-4899-7637-6_1

[10] D. Spiegelhalter, "Risk and uncertainty communication," *Annual Review of Statistics and Its Application*, vol. 4, pp. 31–60, 2017. doi: 10.1146/annurev-statistics-010814-020148

[11] O. Renn, *Risk Governance: Coping with Uncertainty in a Complex World*. Earthscan, London, 2008. ISBN: 978-1-84407-291-0

[12] L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001. doi: 10.1023/A:1010933404324

[13] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 2016, pp. 785–794. doi: 10.1145/2939672.2939785

[14] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017.

[15] S. M. Lundberg et al., "From local explanations to global understanding with explainable AI for trees," *Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, 2020. doi: 10.1038/s42256-019-0138-9

[16] B. Shneiderman, C. Plaisant, M. Cohen, S. Jacobs, N. Elmqvist and N. Diakopoulos, *Designing the User Interface: Strategies for Effective Human-Computer Interaction*, 6th ed. Pearson, 2017. ISBN: 978-0134380391

[17] V. Braun and V. Clarke, "Using thematic analysis in psychology," *Qualitative Research in Psychology*, vol. 3, no. 2, pp. 77–101, 2006. doi: 10.1191/1478088706qp063oa

[18] SEPA, "Flood maps for Scotland," Scottish Environment Protection Agency, 2023. Available: https://www.sepa.org.uk/hazards/flood-risk/

[19] J. Nielsen, *Usability Engineering*. Morgan Kaufmann, San Francisco, 1994. ISBN: 978-0125184069
