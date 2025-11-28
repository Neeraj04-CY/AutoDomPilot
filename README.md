AutoDomPilot · Hybrid LLM + Playwright Browser Agent

AutoDomPilot is a high-grade browser automation agent that combines structured DOM understanding, deterministic LLM planning, and Playwright execution. It focuses on reliable actions, reproducible runs, and research-level analysis of how models reason over real web layouts.

The system has been tested on real public sites such as the HerokuApp login page and local mock pages.

1. Core Features
Semantic layout graph

The DOM is converted into a clean graph representation with:

normalized nodes

parent–child structure

spatial neighbors

bounding boxes

simple CSS-style paths

This graph becomes the main reasoning context for the LLM.

LLM planner with strict schemas

Planning is deterministic:

LLM outputs follow a fixed Plan schema

All outputs go through Pydantic validation

Steps are atomic (find, fill, click, await, navigate, screenshot, upload, download)

Output format is JSON only

Playwright executor

Playwright runs each step and produces:

per-step screenshots

error snapshots

structured logs

dry-run support (LLM planning without actions)

Self-healing hooks

A simple failure classifier proposes:

DOM rescan

visual match fallback

using previous page history

asking for clarification

These hooks are stubs for future experiments with adaptive planning.

Embeddings + FAISS

Nodes are embedded using OpenAI or a local transformer model.
FAISS provides fast similarity search with on-disk caching.

Reproducible artifacts

Each run creates a clean folder containing:

dom_raw.json
layout_graph.json
understanding.json
plan.json
executor_observations.json
screenshots/
logs.jsonl

CI and testing

Unit tests for schemas and DOM normalization

Mocked end-to-end test of the full pipeline

GitHub Actions: black, isort, pytest, and soft mypy

2. System Architecture

The pipeline works in this order:

Playwright Worker
Captures DOM, screenshot, element boxes.

DOM Extractor
Normalizes nodes and computes metadata.

Graph Builder
Constructs the semantic layout graph.

Vector Store
Embeds nodes and builds a FAISS index.

Page Understanding + Planner
LLM produces:

node-level understanding

a complete validated plan

Executor
Executes steps, logs results, saves artifacts.

Self-Healer
Suggests recovery strategies on failure.

Controller / CLI
Orchestrates full runs and manages directories.

A deeper explanation is in docs/architecture.md.

3. Quickstart
3.1 Install and set up environment
git clone https://github.com/<your-username>/AutoDomPilot.git
cd AutoDomPilot

python -m venv .venv
.\.venv\Scripts\activate   # On Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt


Install Playwright browsers:

playwright install

3.2 Configure .env
cp .env.template .env


Set at least:

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

FAISS_INDEX_PATH=./data/faiss_index.index
RUNS_DIR=./runs
PLAYWRIGHT_HEADLESS=true
MAX_LLMS_TOKENS=8000
LLM_RETRY_LIMIT=2
LOG_LEVEL=INFO


The controller blocks sensitive info by default.
To allow sensitive goals or passwords in prompts, use --allow-sensitive.

4. Local Offline Demo

A simple login page is available at:

examples/demo_local_testsite/login.html


Run the agent in dry-run mode:

python -m src.controller.cli \
  --url "file:///<absolute-path>/examples/demo_local_testsite/login.html" \
  --goal "Log in using test credentials and reach the dashboard" \
  --dry-run


This will extract the DOM, build the graph, ask the LLM for a plan, and save artifacts without clicking anything.

A new directory under runs/ will be created automatically.

5. HerokuApp Login Demo (Public Test Site)

Use the public demo page:

https://the-internet.herokuapp.com/login


Public demo credentials:

username: tomsmith

password: SuperSecretPassword!

These are not hard-coded in the repo.
Set them through environment variables:

HEROKUAPP_USERNAME=tomsmith
HEROKUAPP_PASSWORD=SuperSecretPassword!


Run:

python -m src.controller.cli \
  --url "https://the-internet.herokuapp.com/login" \
  --goal "Log in to HerokuApp using demo credentials and reach the secure area" \
  --execute


A folder under examples/heroku_login/run_sample is available for storing curated example outputs.

6. Project Layout
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
│     └─ run_sample/
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

7. Evaluation and Benchmarks

Details in docs/evaluation.md.

Included metrics:

task success

steps per task

recovery attempts

time to completion

Test scenarios:

local login page with DOM mutation

HerokuApp login

You can reproduce small benchmarks with:

./scripts/run_benchmark.sh

8. Research Direction

AutoDomPilot explores:

how LLMs handle layout changes and unstable DOMs

retrieval-focused planning using semantic graphs

grounded tool-use with strict schema validation

reproducibility for real automation experiments

This makes the project suitable for:

research internships

agent reliability experiments

representation learning studies

HCI and UI automation research

9. Citation

If you reference this project:

Neeraj Patil. AutoDomPilot: A Hybrid LLM–Playwright Browser Agent for Robust Web Automation, 2025. GitHub repository: <https://github.com/
<your-username>/AutoDomPilot>.
