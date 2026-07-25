# Research basis

This document separates source claims from the design synthesis in this repository. Primary/open engineering publications are preferred. Older systems are used for enduring architecture principles, not as claims about their owners’ current implementations.

## Evidence table

| ID | Source | Explicit evidence used | Limits / interpretation |
|---|---|---|---|
| R1 | Google, *Overlapping Experiment Infrastructure: More, Better, Faster Experimentation* | Defines domains as traffic segmentation, layers as parameter subsets, and experiments as traffic segments plus alternate parameter values. Uses independent layer-salted diversion, one experiment per layer, preflight conflict checks, factual/counterfactual trigger logging, A/A trials, shared controls, launch layers, and experiment review/education. | Google did not define a first-class “namespace” entity. This repository’s namespace is a synthesis separating mutual-exclusion allocation from the broader semantic layer. |
| R2 | Google SRE Workbook, *Canarying Releases* | Canary/control separation, representative population and duration, attributable metrics, SLI-based guardrails, staged rollout, automation, rollback, and warning that simultaneous canaries contaminate signals. | A deployment canary asks whether a release is safe to continue, not whether a product treatment causes a desired outcome. |
| R3 | Google SRE, *Reliable Product Launches at Scale* | Lightweight but thorough review, common infrastructure, staged rollout, kill switches, launch checklists, and continuous checklist curation from failures. | Launch governance informs operational readiness; it is not an experiment-assignment design. |
| R4 | Meta/Facebook + Stanford, *Designing and Deploying Online Field Experiments* (PlanOut) | Separates experiment design from application logic; supports scalar, tuple, and multiple assignment units; deterministic salted hashing; parameterised treatments; namespaces for iterative/mutually exclusive experiments; automatic logging. | The open-source PlanOut implementation is archived. Its paper remains useful evidence, not a recommended dependency. |
| R5 | Microsoft Research, *The Anatomy of a Large-Scale Experimentation Platform* | Describes four platform components: portal, experiment execution, log processing, and analysis, with trustworthiness and scalability as core tenets. | The public summary is architectural; full product-specific implementation details are not all open on the page. |
| R6 | LinkedIn Engineering, *A/B testing at LinkedIn: Assigning variants at scale* | Hash-based assignment uses experiment + member identity for deterministic independent assignment; local cached evaluation tolerates backend failure; selected assignment data supports offline attribution; system checks pairwise interactions and SRM. | Scale numbers and implementation are LinkedIn-specific. This design adopts the principles, not their exact algorithms or metrics. |
| R7 | LinkedIn Engineering, *Our evolution towards T-REX* | Central definitions and immutable experiment states replaced scattered bucketing/config; targeting became platform functionality; client-side cached evaluation lowered latency; test identity was decoupled from experiment revision. | “Immutable state” terminology is adapted here to experiment revision and assignment epoch. |
| R8 | Netflix TechBlog, *It’s All A/Bout Testing* | Platform service managed eligibility and allocation; persisted allocations; cache reduced read latency; allocation events fed Kafka/Hive/analysis; members could join several non-conflicting tests; schedule tooling helped identify conflicts. | The 2016 architecture is historical. It demonstrates trade-offs between real-time persisted allocation, batch allocation, latency, and mobile reliability. |
| R9 | Google/Firebase, *A/B Testing concepts* | Uses experiment ID + installation ID hash, sticky active-experiment assignment, activation events to limit measurement populations, and event-level experiment properties in exported analytics. | Firebase installation ID is not a human identity. Activation gates measurement but may still be weaker than proof of actual treatment use. |
| R10 | Google Analytics, *Integrate with a third-party experiment tool* | Recommends experiment/variant identifiers on an experiment impression event for downstream analysis. | The page’s “impression” can occur at bucketing time. This repository deliberately keeps assignment and actual exposure separate. |
| R11 | Google Research, *Designing A/B tests in a collaboration network* | Shows that independent assignment of connected units can cause contamination and that cluster-level randomisation can address network interference at a power cost. | The framework can support cluster units but cannot discover causal interference automatically. |
| R12 | Google, *Canary Analysis Service* | Separates passive analysis from rollout control; uses durable evaluation IDs and idempotent result retrieval; compares precise canary/control populations; returns explicit verdicts. | CAS evaluates deployment health, not product-treatment effects. Its API and separation-of-concerns lessons generalise. |

