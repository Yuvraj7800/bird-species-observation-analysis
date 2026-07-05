# 🐦 Bird Species Observation Analysis

> End-to-end data science project analyzing the **distribution and diversity of bird species** across Forest and Grassland ecosystems in **11 National Parks** — featuring interactive Streamlit dashboard, SQL analysis, and Plotly visualizations.

---

## 🚀 Live App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]https://bird-species-observation-analysis-nlhtalpokzejef9wpbhgab.streamlit.app


---

## 📊 Dataset Summary

| Metric | Value |
|--------|-------|
| Total Observations | 17,077 |
| Forest Observations | 8,546 |
| Grassland Observations | 8,531 |
| Unique Bird Species | 127 |
| Unique Plots | 609 |
| National Parks Covered | 11 |
| Observers | 3 |
| Year | 2018 |

---

## 🧠 Methodology

1. **Data Loading** — Loaded all 11 sheets from both Forest and Grassland Excel files and merged into one combined dataset
2. **Data Cleaning** — Handled missing values, standardized columns, aligned schema differences between Forest and Grassland files
3. **Exploratory Data Analysis** — Temporal, Spatial, Species, Environmental, Distance, Observer, and Conservation analyses
4. **SQL Analysis** — SQLite in-memory database for structured querying
5. **Visualization** — Interactive Plotly charts embedded in Streamlit dashboard

---

## 🏆 Key Findings

| Finding | Value |
|---------|-------|
| Most Observed Species | Northern Cardinal (1,160 obs) |
| Top Biodiversity Park | Monocacy National Battlefield (100 species) |
| Most Common ID Method | Singing (57.7% of observations) |
| At-Risk Species (PIF Watchlist) | 8 species, 378 observations (2.2%) |
| Most At-Risk Species | Wood Thrush (309 observations) |
| Peak Season | Summer (11,481 observations) |
| Avg Temperature | 22.6°C |
| Avg Humidity | 73.7% |

---

## 🎯 Analysis Modules

| Module | Description |
|--------|-------------|
| 🕐 Temporal Analysis | Seasonal trends, monthly patterns, observation time windows |
| 🗺️ Spatial Analysis | Admin unit comparisons, plot-level biodiversity hotspots |
| 🦅 Species Analysis | Diversity metrics, sex ratio, activity patterns |
| 🌤️ Environmental Conditions | Temperature, humidity, sky, wind impact on observations |
| 📏 Distance & Behavior | Flyover vs non-flyover, distance distribution |
| 👁️ Observer Trends | Observer bias, visit patterns, species diversity per observer |
| 🚨 Conservation Insights | PIF Watchlist species, regional stewardship priorities |
| 🗄️ SQL Queries | Live SQL analysis with preset and custom queries |

---

## 🚨 Conservation Status

- **8 at-risk species** on PIF Watchlist
- **Wood Thrush** most at-risk — 309 observations
- **Worm-eating Warbler, Prairie Warbler, Cerulean Warbler** also flagged
- Forest habitat shows higher watchlist species concentration

---

## 📁 Project Structure

```
bird-species-observation-analysis/
├── dashboard.py                              # Streamlit app (9 tabs)
├── Bird_Monitoring_Data_FOREST.XLSX          # Forest dataset (11 sheets)
├── Bird_Monitoring_Data_GRASSLAND.XLSX       # Grassland dataset (11 sheets)
├── Bird_Species_Observation_Analysis.ipynb   # Full EDA notebook
├── Bird_Species_Analysis.pptx               # Project presentation
├── requirements.txt
└── README.md
```

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

> ⚠️ Both Excel files must be in the **same folder** as `dashboard.py`

---

## 🏞️ National Parks Covered

| Code | Park Name |
|------|-----------|
| ANTI | Antietam National Battlefield |
| CATO | Catoctin Mountain Park |
| CHOH | Chesapeake & Ohio Canal NHP |
| GWMP | George Washington Memorial Pkwy |
| HAFE | Harpers Ferry NHP |
| MANA | Manassas National Battlefield |
| MONO | Monocacy National Battlefield |
| NACE | National Capital East Parks |
| PRWI | Prince William Forest Park |
| ROCR | Rock Creek Park |
| WOTR | Wolf Trap National Park |

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white)

**Libraries:** Pandas · NumPy · Plotly · Streamlit · SQLite3 · Matplotlib · Seaborn · Statsmodels · OpenPyXL
