# AI-POWERED REVENUE FORECASTING AGENT SYSTEM
## Mid-Year Review Report

**Project**: Time Series Revenue Forecasting with MAPE/WMAPE Analysis

**Prepared by**: Hariharan Balaji

**Organization**: o9 Solutions

**Date**: June 2026

---

## ABSTRACT

Revenue forecasting accuracy is a critical challenge in supply chain and retail planning. This project designs and develops an AI-powered agentic system capable of autonomously analyzing large-scale revenue data, generating time series forecasts, and evaluating forecast accuracy using industry-standard metrics.

The system ingests a North America (NA) retail revenue dataset comprising 276,577 rows across 10 dimensions — including location, channel, product planning level, and monthly time periods spanning July 2021 to December 2025. Using a multi-agent orchestration framework built on OpenAI's agent SDK, the system automatically identifies the forecast horizon start point (July 2024), trains forecasting models on historical statistical actuals, and generates forward-looking revenue projections.

The forecasting engine employs Holt-Winters Exponential Smoothing with a damped trend component, with a fallback to Simple Moving Average when training data is insufficient. Forecast accuracy is measured using two complementary metrics: Mean Absolute Percentage Error (MAPE) and Weighted MAPE (WMAPE). WMAPE results from the existing Final Revenue Forecast stood at **12.49% for the United States of America** and **35.4% for Canada**, indicating good accuracy for the US market and a need for improvement in the Canada market. The comparison study confirms that the existing enterprise forecast outperforms the statistically generated baseline for both locations, providing a clear benchmark for future model improvement.

The system's modular architecture supports extension to additional dimensions including channel-level and product-planning-level forecasting, and is designed to integrate into production planning workflows at o9 Solutions.

---

## TABLE OF CONTENTS

1. [System Architecture & Modules](#1-system-architecture--modules)
2. [Functional Description](#2-functional-description)
3. [Technical Specifications](#3-technical-specifications)
4. [Design Considerations](#4-design-considerations)
5. [Results & Key Findings](#5-results--key-findings)
6. [Future Plan](#6-future-plan)
7. [Abbreviations](#7-abbreviations)

---

## 1. SYSTEM ARCHITECTURE & MODULES

The system is composed of the following major modules:

**(a) Data Ingestion & Preparation Module**
**(b) Forecast Horizon Identification Module**
**(c) Time Series Forecasting Engine**
**(d) MAPE / WMAPE Calculation Module**
**(e) Forecast Comparison & Recommendation Module**
**(f) Multi-Agent Orchestration Layer**
**(g) Output & Reporting Module**

---

### Module Descriptions

**a) Data Ingestion & Preparation Module**
Loads the source CSV file (`Rev_NA.csv`) containing 276,577 rows of North America retail revenue data. Parses the `Time.[Retail Planning Month]` column (format: `Jul-21`) into datetime objects, sorts records by location and time, and validates data completeness. The dataset covers 54 monthly periods, 75 sales channels, 250 product planning levels, and 2 locations (USA and Canada).

**b) Forecast Horizon Identification Module**
Automatically identifies the forecast start month for each location by detecting the first month where `Final Revenue Forecast` values are present. For both USA and Canada, this was determined to be **July 2024**. All data prior to this point is designated as the training window for model fitting.

**c) Time Series Forecasting Engine**
For each location, builds a time series model on historical `Stat Actual Amt` values prior to the forecast start month. The primary algorithm is **Holt-Winters Exponential Smoothing** with an additive damped trend, implemented via `statsmodels`. A Simple Moving Average (3-period window) serves as the fallback when training data is insufficient or the model fails to converge.

**d) MAPE / WMAPE Calculation Module**
Computes two forecast accuracy metrics:

- **MAPE** (Mean Absolute Percentage Error): Simple average of absolute percentage errors across all periods where actuals exist.
- **WMAPE** (Weighted MAPE): Weights each period's error by its actual value magnitude, reducing the influence of low-volume periods. Formula:

```
WMAPE = Σ |Actual - Forecast| / Σ |Actual| × 100
```

Both metrics are computed at the `Location.[Country]` granularity.

**e) Forecast Comparison & Recommendation Module**
Compares the MAPE/WMAPE of the system-generated forecast against the existing enterprise `Final Revenue Forecast`. Determines and outputs which forecast provides better accuracy (lower error) for each location, and issues a recommendation.

**f) Multi-Agent Orchestration Layer**
Built on the OpenAI Agent SDK, the orchestration layer coordinates specialized agents — including a Manager agent, a Data Analysis agent, an EDA (Exploratory Data Analysis) agent, and a Code Execution agent — in a group-chat pattern. Each agent handles a discrete task, and the Manager routes tasks to the appropriate specialist.

**g) Output & Reporting Module**
Produces structured outputs:
- `forecast_analysis.csv` — MAPE comparison results per location
- `WMape_by_Location.csv` — WMAPE results per location
- `forecast_summary.txt` — Human-readable summary with methodology, results, and recommendation

---

## 2. FUNCTIONAL DESCRIPTION

The end-to-end data flow is as follows:

1. **Input**: Raw revenue CSV (`Rev_NA.csv`) with actuals, forecasts, and baseline forecasts across location, channel, product, and time dimensions.
2. **Preparation**: Time parsing, sorting, and null handling applied. Data split by location.
3. **Training Window**: For each location, all rows where `Month < Forecast_Start_Month` form the training set.
4. **Model Fitting**: Exponential Smoothing fitted on aggregated monthly `Stat Actual Amt` values.
5. **Forecast Generation**: Model projects revenue for the forecast horizon (July 2024 – December 2025).
6. **Accuracy Evaluation**: Generated forecast and existing `Final Revenue Forecast` both compared against realized actuals using MAPE and WMAPE.
7. **Comparison & Output**: Lower-error forecast declared as the better model; results written to output files.

