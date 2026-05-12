# Entry Points & Command Aliases

## Overview

The Construction Agent project defines **entry points** (command aliases) in `pyproject.toml` that provide convenient shortcuts to run the application without typing `python3 src/main.py`.

---

## Installation Requirement

Entry points **only work after installing the project**:

```bash
pip install -e .
```

This registers the aliases globally in your virtual environment.

---

## Available Commands

### 1. `agent` — Interactive Analysis Mode

```bash
agent
```

**Flow:**
1. Shows menu to upload CSV/PDF files OR load from `data/` folder
2. Indexes documents with embeddings (real OpenAI or mock)
3. Opens interactive analysis shell
4. You can ask natural language questions about your data

**Example interaction:**
```
Options:
  1. Upload a file (auto-detect CSV/PDF)
  2. Load folder
  3. Start analysis

👉 Choose (1-3): 1

📄 Select file to upload: /path/to/bid_data.csv
✅ CSV indexed: 150 items

💬 ANALYSIS MODE

💡 Ask questions about your documents!
Commands: 'help', 'examples', 'quit'

📍 You: What are the top 5 most expensive items?

🤖 Claude is analyzing...

[Response with top items and prices...]
```

**When to use:**
- When you have specific files to analyze
- For interactive exploration
- When you want to ask follow-up questions

---

### 2. `agent-demo` — Automated Demo Mode

```bash
agent-demo
```

**Flow:**
1. Auto-loads all files from `data/` folder
2. Indexes with mock embeddings (fast, no API calls)
3. Runs 3 pre-defined example queries
4. Displays results and cleans up

**Example output:**
```
🤖 CONSTRUCTION AGENT - DEMO

📂 Loading documents from data/ folder...
   ✅ CSV: sample_bid_tabulation.csv
   ✅ PDF: project_plans.pdf

📊 Indexing documents...
   ✅ CSV indexed: 150 items
   ✅ PDF indexed: 42 chunks

💬 DEMO - Example Queries

📍 Question: What are the top 3 most expensive items?
   [response...]

📍 Question: Are there any pricing anomalies or outliers?
   [response...]

📍 Question: What information is in the plan documents?
   [response...]

✅ Demo complete
```

**When to use:**
- To quickly see what the agent can do
- For presentations or demos
- To verify the system is working

---

## How Entry Points Work

Entry points are defined in `pyproject.toml`:

```toml
[project.scripts]
agent = "src.main:main"
agent-demo = "src.demo:main"
```

**What this means:**
- `agent` command → runs function `main()` from file `src/main.py`
- `agent-demo` command → runs function `main()` from file `src/demo.py`

**Installation process:**
```bash
pip install -e .
    ↓
Setuptools reads pyproject.toml
    ↓
Creates executable scripts:
  - /path/to/venv/bin/agent
  - /path/to/venv/bin/agent-demo
    ↓
You can now type: agent (anywhere in venv)
```

**Verification:**
```bash
which agent         # Shows path to the script
agent               # Runs it
agent --help        # Shows help (if argparse is used)
```

---

## Alternative: Run Without Installation

If you don't want to use entry points, run directly with Python:

```bash
# Interactive agent
python3 src/main.py

# Demo mode
python3 src/demo.py
```

**Pros:**
- No installation step
- Works immediately

**Cons:**
- Longer command to type
- Need to remember file path

---

## Troubleshooting

### "command not found: agent"

**Cause:** Entry points not registered (didn't run `pip install -e .`)

**Fix:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install project
pip install -e .

# Verify
which agent    # Should show: /path/to/venv/bin/agent
agent          # Should work now
```

### "agent: command not found" after fresh terminal

**Cause:** Virtual environment not activated

**Fix:**
```bash
source venv/bin/activate    # Activate venv
agent                       # Now it works
```

### Different versions of Python

If you have multiple Python versions (3.10, 3.11, 3.12), the entry point uses whichever was used to create the venv:

```bash
# Create venv with specific Python
python3.10 -m venv venv

# Install
pip install -e .

# Entry point will use Python 3.10
```

---

## Configuration via Entry Points

The entry points use environment variables from `.env`:

```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env
```

Available settings:
- `OPENAI_API_KEY` — For real embeddings (optional)
- `ANTHROPIC_API_KEY` — For agent (usually already set)
- `LOG_LEVEL` — DEBUG, INFO, WARNING, ERROR
- `LOG_FILE` — Where to write logs

---

## Summary

| Command | Purpose | Requires Installation |
|---------|---------|----------------------|
| `agent` | Interactive analysis | ✅ `pip install -e .` |
| `agent-demo` | Automated demo | ✅ `pip install -e .` |
| `python3 src/main.py` | Same as `agent` | ❌ No |
| `python3 src/demo.py` | Same as `agent-demo` | ❌ No |

---

## Next Steps

- See **SETUP.md** for installation details
- See **docs/QUICK_START.md** for usage examples
- See **.env.example** for configuration options
