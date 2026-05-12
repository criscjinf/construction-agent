# Setup Instructions

This project uses **pyproject.toml** (PEP 517/518) for modern Python packaging.

## Prerequisites

- Python 3.10 or higher (tested on 3.10.12, 3.11+)
- pip (included with Python)

## Installation

### 1. Clone and Setup Virtual Environment

```bash
git clone <repo-url>
cd construction-agent

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate          # On Linux/Mac
# or
python -m venv venv && venv\Scripts\activate  # On Windows
```

### 2. Install Project

```bash
# Install project + production dependencies
pip install -e .

# Or install with development tools (pytest, linting, etc)
pip install -e ".[dev]"

# Or install with API server support (FastAPI, uvicorn)
pip install -e ".[api]"

# Or install everything
pip install -e ".[dev,api]"
```

## Dependencies

### Production Dependencies

Defined in `pyproject.toml` under `[project]`:

- **Data Processing**: pydantic, pandas, numpy, scipy, scikit-learn
- **PDF Handling**: PyPDF2, pytesseract, Pillow
- **LLM APIs**: anthropic, openai
- **Vector Store**: sqlite-vec
- **CLI**: click

### Development Dependencies

Defined in `pyproject.toml` under `[project.optional-dependencies.dev]`:

- **Testing**: pytest, pytest-cov, pytest-asyncio, pytest-mock
- **Linting**: black, flake8, mypy, isort

### Optional API Dependencies

Defined in `pyproject.toml` under `[project.optional-dependencies.api]`:

- **Web Framework**: fastapi, uvicorn

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LOG_LEVEL=INFO
```

## Running the Application

### Entry Points (Command Aliases)

After `pip install -e .`, you can use these convenient command aliases defined in `pyproject.toml`:

#### `agent` — Interactive Agent

```bash
agent
```

**What it does:**
- Opens interactive menu to upload CSV/PDF files OR load from `data/` folder
- Indexes documents with real OpenAI embeddings (or mock if key not available)
- Opens analysis shell where you can ask questions:
  - "What are the top 5 most expensive items?"
  - "Are there price outliers?"
  - "Compare bidders on MOBILIZATION"
- Commands: `help`, `examples`, `quit`

**When to use**: When you have specific files to analyze or want to explore data interactively

#### `agent-demo` — Automated Demo

```bash
agent-demo
```

**What it does:**
- Automatically loads all files from `data/` folder
- Indexes them with mock embeddings (fast, no API calls)
- Runs 3 example queries automatically
- Shows results and cleans up

**When to use**: Quick demonstration of agent capabilities without uploading files

---

### How Entry Points Work

**Entry points are shortcuts** defined in `pyproject.toml`:

```toml
[project.scripts]
agent = "src.main:main"           # Maps 'agent' → runs src/main.py:main()
agent-demo = "src.demo:main"      # Maps 'agent-demo' → runs src/demo.py:main()
```

**To make them work:**
```bash
pip install -e .    # This registers the aliases globally in your venv
```

**After installation:**
```bash
which agent         # Shows: /path/to/venv/bin/agent
agent               # Runs the agent immediately
```

**They're just shortcuts for:**
```bash
python3 src/main.py   # Same as: agent
python3 src/demo.py   # Same as: agent-demo
```

---

### Direct Python Execution (No Installation Needed)

If you don't want to use `pip install -e .`, you can run directly:

```bash
# Interactive agent
python3 src/main.py

# Quick demo
python3 src/demo.py

# Run tests
python3 -m pytest tests/ -v
```

⚠️ **Note**: Entry point aliases (`agent`, `agent-demo`) only work after `pip install -e .`

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_parsers.py -v

# Run with detailed output
pytest tests/ -vv --tb=short
```

## Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Make code changes

# 3. Run tests
pytest tests/ -v

# 4. Format code (optional)
black src/ tests/
isort src/ tests/

# 5. Type checking (optional)
mypy src/

# 6. Linting (optional)
flake8 src/
```

## Updating Dependencies

### Check for outdated packages

```bash
pip list --outdated
```

### Update specific package

```bash
pip install --upgrade <package-name>
```

### Update all packages

```bash
pip install --upgrade -e ".[dev,api]"
```

## Project Structure

```
construction-agent/
├── src/
│   ├── data/
│   │   ├── models/              # Pydantic models (SRP)
│   │   │   ├── bidder.py
│   │   │   ├── bid_item.py
│   │   │   ├── project.py
│   │   │   └── ...
│   │   ├── parsers/             # CSV/PDF parsing
│   │   ├── indexers/            # Document indexers (factory pattern)
│   │   └── validators.py
│   ├── vectorstore/
│   │   ├── storage/             # Vector store implementations
│   │   ├── embeddings/          # Embedding clients (batch optimized)
│   │   └── retrieval.py
│   ├── analysis/                # Outliers, aggregations, comparisons
│   ├── agent/                   # Claude agent + tools
│   ├── main.py                  # Interactive agent ⭐ Entry point
│   ├── demo.py                  # Quick demo
│   └── logging_config.py
├── tests/
│   ├── unit/                    # Unit tests (mock storage)
│   ├── integration/             # Integration tests (real SQLite)
│   └── fixtures/
├── docs/
│   ├── QUICK_START.md
│   ├── EMBEDDINGS.md
│   ├── EXAMPLES.md
│   ├── DEBUGGING.md
│   └── SECURITY.md
├── pyproject.toml               # Modern Python packaging (PEP 517)
├── SETUP.md                     # This file (installation & setup)
├── README.md                    # Project overview
├── CLAUDE.md                    # Development standards
└── .env.example                 # Environment variables template
```

## Troubleshooting

### "command not found: agent" or "agent: command not found"

The entry point aliases only work after installation. Make sure you:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install project in development mode
pip install -e .

# 3. Verify installation
which agent              # Should show: /path/to/venv/bin/agent
agent --help           # Should run the agent
```

**Alternative**: Run directly without installation:
```bash
python3 src/main.py    # Instead of: agent
python3 src/demo.py    # Instead of: agent-demo
```

### "ModuleNotFoundError: No module named 'src'"

Make sure you installed the project:
```bash
pip install -e .
```

### "OPENAI_API_KEY not configured"

The agent works with mock embeddings. If you want real embeddings:
```bash
cp .env.example .env
nano .env
# Add: OPENAI_API_KEY=sk-...
```

### Tests fail with import errors

Ensure virtual environment is activated and project is installed:
```bash
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

## More Information

- **[pyproject.toml format](https://packaging.python.org/en/latest/specifications/declaring-dependencies/)** — PEP 621
- **[Build systems](https://packaging.python.org/en/latest/specifications/pyproject-toml/)** — PEP 517/518
- **[Project README](README.md)** — Overview and features
- **[Security audit](docs/SECURITY.md)** — OWASP compliance

## Support

For issues or questions, check:
1. The troubleshooting section above
2. Test output: `pytest tests/ -vv`
3. Logs: `construction_agent.log`
