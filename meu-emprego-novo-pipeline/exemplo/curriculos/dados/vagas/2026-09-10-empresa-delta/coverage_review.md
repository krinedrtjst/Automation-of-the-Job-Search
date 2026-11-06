# Coverage Review

**Target:** AI Alignment Specialist / Senior Data Scientist, Company Delta.
**Evaluated Version:** `ai_alignment-v1`.
**Sources:** `input/karine_duarte/profile_truth.md` (priority), `outputs/karine_duarte/ai_alignment/json/resume.json` and `job_desc.md`.

## Preserved

Four employers (TaskUs, RWS Group, Stealth AI Lab, SMS Nova Olímpia), real job titles, and dates maintained. Highlights focused on Generative AI, NLP, and large-scale data manipulation present in the master profile. No new metrics were hallucinated; the metrics of 15 TB+, 99.2% accuracy, and 40% bias reduction were strictly preserved.

## Strong Coverage

| Requirement | Resume | Profile Evidence |
| --- | --- | --- |
| RLHF and Red-Teaming Experience | Adversarial prompt injections, structured RLHF rubrics | TaskUs and Stealth AI Lab |
| Big Data Processing | Automated PySpark ETL pipelines (15 TB+) | RWS Group |
| NLP, PyTorch and LLMs | Fine-tuning with Transformers and fairness algorithms | RWS Group and Stealth AI |
| English Fluency | C2 English (Full Professional) | Languages Section |

## Partial Coverage

* **Cognitive Sciences and AI Behavior:** The job requires experience in evaluating foundational model behavior. The solid background in Clinical Neuropsychology and epidemiological research (SMS Nova Olímpia) meets this requirement in an interdisciplinary manner.

## Uninvented Gaps

* **Full-Stack / Web Development (React, Node.js)** (desirable): The job mentions creating interfaces for internal tools. The resume does not present this experience, respecting the master profile's strict constraint against inventing front-end skills.
* **Cloud Architecture (AWS/GCP)** (desirable): The profile focuses heavily on the data layer (PySpark) and modeling (PyTorch), but does not prove pure cloud infrastructure engineering.

## Inconsistencies Found

None. The optimizing agent did not attempt to disguise the lack of React or AWS by inventing fake projects. All numbers on the resume exist in the master profile with a factual origin of `[measured]`.

## Suggested Decision

**High Fit.** Although there are gaps in web development and cloud infrastructure, the coverage of mandatory AI Alignment, data manipulation (PySpark), and bias mitigation requirements is perfect. Application highly recommended. The next step is to use the Interview Copilot to prepare a strong narrative on how Neuropsychology supports Generative AI safety.

*This review does not state that all mandatory requirements are met.*