## Key source findings

## Google overlapping infrastructure

Google rejected two extremes:

- one global layer, which is easy but starves experiments of traffic;
- a fully factorial system, which assumes every parameter combination is safe.

Its middle ground partitions parameters that cannot safely vary independently into layers. Traffic can enter one experiment per layer, and assignment across layers is independently salted:

```text
bucket = f(unit, layer) mod N
```

Google also observed that semantic layer names help detect incorrect configuration, although they can make teams reluctant to reorganise layers.

### Domains and layers

Google’s terms are precise:

- **Domain:** traffic segmentation.
- **Layer:** subset of changeable parameters.
- **Experiment:** traffic segmentation with zero or more alternate parameter values.

Domains contain layers; layers contain experiments and may contain nested domains. Changing domain traffic allocations can move users between entire experiment structures, so domain changes are consequential.

This project changes the presentation while preserving the principle:

- **Layer** remains the decision/influence and effect-compatibility boundary.
- **Allocation namespace** is a stable technical mutual-exclusion pool within a layer.
- **Eligibility** covers the domain-like traffic/subject constraints.

That mapping is synthesis, not Google terminology.

### Triggering versus assignment

Google distinguishes diverted traffic from the trigger set where the treatment changes serving. It recommends factual trigger logging in treatment and counterfactual trigger logging in control. Analysing only broad assignments can dilute effects and waste power.

This directly motivates separate:

```text
assignment → factual/counterfactual trigger → exposure/applied effect → outcome
```

### Conflict and quality checks

Google checked:

- syntax and required fields;
- unique IDs;
- layer/effect ownership;
- traffic conflicts;
- control symmetry and diversion conditions;
- experiment size/power;
- real-time metric bounds;
- pre-period/A/A uniformity;
- forgotten experiments and canonical metric definitions.

Infrastructure alone was not enough: experiment councils, checklists, shared analysis, and education were part of the system.

## Google SRE: deployment canaries are adjacent, not identical

Google SRE defines a canary as a partial, time-limited deployment evaluated to decide whether rollout should continue. It warns that:

- simultaneous canaries increase cognitive load and contaminate signals;
- service-wide metrics can hide a failing small population;
- canary/control may share dependencies and harm each other;
- before/after comparisons are confounded by time;
- metric aggregation intervals must fit within the canary duration;
- automated analysis complements rather than replaces tests and monitoring.

The experimentation service should therefore represent deployment-safety evaluations separately from product-effect experiments, even if both use allocation, exposure, metrics, and rollback primitives.

## PlanOut

PlanOut’s strongest reusable ideas are:

- experimental design is a small declarative program/configuration, not scattered branches;
- randomisation unit is explicit and may be a tuple;
- salted hashing includes namespace/experiment/variable identity to make assignments deterministic and independent;
- assignment can be evaluated consistently across loosely coupled services and languages;
- logging is part of the experiment framework;
- namespaces manage iterative and mutually exclusive experiments.

The archived implementation is not selected as a dependency.

## LinkedIn

LinkedIn contrasts persisted RNG assignment with deterministic hash assignment. Its hash approach allows most evaluations to happen locally from cached definitions and remain available during backend failure. It still records selected assignments to support offline attribution.

Important principles:

- independent hashes allow separate analysis of orthogonal experiments;
- independent assignment does not mean treatments cannot interact;
- pairwise interaction tooling makes collisions visible;
- SRM is a trust failure and should prominently invalidate ordinary reporting;
- central test identities and immutable experiment states simplify evolution and debugging.

## Netflix

Netflix’s historical service architecture demonstrates a different trade-off:

- real-time eligibility and allocation;
- persisted assignment records;
- cache for existing allocations;
- assignment events to streaming and analytical stores;
- stratification for balance;
- several simultaneous tests where conflicts are absent;
- schedule views to help owners identify tests affecting similar areas.

Netflix explicitly noted that real-time network allocation added latency and worked poorly on unreliable mobile connectivity. This supports policy-controlled cached/snapshot evaluation rather than an unconditional network dependency.

## Microsoft ExP

