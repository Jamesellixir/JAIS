# StarForge – JAIS: Just Another Intelligent System

> **Turning AI complexity into business simplicity.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Local_AI-Ollama-black?style=flat-square)
![OpenRouter](https://img.shields.io/badge/Cloud_AI-OpenRouter-6366f1?style=flat-square)
![Flask](https://img.shields.io/badge/Web-Flask-000000?style=flat-square&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Overview

**JAIS** is an intelligent AI routing and orchestration system built by StarForge. It eliminates the cost and complexity of always relying on expensive cloud AI calls by combining a **local AI coordinator** (Ollama/Qwen) with **specialized cloud workers** (via OpenRouter) — routing every user request to the right model, at the right time, for the right task.

Instead of one overloaded AI trying to do everything, JAIS uses a **coordinator-worker architecture**: a lightweight local model analyzes intent and routes the job to a domain-specialized cloud worker. Workers are fully customizable through a **plug-and-play Skills system** — no code changes needed to add new AI capabilities.

Businesses get faster responses, lower API costs, and a modular AI backend that can grow with their needs.

---

## ✨ Features

- **🧠 Intelligent Request Routing** — A local Ollama model reads every user prompt and decides the optimal domain, tool, and cloud worker to use — eliminating wasted API calls.
- **☁️ Pluggable Cloud Workers** — Workers are backed by OpenRouter, giving access to dozens of frontier models. Swap models per domain without touching core logic.
- **📂 Skills System** — Drop a `SKILL.md` file into the `/skills` folder and JAIS automatically discovers, loads, and injects it as a specialized AI worker — zero code changes required.
- **🛠 Local Tool Execution** — JAIS can create files and run shell commands on the host machine based on AI decisions, bridging the gap between AI reasoning and real-world action.
- **🌐 Dual Interface** — Ships with both a **CLI** (for developers and power users) and a **Flask web UI** (for end users), backed by the same routing engine.
- **🔒 File Upload & Workspace API** — The web interface exposes secure endpoints for file uploads, workspace browsing, and content retrieval — ready for deeper integration.
- **⚙️ Environment-Driven Config** — Model selection, API keys, and routing behavior are all controlled via `.env` — no hardcoding, safe for deployment.

---

## 🚀 Demo

> 🔗 [Live Demo](YOUR_DEMO_URL_HERE) · Screenshots coming soon

---

## 🛠 Tech Stack

| Layer | Tools |
|---|---|
| **Local AI (Router)** | Ollama · Qwen 2.5 7B (configurable) |
| **Cloud AI (Workers)** | OpenRouter API (OpenAI-compatible) |
| **Skills Engine** | Custom Python · SKILL.md (Markdown + YAML frontmatter) |
| **Web Backend** | Flask · Werkzeug |
| **CLI Interface** | Python · Colorama |
| **Environment** | python-dotenv |
| **Local Tools** | subprocess · os (file creation, shell commands) |

---

## Getting Started

### Prerequisites

- Python **3.10+**
- [Ollama](https://ollama.com/) installed and running locally
- An [OpenRouter](https://openrouter.ai/) account and API key (free tier available)
- The Qwen model pulled in Ollama (or your preferred model):

```bash
ollama pull qwen2.5:7b
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/JAIS.git
cd JAIS

# 2. Install Python dependencies
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` (or create `.env`) and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|---|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key for cloud workers | ✅ |
| `ROUTER_MODEL` | Local Ollama model name (e.g. `qwen2.5:7b`) | ⬜ (defaults to `qwen2.5:7b`) |

> ⚠️ **Never commit your `.env` file.** Add it to `.gitignore`. Secrets should never be pushed to a repository.

### Running Locally

```bash
# CLI mode (developer / terminal interface)
python main.py

# Web UI mode (browser interface on http://127.0.0.1:5000)
python app.py
```

---

## Usage

### CLI Example

```
==================================================
               AI ROUTER SYSTEM
==================================================
Main AI:  Local Ollama (Qwen)
Workers:  Cloud APIs (OpenRouter)
==================================================

User > Write a Python function to parse a CSV file and return a list of dicts.

[Main AI] Analyzing request using local qwen2.5:7b...
  [Main AI] Decision: {"domain": "coding", "tool_needed": "none", ...}
  [Main AI] Routing to 'coding' worker...
  [Worker System] Delegating to cloud model: openrouter/auto

[Cloud AI (coding)]:
def parse_csv(filepath): ...
```

### Web API Example

```bash
# Send a chat message
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize the key points of machine learning."}'

# Upload a file
curl -X POST http://127.0.0.1:5000/api/upload \
  -F "file=@report.pdf"

# List workspace files
curl http://127.0.0.1:5000/api/files
```

### Adding a Custom Skill

1. Create a new folder under `/skills/your-skill-name/`
2. Add a `SKILL.md` file with a YAML frontmatter block:

```markdown
---
name: your-skill-name
description: What this skill does and when to route to it.
---

# Instructions
Your detailed instructions for the AI worker go here.
These will be injected as the system prompt when this skill is selected.
```

3. Restart JAIS — the skill is auto-discovered. No code changes needed.

---

## Architecture

```
User Prompt (CLI or Web UI)
        │
        ▼
┌──────────────────────┐
│   router.py          │  ← Local Ollama (Qwen) analyzes intent
│   Main AI Coordinator│    Decides: domain + tool + worker_prompt
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌──────────────────────┐
│ tools  │  │    workers.py        │
│.py     │  │  Cloud Worker (API)  │  ← OpenRouter + skill instructions
│        │  │  (OpenRouter/auto)   │
└────┬───┘  └──────────┬───────────┘
     │                 │
     ▼                 ▼
create_file /    Final AI response
run_command      returned to user
```

The **Skills system** (`skills_manager.py`) scans `/skills/*/SKILL.md` at runtime, parses YAML frontmatter for `name` and `description`, and injects the full Markdown body as the worker's system prompt when that domain is selected by the router.

---

## Testing

Currently no automated test suite is included. To manually verify:

```bash
# Confirm Ollama is running
ollama list

# Run CLI and test basic routing
python main.py

# Run web server and test the /api/chat endpoint
python app.py
curl -X POST http://127.0.0.1:5000/api/chat -H "Content-Type: application/json" -d '{"message": "Hello!"}'
```

> 📌 A `pytest` test suite covering routing logic and skill loading is on the roadmap.

---

## Deployment

JAIS is designed to be self-hosted. Recommended platforms:

**Railway / Render (recommended for Flask web UI):**
1. Push repo to GitHub
2. Connect repo to Railway or Render
3. Set environment variables (`OPENROUTER_API_KEY`, `ROUTER_MODEL`) in the platform dashboard
4. Set start command: `python app.py`

> ⚠️ Ollama (local AI) is only available when running on a machine where Ollama is installed. For fully cloud-based deployment, replace the Ollama router call with a cloud model (e.g., a lightweight OpenRouter model) in `router.py`.

---

## Roadmap

- [ ] Persistent conversation history and multi-turn context
- [ ] Automated `pytest` test suite for routing and skill loading
- [ ] Web UI skill manager (add/remove skills without touching the filesystem)
- [ ] Streaming responses in the web interface
- [ ] Docker containerization for one-command deployment
- [ ] Support for multiple simultaneous cloud worker calls (parallel routing)
- [ ] Admin dashboard showing routing logs and worker usage stats

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a PR

---

## License

MIT License — see [`LICENSE`](LICENSE) for details.

---

## Credits & Contact

**Built by [StarForge](YOUR_WEBSITE_HERE)**
> Turning AI complexity into business simplicity.

| | |
|---|---|
| 🏢 **Agency** | StarForge AI Automation |
| 👤 **Founder** | [Your Name] |
| 🌐 **Website** | [YOUR_WEBSITE_HERE] |
| 📧 **Contact** | [YOUR_EMAIL_HERE] |
| 💼 **Services** | AI Chatbots · Document Processing · Workflow Automation · Custom AI Systems |

---

*StarForge builds production-ready AI systems for businesses that want results, not experiments.*
