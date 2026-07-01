# Resume Salary Indicator Reference

Use these indicators as templates, not universal truth. Recalibrate keyword dictionaries, thresholds, and salary adjustments for each dataset and domain.

## Core Concepts

### Apparent Salary Lift

Definition:

```text
median_salary(signal = 1) - median_salary(signal = 0)
```

Meaning: the raw group difference before controlling for experience, role, function, level, location, or other confounders.

### Residual Salary Lift

Fit a baseline salary model first. Then compute:

```text
salary_residual = observed_salary - baseline_predicted_salary
median_residual(signal = 1) - median_residual(signal = 0)
```

Meaning: whether a signal adds independent salary explanation after baseline controls.

Use apparent lift for descriptive EDA. Use residual lift for model feature decisions.

## Baseline Features

Prefer structured, auditable inputs:

- years of experience;
- current function;
- current level;
- target or expected function;
- target or expected level;
- highest degree;
- overseas education signal;
- elite-school signal;
- education field relevance;
- international language signal;
- location;
- work mode or job type where relevant.

A useful transparent experience baseline is a quadratic log-salary curve:

```text
log(salary + 1) = b0 + b1 * years_experience + b2 * years_experience^2
```

The quadratic term captures diminishing marginal returns to experience.

## Resume-Derived Indicators

### Education Signals

Purpose: capture structured education information before using subjective interpretation.

Recommended fields:

- `highest_degree_group`: associate, bachelor, master, mba, phd, or unknown;
- `highest_degree_rank`: ordinal encoding of the highest degree;
- `has_master_or_above`;
- `has_phd`;
- `has_mba`;
- `overseas_education_signal`;
- `elite_education_signal`;
- `education_field_groups`;
- `international_language_signal`.

Interpretation:

- Treat education as a baseline/profile feature, not a resume-text premium by default.
- Validate apparent and residual lift before assigning any numeric adjustment.
- Report whether education remains meaningful after function, level, and experience controls.
- Compare model performance before and after adding education features; do not keep education weights solely because they feel intuitively right.
- Domain fit matters. A technical master's degree may matter more in engineering roles, while MBA or international language signals may matter more in product, strategy, sales, and general-management roles.
- If education is not included in the objective model, explicitly disclose that it was used only in qualitative analysis.

### End-to-End Ownership

Purpose: identify whether broad responsibilities reflect real ownership rather than vague participation.

Positive evidence can include:

- owner verbs: led, owned, built, launched, delivered, scaled, transformed, migrated, commercialized;
- value-chain span: requirement, design, build, launch, operation, optimization, monetization;
- measurable outcomes: revenue, cost, efficiency, quality, latency, yield, conversion, retention, uptime;
- organization scope: team, budget, business unit, factory, product line, region, customers.

Use as an opportunity badge or mild positive context. Do not assume it always creates salary premium.

### Cross-Functional Breadth

Purpose: measure whether a resume crosses multiple function families.

Example families:

- technology;
- product;
- project or delivery;
- sales or business development;
- operations or supply chain;
- manufacturing or quality;
- management;
- finance, legal, or HR.

Interpretation:

- Breadth plus end-to-end ownership can indicate senior operating range.
- Breadth without ownership or outcomes can indicate unfocused narrative.

Do not use breadth alone as a salary premium.

### Career Scatter Risk

Purpose: flag very broad career narratives that span many unrelated functions.

Generic rule:

```text
career_scatter_risk = 1 if function_family_hit_count >= threshold
```

Recommended threshold: start with 5 families, then validate.

Use only conditionally:

```text
if career_scatter_risk and not end_to_end_ownership:
    show focus-risk badge or apply small capped negative adjustment
else:
    do not penalize
```

### Responsibility Without Results

Purpose: identify resumes with many responsibility words but weak outcome evidence.

Generic rule:

```text
responsibility_count high
and numeric_result_count low
and outcome_word_count low
```

Useful as a mild negative or review badge. It often means the resume describes duties rather than business impact.

### Weak Ownership Signal

Purpose: identify coordination-heavy resumes with limited ownership evidence.

Possible evidence:

- coordination words: coordinated, supported, assisted, followed up, communicated, aligned, tracked;
- low ownership words: led, owned, independently, accountable, end-to-end;
- low result evidence.

Use cautiously because some roles are valuable precisely because they coordinate complex stakeholders.

### Recent Short-Tenure Risk

Purpose: factual stability-risk signal based on completed formal jobs.

Recommended parsing:

- parse only formal work-experience sections;
- stop before project, education, skills, or certification sections;
- exclude current roles ending in "present" or equivalent;
- deduplicate near-identical date ranges caused by merged resume sources;
- count only completed formal roles.

Generic rule:

```text
recent_short_tenure_risk = 1
if at least 2 of the most recent 3 completed formal roles are <= 18 months
and the most recent 2 completed formal roles average <= 24 months
```

Interpretation:

- This is a hard factual risk badge.
- It may have large apparent salary differences because short-tenure candidates can be younger or lower-level.
- If residual lift is near zero, do not use it as an independent salary discount.

### Tool Stack Without Results

Purpose: identify resumes listing many technologies or tools but little outcome evidence.

Use as an explanation badge. It often captures junior or hands-on profiles, so residual lift may be small after controlling for role and level.

### Title Inflation Risk

Purpose: identify senior-sounding titles with limited scope evidence.

Use only after careful validation. This rule is noisy and can unfairly penalize genuinely senior individual contributors, architects, advisors, or narrow-domain experts.

## Validation Pattern

For each indicator, record:

- rule definition;
- positive sample size;
- positive rate;
- apparent salary lift;
- residual salary lift;
- median experience in positive and negative groups;
- manual sample notes;
- final decision: model feature, badge only, holdout, or discard.

For rule iteration:

```text
1. Reserve validation sample.
2. Test broad rule.
3. Inspect false positives.
4. Tighten section parsing, thresholds, and exclusions.
5. Stop when confidence target or max iteration count is reached.
```

## Estimator Design

Recommended layering:

1. Baseline salary range from structured features.
2. Residual model or calibrated adjustments from validated text signals.
3. Explanation badges for useful but non-independent signals.
4. Confidence caveat based on sample size and out-of-sample error.

Keep direct adjustments capped. Resume text is noisy, and many signals are correlated with function, level, and experience.
