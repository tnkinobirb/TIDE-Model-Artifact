This document outlines the method used to identify, analyse, and decompose queries from literature.

To test the need for a missing formalisation relevant to data lineage and provenance, the Provenance Challenges and MLMD were identified as useful sources of queries and capabilities expected from provenance tools.

Sources were selected when they provided explicit questions or use cases that a provenance system was expected to answer using recorded execution or data information. The analysis was then used to identify repeated requirements across those questions.

A repeated requirement was considered a candidate for shared formalisation when it:

1. appeared across multiple questions;
2. was required across domain-independent questions; and
3. was representable without replacing domain-specific semantics.

[1] - https://openprovenance.org/provenance-challenge/FirstProvenanceChallenge.html  
[2] - https://openprovenance.org/provenance-challenge/SecondProvenanceChallenge.html  
[3] - https://openprovenance.org/provenance-challenge/ThirdProvenanceChallenge.html  

Specifically, the Provenance Challenges were chosen for their expansive query sets. Originally designed to understand the capabilities provided by tools at the time of publishing [1], the challenges eventually informed the creation of the Open Provenance Model, including later additional profiles [3].

These challenges are therefore a useful source for identifying the general capabilities tools need to answer provenance queries and the requirements needed to provide those capabilities.

We selected the Second and Third Provenance Challenges [2][3] as our analysis set. The Second Provenance Challenge reworked the First Challenge queries to minimise ambiguity in query wording and improve comparison across systems. We therefore analysed the Second Challenge in place of the First, which was not counted separately.

Additionally, MLMD's guide and tutorial contained useful use-case questions that revealed some of the core capabilities expected to be answerable by MLMD or modern provenance tools.

# Query/Question Identifiers

`n` = the number of the specified query.

- `SCQn` = Second Provenance Challenge Queries
- `TCQn` = Third Provenance Challenge Main Queries
- `TOQn` = Third Provenance Challenge Optional Queries
- `MGQn` = MLMD Guide Questions
- `MTQn` = MLMD Tutorial Questions

# Method for decomposition

1. What is the challenge asking for?
2. What is given to answer it?
3. What is required to answer it?
4. What is required to provide those requirements?
5. Answer check.

The answer check is used to confirm that the identified requirements are enough to derive the source answer where one is supplied, or the requested answer form where the concrete query inputs are not supplied.

# Method for identifying repeated requirements

Every requirement sourced from the decomposition was associated with a requirement type.

The six requirement types are:

1. **Identity** — distinguish a specific recorded data item, process occurrence, model, or workflow execution.
2. **Producer-Consumer relationship** — distinguish which recorded process occurrence produced or consumed a recorded data item, including recorded inputs or outputs whose external producer or consumer is outside the selected history.
3. **Execution Status** — distinguish the status of a specific recorded process occurrence.
4. **Ordering/Time** — distinguish when recorded process occurrences happened or their required execution order.
5. **Domain Semantics** — distinguish the meaning, structure, creation, modification, or effects of domain data, such as CSV files, database tables and rows, values, queries, and mappings.
6. **Annotations and Filtering** — distinguish or label data items, process occurrences, or models using specified names, parameters, roles, or other metadata, and apply those fields as filters where required.

`Data Dependency` was not kept as a separate requirement type. Upstream and downstream histories are answer capabilities obtained by composing the required identities and Producer-Consumer relationships.

# Example

## Second Provenance Challenge

<h5>CHALLENGE 1</h5>

Find the process that led to `Atlas X Graphic`, or everything that caused `Atlas X Graphic` to be as it is. This should tell us the new brain images from which the averaged atlas was generated, the warping performed, etc.

1. **What is the challenge asking for?**

   Identify all known data items and process occurrences that led to or affected the production of `Atlas X Graphic`.

2. **What is given to answer it?**

   A. The data item to investigate: `Atlas X Graphic`.

3. **What is required to answer it?**

   A. Which process produced `Atlas X Graphic`.  
   B. Which data items that process consumed.  
   C. Which processes produced those consumed data items.  
   D. Repeat B and C for every identified upstream process until the starting data items are reached.  
   E. Identify the production and consumption relationships connecting the data items and process occurrences in the resulting history.

4. **What is required to provide those requirements?**

   A. Exact recorded data items must be distinguishable. | **REQ_TYPE:** Identity  
   B. Exact recorded process occurrences must be distinguishable. | **REQ_TYPE:** Identity  
   C. It must be known which process produced each data item. | **REQ_TYPE:** Producer-Consumer relationship  
   D. It must be known which process consumed each data item. | **REQ_TYPE:** Producer-Consumer relationship  

5. **Answer check**

   `Atlas X Graphic`  
   > produced by `convert` (step 13)  
   > which consumed `Atlas X Slice`  
   > produced by `slicer` (step 10)  
   > which consumed `Atlas Image` and `Atlas Header`  
   > produced by `softmean` (step 9)  
   > which consumed all four resliced image/header pairs  
   > produced by `reslice` (steps 5–8)  
   > which consumed `Warp Parameters 1–4`  
   > produced by `align_warp` (steps 1–4)  
   > which consumed the four Anatomy Image/Header pairs and the shared  
   > `Reference Image` and `Reference Header`.

## Discussion of review

After decomposing the 35 included questions, 178 atomic requirements were mapped to six recurring requirement types.

