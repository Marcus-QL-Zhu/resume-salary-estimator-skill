# Resume Salary Estimator Skill

A Codex skill for building explainable resume-based salary estimators.

This skill helps an agent estimate a candidate's expected salary range from resume text and structured profile fields. It is designed for recruiting analytics, compensation research, talent mapping, and resume-based salary explanation workflows.

The skill is domain-general. It does not assume any specific data source, platform, geography, employer, or job family. Users should recalibrate the indicators and salary model with their own dataset.

## What It Does

The skill guides Codex to:

- parse resume text and structured candidate fields;
- build a baseline salary model from experience, function, level, target role, and other profile variables;
- engineer resume-derived value and risk signals;
- compare apparent salary differences with residual salary differences;
- output an objective algorithmic estimate with a prediction interval;
- provide separate qualitative interpretation without overriding the algorithmic estimate.

## Key Output Rule

The skill requires the agent to output results in this order:

1. Objective algorithmic salary estimate.
2. 80% prediction interval.
3. Model inputs and rule-based numeric adjustments.
4. Separate subjective qualitative analysis.

The subjective section may discuss factors that could support upward or downward interpretation, but it must not produce a second adjusted salary number.

## Included Indicators

The reference guide includes reusable indicator patterns such as:

- end-to-end ownership;
- cross-functional breadth;
- career scatter risk;
- responsibility without results;
- weak ownership signal;
- recent short-tenure risk;
- tool stack without results;
- title inflation risk.

Each indicator is intended as a template. Thresholds, keywords, and model weights should be validated on the user's own data before use.

## Repository Structure

```text
resume-salary-estimator/
  SKILL.md
  agents/openai.yaml
  references/indicators.md
  scripts/resume_salary_features.py
LICENSE
README.md
```

## Quick Start

Use the bundled feature script on a CSV with a resume text column:

```bash
python resume-salary-estimator/scripts/resume_salary_features.py \
  --input candidates.csv \
  --output candidate_features.csv \
  --resume-col resume_text \
  --salary-col expected_salary_annual
```

The script creates generic resume signal columns. Review and adapt the dictionaries before treating the output as final.

## Installation

Copy or clone the `resume-salary-estimator` folder into your Codex skills directory.

Example:

```bash
git clone https://github.com/Marcus-QL-Zhu/resume-salary-estimator-skill.git
```

Then place the `resume-salary-estimator/` skill folder where your Codex environment loads local skills.

## License

MIT License.
