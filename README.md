# AutoDomPilot · Hybrid LLM + Playwright Browser Agent

AutoDomPilot is a research-grade browser agent that:

- Converts webpages into **semantic layout graphs** from the DOM.
- Uses **OpenAI gpt‑4.1** to generate **deterministic JSON action plans**.
- Executes plans via **Playwright**, with structured logging, dry-run mode, and hooks for self-healing.

The project is designed to showcase **robust web automation**, **retrieval-style reasoning over page structure**, and **reproducible evaluation**. It has been tested on real sites such as the public HerokuApp login page and local test flows.

--- 

## 1. Features

- **Semantic layout graph**  
  DOM → cleaned nodes → spatial and structural edges → JSON layout graph used for LLM reasoning.

- **LLM-driven planner with strict schemas**  
  - System prompt enforces **JSON-only output** following a `Plan` schema.
  - Plans use atomic actions (`find`, `fill`, `click`, `await`, `navigate`, `download`, `screenshot`, `upload`).
  - All LLM I/O is validated using **Pydantic** schemas.

- **Executor with Playwright**  
  - Maps step types to Playwright actions.
  - Saves per-step screenshots and DOM snapshots on failure.
  - Supports **dry-run** (no actions) and **execute** modes.

- **Self-healing hooks**  
  - Failure classifier stub (LLM or heuristics) suggests recovery strategies (`rescan_dom`, `use_visual_match`, `use_history`, `ask_user`).
  - Designed for future DOM mutation / re-planning experiments.

- **Embeddings + FAISS**  
  - Node embeddings via **OpenAI embeddings** (or fallback to `sentence-transformers`).
  - Local FAISS index with on-disk cache for node embeddings.

- **Reproducible artifacts**  
  - Each run creates a timestamped folder with:
    - `dom_raw.json`
    - `layout_graph.json`
    - `understanding.json`
    - `plan.json`
    - `executor_observations.json`
    - `screenshots/step_*.png`
    - `logs.jsonl` (structured logs via `structlog`)

- **CI & tests**  
  - Unit tests for schemas and DOM normalization.
  - E2E test against a **local HTML login page** with mocked LLM (no API use in CI).
  - GitHub Actions pipeline runs `black`, `isort`, `mypy` (soft), and `pytest`.

---

## 2. Architecture

Dataflow overview:

1. **Playwright Worker** (`src/browser/playwright_worker.py`)
   - Loads page, captures DOM, screenshot, bounding boxes.
2. **DOM Extractor** (`src/extractor/dom_extractor.py`)
   - Normalizes nodes, computes simple CSS-like paths, `dom_depth`.
3. **Graph Builder** (`src/graph/builder.py`)
   - Builds canonical `layout_graph` with nodes and edges (parent/child + spatial neighbors).
4. **Vector / Embed Store** (`src/vector/embed_store.py`)
   - Embeds nodes, caches vectors, builds FAISS index.
5. **Page Understanding + Planner** (`src/llm/page_understander.py`, `src/llm/planner.py`)
   - Uses MASTER PROMPT to produce:
     - `understanding` over nodes.
     - `plan` (structured JSON of steps).
6. **Executor** (`src/executor/executor.py`)
   - Executes plan via Playwright; logs `ExecutorObservation` per step.
7. **Self-Healer** (`src/healer/self_healer.py`)
   - Classifies failures and proposes recovery strategies (currently stubbed).
8. **Controller / CLI** (`src/controller/cli.py`)
   - Orchestrates full pipeline and manages run directories.

See [`docs/architecture.md`](docs/architecture.md) for a deeper dive and diagrams.

---

## 3. Quickstart

### 3.1. Setup

```bash
git clone https://github.com/<your-username>/AutoDomPilot.git
cd AutoDomPilot

python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```

### 3.2. Configure environment

Copy the template and set keys:

```bash
cp .env.template .env
```

In `.env`, set:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# For FAISS, runs etc.
FAISS_INDEX_PATH=./data/faiss_index.index
RUNS_DIR=./runs
PLAYWRIGHT_HEADLESS=true
MAX_LLMS_TOKENS=8000
LLM_RETRY_LIMIT=2
LOG_LEVEL=INFO
```

> LLM safety: by default, the controller tags the context with `no_sensitive=true` and does **not** send secrets (passwords) to the LLM unless you pass `--allow-sensitive`.

---

## 4. Local HTML login demo (safe, offline)

The repo includes a simple local login page at:

- [`examples/demo_local_testsite/login.html`](examples/demo_local_testsite/login.html)

Run the agent in **dry-run** mode:

```bash
python -m src.controller.cli \
  --url "file:///<absolute-path-to-project>/examples/demo_local_testsite/login.html" \
  --goal "Log in using test credentials and reach the dashboard" \
  --dry-run
