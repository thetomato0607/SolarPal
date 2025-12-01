# SolarPal → VPP Trading Terminal: Restructure Guide

## New Project Architecture

```
SolarPal/
├── app.py                          # Main Streamlit dashboard (NEW)
├── .streamlit/
│   └── config.toml                 # Dark theme configuration (NEW)
├── modules/                        # Core engines (NEW)
│   ├── __init__.py
│   ├── optimization.py             # Battery arbitrage optimizer
│   ├── grid_physics.py             # Grid constraint checker
│   ├── market_data.py              # UK price/solar generators
│   └── visualization.py            # Plotly chart builders
├── backend/                        # Keep VPP engine (optional API)
│   ├── vpp_engine.py               # Core optimization logic
│   ├── main.py                     # FastAPI server (optional)
│   └── routes/
│       └── vpp.py
├── docs/                           # Documentation (NEW)
│   ├── VPP_INTEGRATION_GUIDE.md
│   └── INTERVIEW_GUIDE.md
└── requirements.txt                # Updated dependencies

FILES TO DELETE:
├── backend/routes/
│   ├── tips.py                     # DELETE (homeowner tips)
│   ├── onboarding.py               # DELETE (educational flow)
│   └── summary.py                  # DELETE (simple summary)
├── backend/db/
│   └── fake_db.py                  # DELETE (no database needed)
├── backend/utils/
│   └── dummy_data.py               # DELETE (replaced by modules)
├── solarpal-frontend/              # DELETE ENTIRE FOLDER (React replaced by Streamlit)
└── Any .html, .css, .json files    # DELETE (no web templates needed)
```

---

## Step 1: Create Module Structure
