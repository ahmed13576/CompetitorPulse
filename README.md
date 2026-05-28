# CompetitorPulse ⚡ — Autonomous GTM Competitive Intelligence Agent

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Bright Data](https://img.shields.io/badge/Bright_Data-Web_Intelligence-FC6B3F?style=for-the-badge)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![AI Agents](https://img.shields.io/badge/AI-Multi_Agent_System-8B5CF6?style=for-the-badge)
![Hackathon](https://img.shields.io/badge/Web_Data_UNLOCKED-Hackathon-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **Track 1: GTM Intelligence** — Built for the [Web Data UNLOCKED Hackathon](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon) by lablab.ai × Bright Data

---

## 🚀 Overview

**CompetitorPulse** is an autonomous, multi-agent competitive intelligence system that monitors competitors across the live web and generates actionable **Sales Battlecards** for revenue teams. It replaces hours of manual research with always-on, structured web intelligence — powered by [Bright Data's](https://brightdata.com) infrastructure and Google's Gemini AI.

Sales, marketing, and revenue operations run on market knowledge. The web has all of it in real time — and most GTM teams still can't access it reliably or at scale. **CompetitorPulse changes that.**

### The Problem
- Sales reps walk into calls without knowing the competitor just changed their pricing yesterday.
- Product marketing teams manually track competitor websites for positioning shifts.
- Revenue leaders lack structured, real-time signals on hiring surges, feature launches, and market moves.

### The Solution
CompetitorPulse deploys three specialized AI agents that autonomously:
1. **Crawl** competitor pricing pages, career boards, and homepages using Bright Data's Scraping Browser (bypassing CAPTCHAs, Cloudflare, and geo-blocks).
2. **Search** Google News and press releases via Bright Data's SERP API for the latest competitive signals.
3. **Analyze** the scraped data to detect strategic trends (pricing changes, AI hiring surges, enterprise pivots).
4. **Generate** professional Sales Battlecards with objection-handling scripts that reps can use immediately.

---

## 🧠 Multi-Agent Architecture

CompetitorPulse uses a **three-agent sequential pipeline**, each powered by Google Gemini 1.5 Flash:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CompetitorPulse Pipeline                      │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────┐│
│  │  🕷️ Data Extractor │───▶│ 📊 Market Analyst │───▶│ 🎯 Sales   ││
│  │     Agent         │    │     Agent         │    │ Strategist ││
│  └──────────────────┘    └──────────────────┘    └────────────┘│
│         │                        │                      │       │
│    Scrapes & cleans         Detects trends &       Generates    │
│    raw web data            compares history      Battlecards    │
│                                                                 │
│  ╔══════════════════════════════════════════════════════════╗   │
│  ║           Bright Data Infrastructure Layer               ║   │
│  ║  Scraping Browser (CDP) │ SERP API │ Web Unlocker       ║   │
│  ╚══════════════════════════════════════════════════════════╝   │
└─────────────────────────────────────────────────────────────────┘
```

| Agent | Role | Tools |
|-------|------|-------|
| **Data Extractor** | Cleans raw HTML, extracts pricing tiers, job listings, and company positioning | Bright Data Scraping Browser via Playwright CDP |
| **Market Analyst** | Identifies strategic shifts, compares with historical scans, detects change signals | Bright Data SERP API, SQLite history |
| **Sales Strategist** | Generates markdown Battlecards with strengths, weaknesses, and verbatim objection scripts | Gemini 1.5 Flash |

---

## ✨ Key Features

- 🔍 **Autonomous Web Crawling** — Scrapes competitor pricing, careers, and homepages via Bright Data's Scraping Browser (Playwright CDP connection), automatically bypassing bot detection and CAPTCHAs.
- 📰 **Live News Intelligence** — Queries Google News via Bright Data SERP API for real-time PR, funding announcements, and product launches.
- 🧠 **Multi-Agent AI Reasoning** — Three specialized Gemini-powered agents work sequentially to extract, analyze, and synthesize competitive intelligence.
- 📊 **Change Detection** — Compares current scans with historical data to surface pricing changes, hiring trends, and positioning shifts over time.
- 🎯 **Sales Battlecard Generation** — Produces professional, ready-to-use battlecards with objection-handling scripts for sales reps.
- 📈 **Interactive Dashboard** — Premium dark-mode Streamlit UI with glassmorphism styling, Plotly charts, and tabbed content views.
- 💾 **Persistent History** — SQLite database stores all scrapes and analyses, enabling historical diffing and trend tracking.
- 🔄 **Always-On Monitoring** — Add any competitor domain and trigger autonomous scans on demand.

---

## 🛠️ Technology Stack

### AI & Intelligence Layer
- **Google Gemini 1.5 Flash** — Powers all three reasoning agents (Data Extractor, Market Analyst, Sales Strategist)
- **Multi-Agent Pipeline** — Sequential agent orchestration with progress callbacks

### Web Data Infrastructure (Bright Data)
- **Scraping Browser** — Cloud-hosted Chromium browser controlled via Playwright CDP. Handles JavaScript rendering, Cloudflare bypass, and CAPTCHA solving automatically.
- **SERP API** — Structured Google News search results for real-time competitive signals
- **Web Unlocker** — Proxy-based clean HTML retrieval with automatic IP rotation

### Frontend & Visualization
- **Streamlit** — Interactive Python web framework with custom dark theme
- **Plotly Express** — Dynamic data visualization (hiring distribution charts)
- **Custom CSS** — Glassmorphism cards, Inter/Outfit typography, HSL-tailored color palette

### Data Layer
- **SQLite** — Zero-config local database for competitor profiles, scrape history, and analysis reports
- **Pandas** — Data manipulation and chart preparation

---

## 📁 Project Structure

```
competitor-pulse/
├── app.py              # Streamlit dashboard — UI, styling, and user interaction
├── agents.py           # Multi-agent orchestrator — Gemini-powered reasoning pipeline
├── scraper.py          # Web scraping engine — Bright Data Scraping Browser + SERP API
├── database.py         # SQLite persistence layer — competitors, scrapes, and reports
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template (copy to .env)
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
└── README.md           # This file
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+**
- **Bright Data Account** with Scraping Browser and SERP API zones configured ([Sign up](https://brightdata.com))
- **Google Gemini API Key** ([Get one](https://aistudio.google.com/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CompetitorPulse.git
cd CompetitorPulse
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BRIGHTDATA_SBR_WS_ENDPOINT=wss://brd-customer-XXXX-zone-XXXX:password@brd.superproxy.io:9222
BRIGHTDATA_API_KEY=your-bright-data-api-key
BRIGHTDATA_SERP_ZONE=serp_api1
GEMINI_API_KEY=your-google-gemini-api-key
```

### 5. Run the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🎮 How to Use

1. **Configure credentials** in the sidebar (Bright Data keys + Gemini API key).
2. **Add a competitor** by entering their name and domain (e.g., "Stripe" / "stripe.com").
3. **Click "🔄 Scan & Analyze"** to launch the autonomous multi-agent pipeline.
4. **View results** across five tabs:
   - 📋 **Sales Battlecard** — The generated competitive playbook
   - 🧠 **AI Analyst Notes** — Strategic analysis with hiring charts
   - 🕸️ **Raw Scraped Content** — Actual text extracted from competitor pages
   - 📰 **News & PR** — Latest Google News results via SERP API
   - 📈 **History & Diffs** — Compare historical scans side-by-side

---

## 🔒 Credit Optimization

Bright Data credits are consumed per Scraping Browser session and SERP API request. To optimize:

- **Cache results locally** — The SQLite database persists all scrapes. The app avoids redundant requests.
- **Session management** — All Playwright connections use `try/finally` blocks to close sessions immediately, preventing idle billing.
- **SERP over custom scraping** — Google search is handled via SERP API (pennies per request) instead of custom scrapers that risk blocks and retries.

---

## 🏗️ Bright Data Products Used

| Product | Usage | Purpose |
|---------|-------|---------|
| **Scraping Browser** | Playwright CDP connection | Scrape JavaScript-heavy pricing and careers pages with automatic CAPTCHA solving |
| **SERP API** | Google News queries | Retrieve structured news and PR results for competitive signals |
| **Web Unlocker** | HTTP proxy fallback | Clean HTML retrieval when full browser rendering isn't needed |

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [**Bright Data**](https://brightdata.com) — For providing the web data infrastructure and $250 in cloud credits
- [**lablab.ai**](https://lablab.ai) — For hosting the Web Data UNLOCKED Hackathon
- [**Google Gemini**](https://ai.google.dev/) — For the Gemini 1.5 Flash model powering the AI agents
