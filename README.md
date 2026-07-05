# Volatility-Modeling

Author:** Dzandu Selorm (dzand-cmd)  
**Project Type:** Quantitative Research  
**Language:** Python  
**Status:** Complete 

---

## Overview

This project implements a volatility modeling framework for analyzing and forecasting asset return volatility using statistical time series methods. It focuses on estimating time-varying volatility and evaluating how well different models capture market risk dynamics.

The objective is to understand and model volatility clustering, persistence, and mean-reversion behavior in financial returns.

## Project Structure

volatility_modeling/
│
├── volatility_modeling.py   # Core volatility estimation and analysis
│
├── gitignore                    
├── README.md                    # Project documentation


## Core Features
- Computation of historical volatility from returns
- Rolling volatility estimation
- Volatility clustering analysis
- Statistical evaluation of volatility behavior
- Visualization of volatility over time
- Comparison of different volatility estimators


## Methodology
This project focuses on modeling the time-varying nature of financial volatility:

- Returns are computed from price series
- Volatility is estimated using rolling windows
- Statistical properties such as persistence and clustering are analyzed
- Optional comparison against baseline constant-volatility assumptions

## Key idea:
Volatility is not constant — it clusters and evolves over time.


## How to run

git clone https://github.com/dzand-cmd/volatility_modeling.git
cd volatility_modeling
python volatility_modeling.py