### Key Interface Points

| Interface | Description |
|-----------|-------------|
| Input CSV | `generated_code/Input/Rev_NA.csv` — source revenue data |
| Agent Orchestration | OpenAI Agent SDK group-chat with Manager, Analyst, EDA, and Executor agents |
| Forecasting Library | `statsmodels.tsa.holtwinters.ExponentialSmoothing` |
| Data Processing | `pandas`, `numpy` |
| Output Files | CSV and TXT reports in `generated_code/Output/` |

---

## 3. TECHNICAL SPECIFICATIONS

| # | Parameter | Specification |
|---|-----------|---------------|
| 1 | Dataset | Rev_NA.csv — North America Retail Revenue |
| 2 | Dataset Size | 276,577 rows × 10 columns (130 MB) |
| 3 | Time Granularity | Monthly (54 periods: Jul-21 to Dec-25) |
| 4 | Locations | USA, Canada |
| 5 | Channels | 75 unique MPU Level 3 channels |
| 6 | Products | 250 product planning levels |
| 7 | Forecast Start | July 2024 (auto-detected for both locations) |
| 8 | Forecasting Method | Holt-Winters Exponential Smoothing (damped trend) |
| 9 | Fallback Method | Simple Moving Average (3-period window) |
| 10 | Accuracy Metrics | MAPE, WMAPE |
| 11 | WMAPE — USA | 12.49% |
| 12 | WMAPE — Canada | 35.4% |
| 13 | Agent Framework | OpenAI Agent SDK (multi-agent group-chat) |
| 14 | Language | Python 3.x |
| 15 | Libraries | pandas, numpy, statsmodels |
| 16 | Output Formats | CSV, TXT |
| 17 | Benchmark Result | Existing Final Revenue Forecast outperforms generated forecast for both locations |

---

## 4. DESIGN CONSIDERATIONS

- **Modularity**: Each pipeline step (data prep, forecast identification, model fitting, MAPE calculation) is implemented as an independent function, enabling isolated testing and reuse.
- **Fallback Robustness**: The system gracefully degrades from Exponential Smoothing to Moving Average when training data is insufficient, ensuring coverage for all locations.
- **Zero-value Handling**: MAPE calculation explicitly excludes rows where actual = 0 to avoid division errors and misleading error values.
- **Multi-Agent Architecture**: Separating concerns across specialized agents (Manager, EDA, Analyst, Executor) mirrors production-grade agentic design patterns and enables parallel task delegation.
- **Extensibility**: The location-level aggregation design can be extended to channel-level and product-level granularity without architectural changes.
- **WMAPE over MAPE**: WMAPE was chosen as the primary metric for business reporting as it down-weights low-revenue periods that would otherwise distort MAPE in a sparse dataset.

---

## 5. RESULTS & KEY FINDINGS

| Location | Forecast Start | WMAPE (Existing Forecast) | MAPE (Generated Forecast) | Better Forecast |
|----------|----------------|--------------------------|--------------------------|-----------------|
| USA | July 2024 | 12.49% | Very High | Existing Forecast |
| Canada | July 2024 | 35.4% | Very High | Existing Forecast |

**Key Observations:**
- The existing enterprise `Final Revenue Forecast` significantly outperforms the statistically generated baseline for both locations.
- USA forecast accuracy (WMAPE 12.49%) is within the "good" range (10–20%).
- Canada forecast accuracy (WMAPE 35.4%) is above the acceptable threshold and warrants investigation.
- The generated Exponential Smoothing forecast shows high MAPE, indicating the model requires parameter tuning, seasonal decomposition, or a richer feature set to be competitive.

---

## 6. FUTURE PLAN

| # | Phase | Timeline | Work to be Done | Status |
|---|-------|----------|-----------------|--------|
| 1 | Data Exploration & Planning | Jan 2026 – Feb 2026 | Data profiling, EDA, implementation plan | COMPLETED |
| 2 | Agent Framework Setup | Feb 2026 – Mar 2026 | Multi-agent orchestration, Manager/Analyst/Executor agent design | COMPLETED |
| 3 | Forecasting Engine (v1) | Mar 2026 – Apr 2026 | Exponential Smoothing implementation, MAPE/WMAPE calculation | COMPLETED |
| 4 | Accuracy Benchmarking | Apr 2026 – May 2026 | Comparison of generated vs existing forecast, WMAPE reporting | COMPLETED |
| 5 | Model Improvement | Jun 2026 – Jul 2026 | Parameter tuning, ARIMA/Holt-Winters with seasonality, channel-level WMAPE | IN PROGRESS |
| 6 | Channel & Product Drill-down | Jul 2026 – Aug 2026 | Extend analysis to channel and product planning level granularity | PENDING |
| 7 | Production Integration | Aug 2026 – Sep 2026 | Integrate agent pipeline into o9 Solutions planning workflows | PENDING |
| 8 | Final Review & Documentation | Sep 2026 | Full system documentation and sign-off | PENDING |

---

## 7. ABBREVIATIONS

| Term | Expansion |
|------|-----------|
| ARIMA | Autoregressive Integrated Moving Average |
| CSV | Comma-Separated Values |
| EDA | Exploratory Data Analysis |
| ETS | Error-Trend-Seasonality (Exponential Smoothing family) |
| MAPE | Mean Absolute Percentage Error |
| MPU | Merchandise Planning Unit |
| NA | North America |
| SDK | Software Development Kit |
| WMAPE | Weighted Mean Absolute Percentage Error |
| LLM | Large Language Model |
| API | Application Programming Interface |
| GSA | General Sporting Accounts |