The most common was `Identity`, appearing in 32 questions. These questions required specific recorded data items, process occurrences, models, or workflow executions to be distinguished.

The second most common was `Producer-Consumer relationship`, appearing in 25 questions. In questions asking for exact movement between process occurrences and recorded data items, this requirement was used with `Identity` so the participating items and occurrences could be distinguished.

| Requirement type | Questions containing the requirement |
|---|---:|
| Identity | 32 |
| Producer-Consumer relationship | 25 |
| Execution Status | 9 |
| Ordering/Time | 6 |
| Domain Semantics | 9 |
| Annotations and Filtering | 23 |
| **Total questions analysed** | **35** |

Three questions did not require `Identity`. They were answered entirely through domain-specific information.

Ten questions did not require a `Producer-Consumer relationship`. Instead, they relied on one or more of `Identity`, `Execution Status`, `Ordering/Time`, `Domain Semantics`, and `Annotations and Filtering`.

## Formalisation candidates

| Requirement type | Reason for consideration | Decision in this analysis |
|---|---|---|
| **Identity** | Appeared most frequently and is required before exact recorded items or occurrences can be referred to. | Required as a basis, but not selected for a new shared formalisation. Systems already provide native identities, while correspondence between different identity schemes generally requires supplied mappings or domain knowledge. |
| **Producer-Consumer relationship** | Appeared repeatedly across sources and describes how recorded data moved between exact process occurrences. | Selected as the strongest candidate for shared formalisation because it is structural, repeated across systems, and can be represented without replacing native identities or domain semantics. |
| **Execution Status** | Required by questions about completed, failed, halted, or unexecuted processes. | Not selected in this work. Status vocabularies and meanings may differ between systems, and the corpus does not establish one shared status model. |
| **Ordering/Time** | Required by questions involving elapsed time, process order, or events before and after a halt. | Not selected in this work. These questions require timestamps or ordering information, but the analysis does not establish the need for a new shared time or ordering formalisation. |
| **Domain Semantics** | Required to interpret files, database rows, values, queries, operation effects, and domain-specific mappings. | Not selected in this work. The required meanings were specific to the data structures and operations used by each source, and the corpus does not establish one shared domain-semantic model. |
| **Annotations and Filtering** | Appeared frequently and was used to select, filter, label, or return particular items and occurrences. | Not selected in this work. The required annotations varied substantially between questions, and the corpus does not establish one common annotation schema. |

Although `Identity` was the most frequent requirement, the analysis did not itself establish that a new shared identity formalisation was needed. Individual systems already assign identities to their native records, while correspondence between independently implemented identity schemes generally requires supplied mappings and may remain domain-dependent.

`Annotations and Filtering` also appeared frequently, but the required annotations, parameters, roles, and metadata varied substantially by source and use case. The analysis therefore shows that this information is often needed, but it does not yet show that one shared annotation formalisation would be suitable.

`Domain Semantics` was similarly tied to particular data structures and operations, including CSV files, database rows, values, queries, mappings, and rules describing how data was created or changed.

Questions involving `Annotations and Filtering` or `Domain Semantics` often combined those requirements with `Producer-Consumer relationship`. Additional information selected or interpreted the relevant recorded item or occurrence, while the structural relationships connected it to the represented execution history.

`Producer-Consumer relationship` was the most frequent requirement describing a repeated structural relationship between recorded data items and process occurrences. It was therefore selected as the strongest candidate for shared formalisation within this analysis.

Within the analysed corpus, `Identity` and `Producer-Consumer relationship` formed a recurring structural basis for questions asking how recorded data moved between process occurrences. `Domain Semantics` and `Annotations and Filtering` supplied additional information required by particular domains and tasks.

This does not establish that the other requirement types could not benefit from formalisation. It only explains why `Producer-Consumer relationship` was selected for the scope of this work.

Following this result, additional literature was reviewed to identify whether this relationship has already been formalised and, where it has, whether the formalisation preserves the exact identities, production and consumption relationships, and complete upstream or downstream histories required by the analysed questions. Where it does not, the missing distinctions and conditions needed to provide those requirements were identified.

## Producer-Consumer normalisation conclusion

The different Producer-Consumer phrasings reduce to four directional questions: which Execution produced or consumed a selected State, and which States a selected Execution consumed or produced. The normalisation does not merge away the source-specific atomic requirement; it keeps that requirement and its stable ID visible, then records which of the four answer forms it supports. This is why one “produced or used” requirement may link to two forms while remaining one classified atomic occurrence.

# Files

- `source_selection.csv` — declared source boundary and every retained or excluded source item.
- `source_questions.csv` — the 35 retained questions, stable labels, concise paraphrases, requested answers, and direct official URLs.
- `question_conditions.csv` — target, type, boundary, and filter conditions already supplied by each question.
- `atomic_requirements_classification.csv` — the authoritative 178 classified occurrences, each carrying its stable requirement ID and any Producer-Consumer form link.
- `atomic_requirement_catalogue.csv` — the 97 distinct canonical requirements, their IDs, repetition counts, question counts, and question appearances.
- `producer_consumer_normalisation.csv` — the complete requirement-to-`PC1`–`PC4` crosswalk, including both the TIDE restatement and the exact answer wording printed in the paper.
- `aggregation_summary.xlsx` — the human-readable summary of corpus-level counts.
- `source_snapshot_manifest.csv` — sources and access date
