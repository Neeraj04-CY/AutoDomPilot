# Adaptive Browser Agent

Adaptive Browser Agent is a research-grade project that:

- Converts a web page into a **semantic layout graph**.
- Uses an LLM planner (OpenAI `gpt-4.1`) to produce a **deterministic action plan** to achieve a user goal.
- Executes plans with **Playwright** and can run in **dry-run** mode for safety.
- Is designed for **self-healing** and future recovery strategies.

> ⚠️ This project is for research and educational purposes. Do **not** use it to automate websites that prohibit automated access in their Terms of Service.

## Quickstart

### 1. Clone and set up environment

```bash
git clone <your-fork-url> adaptive-browser-agent
cd adaptive-browser-agent

python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Unix:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

Copy the template and edit:

```bash
cp .env.template .env
```

Set your OpenAI API key:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

Other settings have sensible defaults.

### 3. Install Playwright browsers

```bash
playwright install
```

### 4. Run a local demo (dry-run)

Prepare a local HTML demo page under:

- `examples/demo_local_testsite/login.html` (a simple login page)

Then run:

```bash
python -m src.controller.cli ^
  --url "file:///C:/path/to/your/project/examples/demo_local_testsite/login.html" ^
  --goal "Log in using test credentials" ^
  --dry-run
```

On Unix:

```bash
python -m src.controller.cli \
  --url "file:///home/you/adaptive-browser-agent/examples/demo_local_testsite/login.html" \
  --goal "Log in using test credentials" \
  --dry-run
```

This will:

1. Launch Playwright headless.
2. Extract DOM and bounding boxes.
3. Normalize DOM into a `layout_graph.json`.
4. (Optionally) build embeddings.
5. Call the LLM in **dry-run mode** (no actual actions).
6. Save artifacts in a new run directory under `./runs/YYYYMMDD_HHMMSS/`.

### 5. Execute actions (⚠️ read ToS warning first)

To actually perform actions with Playwright:

```bash
python -m src.controller.cli \
  --url "file:///.../examples/demo_local_testsite/login.html" \
  --goal "Log in using test credentials" \
  --execute
```

- The executor will run the plan produced by the LLM.
- Artifacts: screenshots and logs in `runs/<timestamp>/`.

> ⚠️ **Terms of Service & Safety**  
> - Do **not** point this agent at sites whose ToS disallow automation or scraping.  
> - By default, **passwords and other secrets are not sent to the LLM**.  
> - Use `--allow-sensitive` only if you fully understand the privacy implications and have permission.

### Artifacts per run

Each run creates a directory under `RUNS_DIR` (default `./runs`):

- `layout_graph.json` — normalized page layout graph.
- `dom_raw.json` — raw DOM extraction.
- `plan.json` — planner output.
- `understanding.json` — LLM semantic understanding (if applicable).
- `screenshots/step_*.png` — screenshots per step.
- `logs.jsonl` — structured logs (one JSON per line).

## Tests

Run unit and e2e tests:

```bash
pytest
```

- Unit tests mock LLM calls and operate on fixtures in `data/fixtures`.
- E2E tests for `demo_local_testsite` do **not** call OpenAI in CI (they are mocked).

## Development

- Code style: `black`, `isort`
- Type checking: `mypy` (optional)
- CI: GitHub Actions in `.github/workflows/ci.yml`

See:

- `docs/architecture.md` for high-level design.
- `docs/runbook.md` for debugging and operational tips.