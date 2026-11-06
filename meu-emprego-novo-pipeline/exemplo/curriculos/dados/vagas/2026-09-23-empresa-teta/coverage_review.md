# Coverage Review (FICTIONAL EXAMPLE)

**Target:** Mid-Level Data Scientist (NLP), Company Theta.
**Evaluated Version:** First `data_scientist-v1`, then `data_scientist-v2`.
**Sources:** `input/karine_duarte/profile_truth.md` (priority), `outputs/karine_duarte/data_scientist/json/resume.json`, and `job_desc.md`.

## Result with `data_scientist-v1`

The clinical data analysis and automated reporting—which are central to this specific role—were buried in the last bullet point of the oldest employer, and the automated resource allocation routines did not appear at all. Because of this, `data_scientist-v2` was generated using the adjustment prompt.

## Preserved in `data_scientist-v2`

All four employers (TaskUs, RWS Group, Stealth AI Lab, SMS Nova Olímpia), real job titles, and dates were strictly maintained. One highlight was brought forward based on the master profile's addendums (VBA automation). No new metrics were hallucinated (the verified 15TB+, 99.2% accuracy, and 40% bias reduction remain intact).

## Strong Coverage

| Requirement | Resume Evidence | Profile Origin |
| --- | --- | --- |
| Python and SQL | PySpark ETL pipelines and complex queries | RWS Group & SMS Nova Olímpia |
| Actionable Business/Health Reports | Analyzed clinical datasets to inform strategic planning | SMS Nova Olímpia |
| NLP & PyTorch | Deployed NLP models using Hugging Face Transformers | RWS Group |
| Automated Routines (Desirable) | Automated resource allocation reports using Excel VBA | Master Profile Addendum (2026-09-21) |

## Partial Coverage

None.

## Uninvented Gaps

* **A/B Testing in Production** (desirable): Listed only as a theoretical competency under the "Skills / Analytics" section; no production rollout is claimed.

## Inconsistencies Found

None. All numbers in the resume exist in the master profile with a verified `[measured]` origin.

## Suggested Decision

Apply using `data_scientist-v2`. No mandatory requirements are missing, and the profile perfectly bridges the gap between data modeling and actionable reporting.

*This review does not state that all mandatory requirements are met.*