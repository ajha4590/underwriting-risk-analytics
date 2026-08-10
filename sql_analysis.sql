-- ============================================================
-- Life Insurance Underwriting Analytics
-- SQL Schema + Analysis Queries
-- Load underwriting_cases.csv into a table called `underwriting_cases`
-- (SQLite / PostgreSQL / MySQL compatible with minor syntax tweaks)
-- ============================================================

-- ---------------------------------------------------
-- 1. Schema
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS underwriting_cases (
    case_id                 TEXT PRIMARY KEY,
    application_date        DATE,
    age                      INTEGER,
    age_band                 TEXT,
    gender                   TEXT,
    smoker_status            TEXT,
    bmi                      REAL,
    bmi_category              TEXT,
    occupation_risk_class     TEXT,
    income_band               TEXT,
    plan_type                 TEXT,
    rider_type                TEXT,
    sum_assured                REAL,
    medical_condition_flag    TEXT,
    risk_score                 REAL,
    decision                   TEXT,
    premium_loading_pct        REAL,
    distribution_partner       TEXT
);

-- ============================================================
-- 2. Portfolio Overview
-- ============================================================

-- 2.1 Monthly case volume trend across the year
SELECT
    strftime('%Y-%m', application_date) AS month,
    COUNT(*) AS total_cases
FROM underwriting_cases
GROUP BY month
ORDER BY month;

-- 2.2 Plan type mix (share of total cases)
SELECT
    plan_type,
    COUNT(*) AS cases,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM underwriting_cases), 1) AS pct_of_total
FROM underwriting_cases
GROUP BY plan_type
ORDER BY cases DESC;

-- 2.3 Case volume and average sum assured by distribution partner
SELECT
    distribution_partner,
    COUNT(*) AS cases,
    ROUND(AVG(sum_assured), 0) AS avg_sum_assured
FROM underwriting_cases
GROUP BY distribution_partner
ORDER BY cases DESC;

-- ============================================================
-- 3. Medical Risk Trends
-- ============================================================

-- 3.1 Medical condition prevalence by age band
SELECT
    age_band,
    medical_condition_flag,
    COUNT(*) AS cases,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY age_band), 1) AS pct_within_age_band
FROM underwriting_cases
GROUP BY age_band, medical_condition_flag
ORDER BY age_band, cases DESC;

-- 3.2 Decision outcome breakdown by medical condition
SELECT
    medical_condition_flag,
    decision,
    COUNT(*) AS cases,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY medical_condition_flag), 1) AS pct_within_condition
FROM underwriting_cases
GROUP BY medical_condition_flag, decision
ORDER BY medical_condition_flag, cases DESC;

-- 3.3 Average premium loading % by BMI category and smoker status
SELECT
    bmi_category,
    smoker_status,
    ROUND(AVG(premium_loading_pct), 1) AS avg_loading_pct,
    COUNT(*) AS cases
FROM underwriting_cases
WHERE decision = 'Rated'
GROUP BY bmi_category, smoker_status
ORDER BY avg_loading_pct DESC;

-- ============================================================
-- 4. Financial & Product Trends
-- ============================================================

-- 4.1 Average sum assured by age band and plan type
SELECT
    age_band,
    plan_type,
    ROUND(AVG(sum_assured), 0) AS avg_sum_assured,
    COUNT(*) AS cases
FROM underwriting_cases
GROUP BY age_band, plan_type
ORDER BY age_band, plan_type;

-- 4.2 Rider attachment rate by plan type
SELECT
    plan_type,
    ROUND(100.0 * SUM(CASE WHEN rider_type != 'None' THEN 1 ELSE 0 END) / COUNT(*), 1) AS rider_attach_rate_pct,
    COUNT(*) AS cases
FROM underwriting_cases
GROUP BY plan_type
ORDER BY rider_attach_rate_pct DESC;

-- 4.3 Rider attachment rate by age band (which age group buys CI/TPD most?)
SELECT
    age_band,
    ROUND(100.0 * SUM(CASE WHEN rider_type != 'None' THEN 1 ELSE 0 END) / COUNT(*), 1) AS rider_attach_rate_pct,
    COUNT(*) AS cases
FROM underwriting_cases
GROUP BY age_band
ORDER BY age_band;

-- 4.4 Income band vs plan type chosen (do higher earners prefer savings plans?)
SELECT
    income_band,
    plan_type,
    COUNT(*) AS cases,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY income_band), 1) AS pct_within_income_band
FROM underwriting_cases
GROUP BY income_band, plan_type
ORDER BY income_band, cases DESC;

-- 4.5 Overall underwriting decision mix (loss-ratio-style KPI)
SELECT
    decision,
    COUNT(*) AS cases,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM underwriting_cases), 1) AS pct_of_total
FROM underwriting_cases
GROUP BY decision
ORDER BY cases DESC;

-- 4.6 Year-over/quarter comparison ready view (useful for Tableau trend charts)
SELECT
    strftime('%Y-%m', application_date) AS month,
    plan_type,
    COUNT(*) AS cases,
    ROUND(AVG(risk_score), 3) AS avg_risk_score,
    ROUND(100.0 * SUM(CASE WHEN decision = 'Standard' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_standard
FROM underwriting_cases
GROUP BY month, plan_type
ORDER BY month, plan_type;
