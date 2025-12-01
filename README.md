# ⚡ VPP Trading Terminal

> **Professional Virtual Power Plant simulation platform for grid-connected battery arbitrage**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 What This Is

A **Bloomberg-terminal style** energy trading dashboard that optimizes residential battery systems for maximum profit while respecting physical grid constraints.

**Target Audience:** Quantitative traders, grid engineers, energy market analysts

**Key Innovation:** Uses **Linear Programming** to mathematically guarantee grid compliance while maximizing arbitrage revenue—no heuristics, no guesswork.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/SolarPal.git
cd SolarPal
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run app.py
```

**Opens at:** `http://localhost:8501`

---

## 💡 Features

### 1. **Market Engine** (Financial Optimization)
- Linear Programming solver for battery arbitrage
- Maximizes revenue through price-based charge/discharge
- Realistic UK "duck curve" price simulation
- Sharpe ratio and risk-adjusted returns

### 2. **Grid Engine** (Physical Constraints)
- DNO G99 compliance checking
- Voltage rise calculation (±10% limit)
- Transformer thermal limits
- Automatic violation detection

### 3. **Interactive Dashboard**
- Dark-mode Bloomberg-style UI
- Real-time optimization (< 0.5s solve time)
- Configurable scenarios (volatility, cloud cover)
- Professional Plotly visualizations

---

## 📊 Screenshots

### Main Dashboard
![Dashboard](docs/images/dashboard.png)
*Bloomberg-terminal style metrics: Profit, Payback, Sharpe Ratio, Grid Compliance*

### Financial Optimization
![Price Chart](docs/images/price_chart.png)
*Market price vs. battery actions—buy low, sell high*

### Grid Constraint Enforcement
![Grid Chart](docs/images/grid_chart.png)
*Net export vs. DNO limit—red line never exceeded*

---

## 🧠 How It Works

### The Optimization Problem

```
Objective:
    Maximize Σ(Grid_Export × Price × dt)

Subject to:
    1. Battery capacity: 0 <= SoC <= 13.5 kWh
    2. Power limits: |Charge|, |Discharge| <= 5 kW
    3. Grid limit: Net_Export <= 4.0 kW  ← THE KEY CONSTRAINT
    4. Energy conservation: SoC dynamics with 90% efficiency
```

**Solver:** SciPy's HiGHS (interior-point Linear Programming)

### Why This Matters

Without optimization, a battery might discharge at high prices while solar is generating, exceeding the grid export limit:

```
❌ Naive Strategy:
Solar: 3 kW
Battery discharge: 5 kW
→ Net export: 8 kW (exceeds 4 kW limit!)
→ Transformer overload, voltage rise > 10%, £20k DNO fine

✅ LP-Constrained:
Optimizer automatically curtails discharge to 1 kW
→ Net export: 4 kW (exactly at limit)
→ Revenue loss: £1.20 | Penalty avoided: £20k+
```

The grid constraint is **mathematically guaranteed** by the LP solver.

---

## 📁 Project Structure

```
SolarPal/
├── app.py                      # Main Streamlit dashboard
├── .streamlit/
│   └── config.toml             # Dark theme configuration
├── modules/                    # Core optimization engines
│   ├── optimization.py         # LP solver (BatteryOptimizer)
│   ├── grid_physics.py         # Grid violation checker
│   ├── market_data.py          # UK price/solar generator
│   └── visualization.py        # Plotly chart builders
├── backend/                    # Optional FastAPI (for API access)
│   ├── vpp_engine.py
│   ├── main.py
│   └── routes/vpp.py
├── docs/                       # Documentation
│   ├── VPP_INTEGRATION_GUIDE.md
│   ├── INTERVIEW_GUIDE.md
│   └── PROJECT_RESTRUCTURE.md
└── requirements.txt
```

---

## 🔧 Configuration

### Scenario Parameters (Sidebar)

**Asset:**
- Battery capacity: 5-20 kWh (default: 13.5 kWh)
- Inverter limit: 2-10 kW (default: 5 kW)
- Grid export limit: 2-8 kW (default: 4 kW)

**Market:**
- Price volatility: 1x-5x (1x = normal, 5x = extreme)
- Solar noise: 0-1 (0 = clear sky, 1 = heavy clouds)
- System size: 1-10 kWp
- Daily load: 5-30 kWh

---

## 📈 Example Results

