# 706-Final-Project-Group-1



The **main Streamlit app file is `main_dashboard_trial.py`**.

# Global Health Trends: Linking Health Determinants, Coverage, and Child Survival

Authors: Brittany Bustos, Anya Sharma, Radhika Sonthalia  

Streamlit app: https://706-final-project-group-1-lycyd8p8ef3rf47eqwxneg.streamlit.app/  
GitHub repo: https://github.com/radhikasonthalia/706-Final-Project-Group-1.git  

---

## Overview

This project is an interactive Streamlit dashboard that explores global patterns in:

- **Health determinants** (economic status, education, electricity access, etc.)
- **Immunization coverage** (as a proxy for access to essential health services)
- **Under‑5 mortality** (as a key child survival outcome)

Our goal is to help users see how baseline living conditions and service coverage are linked to child survival, and to highlight which countries and population groups face the greatest disadvantages and inequities.

Target users include:
- General public interested in global health fairness and progress  
- Public health researchers, students, and policymakers who want quick, visual, cross‑country comparisons and hypothesis generation

---

## Data

We use disaggregated global health inequality data from the **WHO Health Inequality Data Repository**, focusing on three domains across up to ~198 countries:

- **Health determinants**: economic status, education, electricity access, etc.  
- **Immunizations**: vaccination coverage in 1‑year‑olds  
- **Under‑5 mortality**: deaths per 1,000 live births  

Key variable types include:
- Categorical: Country/Setting, WHO Region, Sex, Subnational Region  
- Temporal: Year/Date  
- Quantitative: Mortality rates, vaccination coverage, income share, electricity access  
- Ordinal: Economic status (wealth quintiles), education level  

Each record represents an indicator value for a given country, year, and inequality dimension (e.g., sex, economic quintile, education, urban/rural).

---

## Main Analysis Tasks in the App

1. **Health Determinants – Baseline Conditions**  
   Visualize how economic status, education, and housing conditions (e.g., electricity) vary within countries to identify underlying structural disadvantages.

2. **Immunization Coverage – Access to Services**  
   Explore trends in vaccination coverage over time, by country and subgroup, to reveal progress, stagnation, or reversals in access to essential health services.

3. **Under‑5 Mortality – Real‑World Outcomes**  
   Examine under‑5 mortality patterns and how they track with determinants and coverage, including differences by sex and economic status.

Together, these views help distinguish between countries where conditions are uniformly poor and those with stark internal disparities.

---









