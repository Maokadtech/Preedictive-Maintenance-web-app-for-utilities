# 🔧 Industrial IoT Predictive Maintenance Dashboard

A clean, modern Flask web application for monitoring and predicting industrial machine failures.

## Features

- **Dashboard** — KPI cards, failure charts, risk distribution, high-risk alerts, and live ML prediction
- **Machines** — Filterable grid view of all machines with status indicators
- **Machine Detail** — Deep dive into individual machine metrics and maintenance history
- **Analytics** — Monthly failure trends, correlation heatmap, and cost analysis
- **ML Prediction** — Random Forest model predicts failure probability from sensor inputs

## Installation

```bash
cd predictive_maintenance_app
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Overview with KPIs, charts, alerts, and prediction |
| Machines | `/machines` | Browse and filter all machines |
| Machine Detail | `/machine/<id>` | Detailed view of a single machine |
| Analytics | `/analytics` | Advanced charts and correlations |

## Tech Stack

- **Backend**: Flask, Pandas, Scikit-learn
- **Frontend**: Vanilla HTML/CSS/JS, Chart.js
- **ML**: Random Forest Classifier
