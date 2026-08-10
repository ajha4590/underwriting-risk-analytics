# Life Insurance Underwriting Analytics: Medical & Financial Risk Trends

## Background
In my current role as an Underwriting Analyst (life insurance & reinsurance), I assess
~15,000+ cases per year — evaluating medical and financial risk to decide whether an
application is Standard, Rated (extra premium), Postponed, or Declined, and whether
riders like Critical Illness (CI) or Total & Permanent Disability (TPD) apply.

This project rebuilds that analysis end-to-end using **SQL, Python, and Tableau**, to
demonstrate how the manual, case-by-case judgment underwriters apply daily can be scaled
into a portfolio-level analytics view for underwriting, pricing, and product teams.

> **Data note:** All data in this project is **synthetically generated** — no real
> policyholder, case, or client data is used anywhere. The generator (`generate_underwriting_data.py`)
> builds realistic statistical relationships (e.g. medical condition risk rising with age
> and BMI, rider attachment varying by plan type and age) so the resulting trends mirror
> genuine underwriting patterns without exposing any confidential information.
> Distribution partners are labeled generically (Partner A/B/C/D) rather than naming real
> insurers.

## Business questions this project answers
- What does a year of underwriting case volume look like, and is there seasonality?
- Which medical conditions are trending, and in which age groups?
- What's the rider (CI/TPD) attachment rate, and who's buying them?
- How does financial profile (income, sum assured) vary by plan type and age?
- What actually drives a "Rated" underwriting decision — and can it be predicted?

## Project structure
```
├── generate_underwriting_data.py   # Synthetic data generator (15,400 simulated cases)
├── underwriting_cases.csv          # Generated dataset
├── sql_analysis.sql                # Schema + 12 analysis queries
├── python_analysis.py              # EDA, chi-square test, risk classification model
├── chart_monthly_volume.png        # Output chart
├── chart_medical_prevalence.png    # Output chart
├── chart_feature_importance.png    # Output chart
└── README.md
```

## Tech stack & what each layer shows
| Layer | Tool | What it demonstrates |
|---|---|---|
| Data generation | Python (pandas, numpy) | Simulating realistic correlated data |
| Querying | SQL (SQLite-compatible) | Aggregation, window functions, CTEs-style analysis |
| Analysis | Python (pandas, scikit-learn, scipy) | EDA, hypothesis testing, classification modeling |
| Visualization | Tableau Public | Interactive dashboard for a business audience |

## Key findings
- **Medical risk rises sharply with age**: Diabetes prevalence goes from ~3% in the
  18-24 age band to ~13% in the 55-65 band — the single clearest trend in the portfolio.
- **Rider attachment is significantly associated with age band** (chi-square test,
  p < 0.001) — attachment peaks in the 25-44 age range, where CI/TPD riders are most
  commonly bundled with Term Life policies.
- **Term Life carries the highest rider attachment rate** (~34%) vs. Whole Life and
  Savings/ULIP (~21-22%) — a pattern that's useful for cross-sell strategy.
- **Occupation risk class, medical condition, and smoker status are the top three
  predictors of a "Rated" decision** (Random Forest classifier, ROC-AUC 0.999 on
  synthetic data) — age and BMI matter, but occupation risk dominates.

## How to reproduce
```bash
pip install pandas numpy scikit-learn scipy matplotlib faker

python generate_underwriting_data.py     # generates underwriting_cases.csv
python python_analysis.py                # runs EDA, stats test, and risk model

# Load underwriting_cases.csv into SQLite/Postgres and run sql_analysis.sql
# Load underwriting_cases.csv into Tableau Public for the dashboard
```

## Tableau Dashboard
Published dashboard: *[add your Tableau Public link here once published]*

Structured as 3 views:
1. **Portfolio Overview** — case volume trend, plan type mix, partner-level breakdown
2. **Medical Risk Trends** — condition prevalence by age (heatmap), decision outcome by condition
3. **Financial & Product Trends** — sum assured by age/plan, rider attachment trends, income vs. plan type

## What I'd tell an interviewer
"In my day-to-day underwriting role I make this kind of risk assessment case-by-case,
manually reviewing medical and financial factors for each application. This project
shows I can take that same judgment and apply it at a portfolio level — surfacing trends
an underwriting team lead or product manager would actually act on, like which segments
are driving loss experience or where rider cross-sell opportunity is highest."