### Typical Daily Performance:
```
Net Profit:              £1.91
Annual Projection:       £697
Payback Period:          10.0 years
Sharpe Ratio:            2.34
Grid Compliance:         ✅ 100%
Max Grid Export:         4.00 kW (at limit)
Violations:              0
```

### Financial Breakdown:
```
Revenue (Export):        £3.08
Cost (Import):           £1.17
Baseline (No Battery):   -£0.29
Battery Benefit:         +£2.20/day
```

---

## 💻 Technical Stack

- **Backend:** Python 3.9+, SciPy, NumPy
- **Optimization:** Linear Programming (HiGHS solver)
- **Frontend:** Streamlit (dark mode)
- **Visualization:** Plotly (interactive charts)
- **Optional API:** FastAPI + Uvicorn

---

## 🎓 Use Cases

### For Students/Portfolio:
- Demonstrates professional-grade optimization
- Shows understanding of power systems constraints
- Interview-ready talking points (see [INTERVIEW_GUIDE.md](docs/INTERVIEW_GUIDE.md))

### For Researchers:
- Extensible framework for VPP studies
- Easy to add stochastic programming, MPC, degradation models
- Scales to fleet-level aggregation

### For Industry:
- Production-ready optimization engine
- API available for integration
- Fast (<0.5s solve time per 24h horizon)

---

## 🔬 Advanced Features

### Coming Soon:
1. **Stochastic Programming:** Handle forecast uncertainty
2. **Model Predictive Control:** Rolling horizon optimization
3. **Battery Degradation:** Cycle-wear cost modeling
4. **Frequency Response:** FFR/DFS grid services
5. **Fleet Aggregation:** Multi-home coordination

### Extensibility:
The modular architecture makes it easy to add:
- Real weather APIs (OpenWeatherMap)
- Live pricing (Octopus Agile API)
- Hardware interfaces (Tesla Powerwall API)
- Machine learning forecasts

---

## 📚 Documentation

- **Integration Guide:** [VPP_INTEGRATION_GUIDE.md](VPP_INTEGRATION_GUIDE.md)
- **Interview Prep:** [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)
- **Cleanup Guide:** [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md)

---

## 🤝 Contributing

This is a portfolio project, but suggestions welcome!

**Areas for contribution:**
- Real-world data integration
- Alternative solvers (Gurobi, CPLEX)
- Additional grid services (reactive power, inertia)
- Validation against real battery systems

---

## 📝 License

MIT License - Free to use for educational and portfolio purposes.

---

## 👨‍💻 Author

**SolarPal Team**

Built to demonstrate quantitative optimization and power systems engineering for energy sector recruitment.

**Contact:** [Your Email / LinkedIn]

---

## 🙏 Acknowledgments

- **Inspiration:** National Grid ESO's VPP strategy
- **Physics:** UK Power Networks G99 technical guidance
- **Optimization:** SciPy developers for robust LP solvers
- **Market Data:** Representative of UK day-ahead prices

---

## 📊 Performance Metrics

**Optimization Speed:**
- Problem size: 289 variables, ~400 constraints
- Solve time: <0.5 seconds (96 intervals @ 15-min resolution)
- Scalable to: 1000+ homes (fleet-level)

**Algorithm:**
- Method: Linear Programming (convex optimization)
- Solver: HiGHS (modern interior-point)
- Guarantee: Global optimum (no local minima)

---

**⚡ Built with Python, SciPy, Streamlit, and a passion for clean energy systems ⚡**

---

## 🚨 Important Notes

### Grid Constraints:
The 4 kW export limit represents typical UK DNO G99 connection limits. Exceeding this causes:
- Voltage rise > ±10% (statutory limit)
- Transformer thermal overload
- Protection relay trips
- £20k+ DNO penalties

### Optimization Method:
We use Linear Programming (not heuristics) because:
- **Provable optimality:** Guarantees best solution
- **Constraint enforcement:** Mathematically ensures grid limit satisfaction
- **Fast:** Solves in real-time (<0.5s)
- **Explainable:** Can justify decisions to regulators

### For Recruiters:
This project demonstrates:
✅ Quantitative optimization (LP formulation)
✅ Domain expertise (UK energy markets, G99 regs)
✅ System design (modular architecture)
✅ Production thinking (fast solvers, API-ready)
✅ Communication (professional documentation)

**Key Talking Point:** *"The grid constraint is enforced as an LP inequality, guaranteeing compliance without manual checks—this is production-grade DNO integration."*

---

**Ready to impress energy quants and grid engineers!** 🎯
