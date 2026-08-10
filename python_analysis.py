"""
Life Insurance Underwriting Analytics - Python Analysis
----------------------------------------------------------
Loads the simulated underwriting_cases.csv dataset and performs:
  1. Exploratory data analysis (trend + distribution checks)
  2. A risk classification model predicting whether a case will be
     "Rated" (i.e. requires extra premium loading) based on
     age, BMI, smoker status, medical condition, and occupation risk
  3. Feature importance analysis (what actually drives a Rated decision)
  4. A chi-square test checking whether rider attachment (CI/TPD) is
     significantly associated with age band

Run: python python_analysis.py
Outputs: prints summary stats + saves 3 charts as PNG for reference
(main dashboard visuals live in Tableau - see README)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

df = pd.read_csv(
    "underwriting_cases.csv",
    parse_dates=["application_date"],
    keep_default_na=False,  # "None" is a real category here, not a missing value
    na_values=[],
)

print("=" * 60)
print("1. BASIC PORTFOLIO OVERVIEW")
print("=" * 60)
print(f"Total cases: {len(df):,}")
print(f"Date range: {df['application_date'].min().date()} to {df['application_date'].max().date()}")
print("\nDecision mix:")
print(df["decision"].value_counts(normalize=True).mul(100).round(1))

print("\nPlan type mix:")
print(df["plan_type"].value_counts(normalize=True).mul(100).round(1))

# ------------------------------------------------------------
# 2. Monthly trend chart
# ------------------------------------------------------------
monthly = df.groupby(df["application_date"].dt.to_period("M")).size()
plt.figure(figsize=(9, 4))
monthly.plot(kind="line", marker="o")
plt.title("Monthly Underwriting Case Volume")
plt.ylabel("Cases")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig("chart_monthly_volume.png", dpi=120)
plt.close()

# ------------------------------------------------------------
# 3. Medical condition prevalence by age band
# ------------------------------------------------------------
print("\n" + "=" * 60)
print("2. MEDICAL CONDITION PREVALENCE BY AGE BAND")
print("=" * 60)
prevalence = pd.crosstab(df["age_band"], df["medical_condition_flag"], normalize="index").mul(100).round(1)
print(prevalence)

prevalence.drop(columns=["None"], errors="ignore").plot(kind="bar", stacked=True, figsize=(9, 5))
plt.title("Medical Condition Prevalence by Age Band (%)")
plt.ylabel("% of cases in age band")
plt.tight_layout()
plt.savefig("chart_medical_prevalence.png", dpi=120)
plt.close()

# ------------------------------------------------------------
# 4. Chi-square test: is rider attachment associated with age band?
# ------------------------------------------------------------
print("\n" + "=" * 60)
print("3. CHI-SQUARE TEST: Rider attachment vs Age band")
print("=" * 60)
df["has_rider"] = df["rider_type"] != "None"
contingency = pd.crosstab(df["age_band"], df["has_rider"])
chi2, p_value, dof, expected = chi2_contingency(contingency)
print(contingency)
print(f"\nChi-square statistic: {chi2:.2f}")
print(f"p-value: {p_value:.6f}")
if p_value < 0.05:
    print("-> Statistically significant association between age band and rider attachment.")
else:
    print("-> No statistically significant association found.")

# ------------------------------------------------------------
# 5. Risk classification model: predict "Rated" decision
# ------------------------------------------------------------
print("\n" + "=" * 60)
print("4. RISK CLASSIFICATION MODEL (predicting a Rated decision)")
print("=" * 60)

model_df = df[df["decision"].isin(["Standard", "Rated"])].copy()
model_df["target"] = (model_df["decision"] == "Rated").astype(int)

feature_cols = [
    "age", "bmi", "smoker_status", "occupation_risk_class",
    "medical_condition_flag", "plan_type", "gender"
]

X = model_df[feature_cols].copy()
y = model_df["target"]

encoders = {}
for col in ["smoker_status", "occupation_risk_class", "medical_condition_flag", "plan_type", "gender"]:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

clf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred, target_names=["Standard", "Rated"]))
print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")

importances = pd.Series(clf.feature_importances_, index=feature_cols).sort_values(ascending=False)
print("\nFeature importance (what drives a Rated decision):")
print(importances.round(3))

importances.plot(kind="barh", figsize=(7, 4))
plt.title("Feature Importance - Predicting a 'Rated' Decision")
plt.xlabel("Importance")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("chart_feature_importance.png", dpi=120)
plt.close()

print("\nCharts saved: chart_monthly_volume.png, chart_medical_prevalence.png, chart_feature_importance.png")
print("\nDone. Load underwriting_cases.csv into Tableau for the full interactive dashboard.")
