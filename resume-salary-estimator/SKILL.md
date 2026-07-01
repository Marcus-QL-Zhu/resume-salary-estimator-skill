---
name: resume-salary-estimator
description: Build explainable salary estimators from resume text and structured candidate profile fields. Use when Codex needs to parse resumes, engineer resume-derived value/risk signals, compare apparent salary differences with residual differences, design compensation or expected-salary models, or explain why a resume may estimate above or below a baseline salary range.
---

# Resume Salary Estimator

## Overview

Use this skill to build an explainable resume-based salary estimator. The estimator should combine structured profile features, resume-derived signals, and residual analysis rather than relying on keyword counts alone.

The skill is domain-general. Do not assume any specific platform, employer dataset, recruiting workflow, geography, or job family. Adapt all keyword dictionaries and salary units to the user's dataset.

## Core Workflow

1. Identify the target variable.
   - Prefer expected or requested annual salary when the task is about candidate expectations.
   - Prefer actual compensation only when verified compensation data is available.
   - Output ranges, not single-point truth claims.

2. Build the baseline model first.
   - Use structured features such as years of experience, current function, current level, target function, target level, education, location, and work mode.
   - Include education fields when available: highest degree, overseas education, elite-school signal, field relevance, and international language signal.
   - Keep a simple experience-only curve as a transparent benchmark.
   - Fit a stronger baseline with role/function/level controls before interpreting resume text signals.

3. Engineer resume-derived signals.
   - Use `references/indicators.md` for indicator definitions and adaptation guidance.
   - Use factual indicators where possible, especially work-tenure patterns.
   - Treat subjective self-description signals as explanatory, not definitive.

4. Compare apparent salary lift with residual lift.
   - Apparent salary lift: median salary among signal-positive candidates minus median salary among signal-negative candidates.
   - Residual lift: median model residual among signal-positive candidates minus median model residual among signal-negative candidates.
   - A signal with apparent lift but near-zero residual lift is useful for explanation or risk context, but should not receive a strong independent salary adjustment.

5. Validate before using a signal.
   - Reserve a validation sample.
   - Iterate rules up to a fixed maximum when possible.
   - Prefer precision/confidence for risk badges and recall for screening-support features.
   - Manually inspect examples when text extraction or section parsing may be noisy.

6. Produce an estimator output.
   - First return the objective algorithmic estimate and its 80% prediction interval.
   - State the model inputs, baseline estimate, and any rule-based numeric adjustments used by the skill.
   - Explicitly state whether education was included in the objective model inputs. If education is missing or only used qualitatively, say so.
   - Then provide a separate subjective qualitative analysis section.
   - In the subjective section, describe factors that may justify upward or downward interpretation, but do not give a second adjusted salary number or override the algorithmic estimate.
   - Add explanation badges for signals that are useful but not independently salary-predictive.
   - Include caveats about dataset scope and non-market-wide generalization.

## When Using Scripts

For CSV-like data, consider running:

```bash
python scripts/resume_salary_features.py --input candidates.csv --output candidate_features.csv --resume-col resume_text --salary-col expected_salary_annual
```

The script creates generic resume signal columns. Read and adapt the dictionaries before treating the output as final.

## Output Guidance

Use language like:

```text
Objective algorithmic result: based on similar candidates in the provided dataset, this profile is estimated at X annual salary units, with an 80% prediction interval of Y-Z. The estimate is driven mainly by function, level, and experience. Rule-based signal adjustments included: ...

Subjective qualitative interpretation: the resume also shows factors that may support an upward/downward reading, such as ..., but these are not converted into a second numeric estimate.
```

Avoid language like:

```text
This candidate is worth exactly X.
After qualitative judgment, I would change the estimate to X.
```

## References

- Read `references/indicators.md` when defining, adapting, or explaining resume-derived indicators.