Microsoft frames an experimentation platform as four connected capabilities:

1. experiment portal;
2. execution service;
3. log processing;
4. analysis service.

Trustworthiness and low-friction scale are platform-wide properties; reliable bucketing alone is insufficient. The proposed MVP narrows the analysis scope but must export canonical trustworthy data and quality status.

## Synthesis adopted by this repository

The following are design decisions derived across sources rather than mandates from one source:

1. Separate a semantic **layer** from a technical **allocation namespace**.
2. Add explicit **effect claims** to make compatibility machine-checkable.
3. Use fixed namespace slot ownership so unrelated add/remove operations cannot compact traffic.
4. Persist authoritative first decisions while retaining deterministic replay and policy-controlled local evaluation.
5. Propagate a signed decision-context token and record actual applied effects.
6. Store complete co-exposure context so interactions can be identified later.
7. Treat attribution as a versioned derived data product over immutable facts.
8. Leave feature delivery downstream of assignment.
9. Make failure behaviour explicit per layer/experiment.
10. Keep deployment canary decisions distinct from product experiment inference.

## Exact sources

- **[R1]** Diane Tang, Ashish Agarwal, Deirdre O’Brien, Mike Meyer, [Overlapping Experiment Infrastructure: More, Better, Faster Experimentation](https://research.google.com/pubs/archive/36500.pdf), KDD 2010. [Google Research record](https://research.google/pubs/overlapping-experiment-infrastructure-more-better-faster-experimentation).
- **[R2]** Google SRE Workbook, [Canarying Releases](https://sre.google/workbook/canarying-releases/).
- **[R3]** Google SRE, [Reliable Product Launches at Scale](https://sre.google/sre-book/reliable-product-launches/) and [Launch Coordination Checklist](https://sre.google/sre-book/launch-checklist/).
- **[R4]** Eytan Bakshy, Dean Eckles, Michael Bernstein, [Designing and Deploying Online Field Experiments](https://hci.stanford.edu/publications/2014/planout/planout-www2014.pdf); [Meta Research record](https://research.facebook.com/publications/designing-and-deploying-online-field-experiments); [archived implementation](https://github.com/facebookarchive/planout).
- **[R5]** Microsoft Research, [The Anatomy of a Large-Scale Experimentation Platform](https://www.microsoft.com/en-us/research/publication/the-anatomy-of-a-large-scale-experimentation-platform).
- **[R6]** LinkedIn Engineering, [A/B testing at LinkedIn: Assigning variants at scale](https://www.linkedin.com/blog/engineering/ab-testing-experimentation/a-b-testing-variant-assignment).
- **[R7]** LinkedIn Engineering, [Our evolution towards T-REX](https://www.linkedin.com/blog/engineering/ab-testing-experimentation/our-evolution-towards-t-rex-the-prehistory-of-experimentation-i).
- **[R8]** Netflix TechBlog, [It’s All A/Bout Testing: The Netflix Experimentation Platform](http://techblog.netflix.com/2016/04/its-all-about-testing-netflix.html).
- **[R9]** Firebase, [About A/B Testing](https://firebase.google.com/docs/ab-testing/ab-concepts) and [Create Remote Config experiments](https://firebase.google.com/docs/ab-testing/abtest-config).
- **[R10]** Google Analytics, [Integrate with a third-party experiment tool](https://developers.google.com/analytics/devguides/collection/ga4/integration).
- **[R11]** Google Research, [Designing A/B tests in a collaboration network](https://research.google/pubs/designing-ab-tests-in-a-collaboration-network).
- **[R12]** Google, [Canary Analysis Service](https://sre.google/static/pdf/canary_analysis.pdf).

## Further reading

- Microsoft Research [Experimentation Platform publications and articles](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/).
- LinkedIn, [A/B Testing Challenges in Large Scale Social Networks](https://content.linkedin.com/content/dam/engineering/site-assets/pdfs/ABTestingSocialNetwork_share.pdf).
- Netflix Research, [Engineering for a Science-Centric Experimentation Platform](https://research.netflix.com/publication/engineering-for-a-science-centric-experimentation-platform).
- Google Research, [Focus on the Long-Term](https://research.google/pubs/focus-on-the-long-term-its-better-for-users-and-business).
