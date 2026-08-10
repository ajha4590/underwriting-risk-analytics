"""
Life Insurance Underwriting Analytics - Simulated Dataset Generator
----------------------------------------------------------------------
Generates a realistic (fully synthetic, non-confidential) dataset that
mirrors the structure and patterns of a life insurance underwriting book
of business: ~15,000 cases across a year, spanning plan types, riders,
medical risk factors, financial underwriting inputs, and underwriting
decisions.

No real client, policyholder, or case data is used. All records are
randomly generated with realistic statistical relationships (e.g. older
applicants and higher BMI/smoker status increase the likelihood of a
medical flag, rated decision, and higher premium loading) so that the
resulting trends resemble genuine underwriting patterns without
reproducing any actual company's data.

Output: underwriting_cases.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# ----------------------------------------------------------------------
# Reproducibility
# ----------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

N_CASES = 15400  # "15K plus cases" per year

# ----------------------------------------------------------------------
# 1. Application date - spread across one year with mild seasonality
#    (slightly higher volumes in Jan (new year resolutions) and Mar
#    (financial year end in India) - a realistic touch for an Indian
#    insurance book of business)
# ----------------------------------------------------------------------
YEAR = 2025
start_date = datetime(YEAR, 1, 1)

month_weights = {
    1: 1.25, 2: 0.95, 3: 1.35, 4: 0.85, 5: 0.85, 6: 0.90,
    7: 0.90, 8: 0.90, 9: 0.95, 10: 1.00, 11: 1.00, 12: 1.10
}
months = list(month_weights.keys())
weights = np.array(list(month_weights.values()))
weights = weights / weights.sum()

chosen_months = np.random.choice(months, size=N_CASES, p=weights)
application_dates = []
for m in chosen_months:
    days_in_month = 28 if m == 2 else (30 if m in [4, 6, 9, 11] else 31)
    day = np.random.randint(1, days_in_month + 1)
    application_dates.append(datetime(YEAR, m, day))

# ----------------------------------------------------------------------
# 2. Age - realistic working-age skew (peak 28-45)
# ----------------------------------------------------------------------
age = np.random.normal(loc=36, scale=10, size=N_CASES)
age = np.clip(age, 18, 65).round().astype(int)

def age_band(a):
    if a < 25: return "18-24"
    elif a < 35: return "25-34"
    elif a < 45: return "35-44"
    elif a < 55: return "45-54"
    else: return "55-65"

age_bands = np.array([age_band(a) for a in age])

# ----------------------------------------------------------------------
# 3. Gender
# ----------------------------------------------------------------------
gender = np.random.choice(["Male", "Female"], size=N_CASES, p=[0.62, 0.38])

# ----------------------------------------------------------------------
# 4. Smoker status - higher among males, rises slightly with age
# ----------------------------------------------------------------------
base_smoker_prob = np.where(gender == "Male", 0.22, 0.04)
age_adj = (age - 18) / 100  # small upward nudge with age
smoker_prob = np.clip(base_smoker_prob + age_adj, 0, 0.45)
smoker_status = np.array([np.random.choice(["Yes", "No"], p=[p, 1 - p]) for p in smoker_prob])

# ----------------------------------------------------------------------
# 5. BMI - normal distribution, mildly correlated with age
# ----------------------------------------------------------------------
bmi = np.random.normal(loc=24 + (age - 30) * 0.05, scale=3.5, size=N_CASES)
bmi = np.clip(bmi, 16, 45).round(1)

def bmi_class(b):
    if b < 18.5: return "Underweight"
    elif b < 25: return "Normal"
    elif b < 30: return "Overweight"
    else: return "Obese"

bmi_category = np.array([bmi_class(b) for b in bmi])

# ----------------------------------------------------------------------
# 6. Occupation risk class
# ----------------------------------------------------------------------
occupation_risk_class = np.random.choice(
    ["Low", "Medium", "High"], size=N_CASES, p=[0.55, 0.32, 0.13]
)

# ----------------------------------------------------------------------
# 7. Income band - drives sum assured capacity
# ----------------------------------------------------------------------
income_bands = ["<5L", "5-10L", "10-25L", "25-50L", "50L+"]
income_weights = [0.18, 0.32, 0.30, 0.14, 0.06]
income_band = np.random.choice(income_bands, size=N_CASES, p=income_weights)

# ----------------------------------------------------------------------
# 8. Plan type & rider attachment
#    - Term life dominates, ULIP/Savings rises with income band
#    - Riders (CI/TPD) more common among 30-50 age band and Term buyers
# ----------------------------------------------------------------------
def choose_plan_type(inc):
    if inc in ["25-50L", "50L+"]:
        p = [0.40, 0.20, 0.40]  # Term, Whole Life, Savings/ULIP
    else:
        p = [0.58, 0.20, 0.22]
    return np.random.choice(["Term Life", "Whole Life", "Savings/ULIP"], p=p)

plan_type = np.array([choose_plan_type(i) for i in income_band])

def choose_rider(pt, a):
    # Rider attach probability higher for term life, mid-age applicants
    base = 0.28 if pt == "Term Life" else 0.15
    if 30 <= a <= 50:
        base += 0.10
    r = np.random.rand()
    if r < base * 0.55:
        return "CI"          # Critical Illness
    elif r < base * 0.85:
        return "TPD"          # Total & Permanent Disability
    elif r < base:
        return "CI+TPD"
    else:
        return "None"

rider_type = np.array([choose_rider(pt, a) for pt, a in zip(plan_type, age)])

# ----------------------------------------------------------------------
# 9. Sum assured - scales with income band and plan type
# ----------------------------------------------------------------------
income_multiplier = {
    "<5L": (300000, 700000),
    "5-10L": (500000, 1500000),
    "10-25L": (1000000, 3000000),
    "25-50L": (2500000, 7000000),
    "50L+": (5000000, 20000000),
}

def gen_sum_assured(inc, pt):
    low, high = income_multiplier[inc]
    val = np.random.uniform(low, high)
    if pt == "Whole Life":
        val *= 0.85
    elif pt == "Savings/ULIP":
        val *= 0.6
    return round(val, -3)  # round to nearest thousand

sum_assured = np.array([gen_sum_assured(i, p) for i, p in zip(income_band, plan_type)])

# ----------------------------------------------------------------------
# 10. Medical condition flag - probability rises with age, BMI, smoker
# ----------------------------------------------------------------------
conditions = ["None", "Diabetes", "Hypertension", "Cardiac", "Obesity", "Respiratory"]

def choose_medical_condition(a, b, smoker):
    # base risk score
    risk = 0.05
    risk += max(0, (a - 30)) * 0.012          # age effect
    risk += max(0, (b - 25)) * 0.03            # bmi effect
    risk += 0.12 if smoker == "Yes" else 0     # smoker effect
    risk = min(risk, 0.85)

    if np.random.rand() > risk:
        return "None"

    # distribute among conditions with age/bmi influenced weights
    weights = np.array([
        0.30 + (0.01 if a > 45 else 0),   # Diabetes
        0.28 + (0.01 if a > 45 else 0),   # Hypertension
        0.15 + (0.01 if a > 50 else 0),   # Cardiac
        0.17 + (0.02 if b > 30 else 0),   # Obesity
        0.10,                              # Respiratory
    ])
    weights = weights / weights.sum()
    return np.random.choice(conditions[1:], p=weights)

medical_condition_flag = np.array([
    choose_medical_condition(a, b, s) for a, b, s in zip(age, bmi, smoker_status)
])

# ----------------------------------------------------------------------
# 11. Underwriting decision + premium loading - driven by a composite
#     risk score (age, bmi, smoker, medical condition, occupation risk)
# ----------------------------------------------------------------------
condition_risk_weight = {
    "None": 0.0, "Diabetes": 0.35, "Hypertension": 0.25,
    "Cardiac": 0.5, "Obesity": 0.2, "Respiratory": 0.3
}
occ_risk_weight = {"Low": 0.0, "Medium": 0.15, "High": 0.35}

def composite_risk(a, b, smoker, cond, occ):
    score = 0.0
    score += max(0, (a - 30)) * 0.01
    score += max(0, (b - 25)) * 0.02
    score += 0.20 if smoker == "Yes" else 0
    score += condition_risk_weight[cond]
    score += occ_risk_weight[occ]
    return score

risk_score = np.array([
    composite_risk(a, b, s, c, o)
    for a, b, s, c, o in zip(age, bmi, smoker_status, medical_condition_flag, occupation_risk_class)
])

def decision_and_loading(score):
    if score < 0.35:
        return "Standard", 0.0
    elif score < 0.55:
        loading = round(np.random.uniform(10, 50), 0)
        return "Rated", loading
    elif score < 0.75:
        loading = round(np.random.uniform(50, 150), 0)
        return "Rated", loading
    elif score < 0.90:
        return "Postponed", np.nan
    else:
        return "Declined", np.nan

decisions = [decision_and_loading(s) for s in risk_score]
decision = np.array([d[0] for d in decisions])
premium_loading_pct = np.array([d[1] for d in decisions])

# ----------------------------------------------------------------------
# 12. Distribution partner (kept generic - NOT real company names, to
#     avoid implying this is real client data)
# ----------------------------------------------------------------------
partner = np.random.choice(
    ["Partner A", "Partner B", "Partner C", "Partner D"],
    size=N_CASES, p=[0.35, 0.30, 0.20, 0.15]
)

# ----------------------------------------------------------------------
# Assemble dataframe
# ----------------------------------------------------------------------
case_ids = [f"UW{str(i).zfill(6)}" for i in range(1, N_CASES + 1)]

df = pd.DataFrame({
    "case_id": case_ids,
    "application_date": application_dates,
    "age": age,
    "age_band": age_bands,
    "gender": gender,
    "smoker_status": smoker_status,
    "bmi": bmi,
    "bmi_category": bmi_category,
    "occupation_risk_class": occupation_risk_class,
    "income_band": income_band,
    "plan_type": plan_type,
    "rider_type": rider_type,
    "sum_assured": sum_assured,
    "medical_condition_flag": medical_condition_flag,
    "risk_score": risk_score.round(3),
    "decision": decision,
    "premium_loading_pct": premium_loading_pct,
    "distribution_partner": partner,
})

df = df.sort_values("application_date").reset_index(drop=True)

# ----------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------
output_path = "underwriting_cases.csv"
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} rows -> {output_path}")
print("\nQuick sanity checks:")
print(df["decision"].value_counts(normalize=True).round(3))
print("\nMedical condition prevalence by age band:")
print(pd.crosstab(df["age_band"], df["medical_condition_flag"], normalize="index").round(2))
print("\nRider attachment rate by plan type:")
print(pd.crosstab(df["plan_type"], df["rider_type"] != "None", normalize="index").round(2))