```

Example (Windows PowerShell):

```bash
$proj = (Get-Location).Path
python -m src.controller.cli `
  --url "file:///$proj/examples/demo_local_testsite/login.html" `
  --goal "Log in using test credentials and reach the dashboard" `
  --dry-run
```

This will:

1. Extract DOM and screenshot.
2. Build `layout_graph.json`.
3. Call the LLM to produce `understanding` + `plan`.
4. **Skip** actual actions (dry-run) but log everything.

Artifacts are saved in a new directory like:

```text
runs/20251128_153012/
  dom_raw.json
  layout_graph.json
  understanding.json
  plan.json
  executor_observations.json
  screenshots/
  logs.jsonl
```

---

## 5. HerokuApp login demo (public test site)

The project includes a configuration for the public test site:

- <https://the-internet.herokuapp.com/login>

This site provides **public demo credentials**:

- `tomsmith` / `SuperSecretPassword!`

> These credentials are **not** hard-coded in the repo.  
> You should provide them via environment variables at runtime, e.g.:

```env
HEROKUAPP_USERNAME=tomsmith
HEROKUAPP_PASSWORD=SuperSecretPassword!
```

Then run:

```bash
python -m src.controller.cli \
  --url "https://the-internet.herokuapp.com/login" \
  --goal "Log in to HerokuApp using demo credentials and reach the secure area" \
  --execute
```

The agent will:

1. Extract the login page.
2. Plan a multi-step login flow.
3. Execute it via Playwright, logging each step.

A placeholder for a curated example run is at:

```text
examples/heroku_login/run_sample/   # you can save one of your real runs here
```

You can later commit one sanitized `run_sample` to show actual outputs.

---

## 6. Project layout

```text
AutoDomPilot/
├─ README.md
├─ LICENSE
├─ .env.template
├─ requirements.txt
├─ docs/
│  ├─ architecture.md
│  └─ evaluation.md
├─ examples/
│  ├─ demo_local_testsite/
│  │  ├─ login.html
│  │  └─ task.json
│  └─ heroku_login/
│     └─ run_sample/        # placeholder, add one curated run later
├─ data/
│  ├─ fixtures/
│  └─ embeddings_cache/
├─ infra/
│  ├─ Dockerfile
│  └─ docker-compose.yml
├─ scripts/
│  ├─ simulate_dom_changes.py
│  └─ run_benchmark.sh
├─ src/
│  ├─ config/
│  ├─ controller/
│  ├─ browser/
│  ├─ extractor/
│  ├─ graph/
│  ├─ vector/
│  ├─ llm/
│  ├─ executor/
│  ├─ healer/
│  ├─ schema/
│  ├─ utils/
│  └─ tests/
└─ .github/workflows/ci.yml
```

---

## 7. Evaluation & benchmarks

See [`docs/evaluation.md`](docs/evaluation.md) for:

- Metrics:
  - Task success rate
  - Mean steps per task
  - Number of recovery attempts
  - Time to completion
- Test scenarios:
  - Local login page with DOM mutations
  - HerokuApp login
- How to reproduce small benchmarks using:
  - `scripts/run_benchmark.sh`

---

## 8. Research angle

AutoDomPilot is built to explore:

- **Robustness of LLM agents** to DOM changes (distribution shift in UI).
- **Representation and retrieval** over semantic layout graphs.
- **Grounded planning**: plans constrained by validated JSON schemas and executors.
- **Reproducibility**: every run creates full artifacts for later analysis.

This makes it suitable as a **research internship portfolio project** in areas such as representation learning, robust NLP, and trustworthy retrieval systems.

---

## 9. Citation

If you reference AutoDomPilot in applications or reports, you can cite it as:

> Neeraj Patil. *AutoDomPilot: A Hybrid LLM–Playwright Browser Agent for Robust Web Automation*, 2025. GitHub repository: <https://github.com/<your-username>/AutoDomPilot>.
