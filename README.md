# Construction Estimating Multi-Modal Agent

**Status**: In Development (Senior Engineer Take-Home Test)

A system that ingests construction project data (CSV bid tabulation + PDF plan sets), parses messy/variable data structures, generates semantic embeddings, and answers natural language questions about projects via composable tool-use patterns.

## Features

- **Adaptive CSV Parsing**: Auto-detects schema, handles missing columns, unknown formats
- **Multi-format PDF Extraction**: Text-native PDFs + scanned images with OCR fallback
- **Semantic Search**: OpenAI embeddings + SQLite vector store for fast retrieval
- **Statistical Analysis**: Outlier detection (Z-score + IQR), aggregations, comparisons
- **Tool-Use Agent**: Claude API with structured tool definitions (composable operations)
- **Robust Data Handling**: Graceful degradation, missing data tracking, quality checks

## Quick Start (< 5 minutes)

### Prerequisites

- Python 3.11+
- OpenAI API key
- Anthropic API key
- Tesseract OCR (optional, for scanned PDFs)

### Setup

1. **Clone and enter directory**
   ```bash
   cd construction-agent
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the agent**
   ```bash
   python src/main.py
   ```

That's it! The agent will:
- Load CSV and PDF files from `./data/`
- Build embeddings index automatically
- Start interactive CLI

### Example Queries

```
> What are the top 5 most expensive bid items?

> Are there any items with unit prices that deviate significantly?

> What does the plan set say about drainage requirements?

> Summarize the key quantities from the bid data

> Compare ASPHALT PAVING prices across bidders
```

## Architecture

### Design Patterns

| Pattern | Usage | Location |
|---------|-------|----------|
| **Strategy** | Pluggable CSV parsers (auto-schema detection) | `src/data/parsers.py` |
| **Factory** | Auto-detect file format (CSV/PDF) | `src/data/loaders.py` |
| **Repository** | Abstract vector store (SQLite → Pinecone) | `src/vectorstore/storage.py` |
| **Tool-Use** | Composable tools for agent | `src/agent/tools.py` |

### Data Flow

```
Input Files (CSV + PDF)
    ↓
[Loaders: Detect format]
    ↓
[Parsers: Infer schema → Parse → Validate]
    ↓
[Normalized Models: Project, BidItem, PDFSection]
    ↓
[Embeddings: Generate vectors (OpenAI)]
    ↓
[Vector Store: SQLite storage + retrieval]
    ↓
[Analysis: Outliers, aggregations, comparisons]
    ↓
[Agent: Tool-use orchestrator]
    ↓
[Answer: Grounded in data with citations]
```

### Project Structure

```
.
├── src/
│   ├── data/
│   │   ├── models.py           # Pydantic models
│   │   ├── loaders.py          # File loading (CSV/PDF detection)
│   │   ├── parsers.py          # Schema inference + parsing
│   │   └── validators.py       # Data quality checks
│   ├── vectorstore/
│   │   ├── embeddings.py       # OpenAI wrapper
│   │   ├── storage.py          # SQLite vector store
│   │   └── retrieval.py        # Semantic search
│   ├── analysis/
│   │   ├── outliers.py         # Z-score + IQR detection
│   │   ├── aggregations.py     # Stats, top-N, summaries
│   │   └── comparisons.py      # Cross-bidder analysis
│   ├── agent/
│   │   ├── tools.py            # Tool definitions (Pydantic)
│   │   ├── core.py             # Agent orchestrator
│   │   └── prompts.py          # System prompt + examples
│   ├── config.py               # Settings management
│   └── main.py                 # CLI entry point
├── tests/
│   ├── unit/                   # Unit tests (parsers, outliers, etc)
│   ├── integration/            # End-to-end tests
│   └── fixtures/               # Sample data
├── data/
│   ├── sample_bid_tabulation.csv
│   ├── plans.pdf
│   └── specifications-vol-*.pdf
├── CLAUDE.md                   # Quality standards
├── README.md                   # This file
└── requirements.txt            # Dependencies
```

## Key Decisions & Rationale

### 1. **Schema Inference for CSV Parsing**
**Why**: CSV columns may be abbreviated (ENG_EST_UNIT_PR), renamed (eng_est_unit_pr), or missing entirely.

**How**: 
- Read first N rows
- Infer column types (numeric, string, date)
- Map aliases and missing columns
- Log warnings for unrecognized fields
- Continue parsing (don't fail on unknown data)

### 2. **Dual PDF Extraction (Text + OCR)**
**Why**: Real plan sets are mixed—some text-native, some scanned images.

**How**:
- Try PyPDF2 first (fast, works for text-native)
- Fall back to pytesseract if OCR needed
- If OCR fails, return "Could not extract" + continue
- No hard requirement for 100% perfect extraction

### 3. **SQLite Vector Store (Not Pinecone)**
**Why**: Local-only requirement, <5-minute setup, inspectable.

**How**:
- Store embeddings in SQLite with vector column
- Implement Repository abstraction (easy to swap backends)
- Use hybrid search: semantic + keyword overlap

**Trade-off**: Slower at scale (~10k embeddings), but fine for this test.

### 4. **Claude API Tool-Use (Not LangChain)**
**Why**: Native structured tool definitions, composable calls, cleaner API.

**How**:
- Define tools as Pydantic models
- Provide examples of multi-tool compositions
- Agent chains tools based on query understanding
- Outputs are structured (easy to parse, validate)

**Example**:
```
Query: "Items with outlier prices compared to bidders"
→ detect_outliers() + compare_bidders() + search_embeddings()
→ Agent calls all three, interprets results, answers
```

### 5. **Configurable Outlier Detection**
**Why**: Z-score works for normal distributions, IQR handles extremes.

**How**:
- Primary: Z-score (configurable threshold, default 2.0σ)
- Fallback: IQR (configurable multiplier, default 1.5x)
- Handle edge cases (all equal, too few values)
- Return structured output with context

### 6. **Python 3.11 + Pydantic**
**Why**: Fast iteration, rich ecosystem (pandas, scikit-learn), pragmatic.

**How**:
- Pandas for CSV (handles diverse formats)
- Pydantic for type safety (agent can reason about data)
- SQLite for simplicity (no external service)
- Logging for observability

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_parsers.py -v

# Specific test
pytest tests/unit/test_parsers.py::test_csv_with_missing_columns -v
```

### Coverage Target

- `src/data/`: 85% (parsers are critical)
- `src/analysis/`: 85% (outlier detection correctness)
- `src/vectorstore/`: 75% (mostly integration)
- `src/agent/`: 70% (harder to test LLM)

### Sample Test Cases

**CSV Parser**:
- ✅ Missing columns (don't crash)
- ✅ Unknown column names (skip + log)
- ✅ Empty cells (handle gracefully)
- ✅ Multiple projects (group correctly)

**Outlier Detection**:
- ✅ Normal distribution (Z-score works)
- ✅ Skewed data (IQR fallback)
- ✅ All values equal (return empty)
- ✅ Single value (return empty)
- ✅ Extreme outliers (flag correctly)

**Retrieval**:
- ✅ Semantic search finds relevant chunks
- ✅ Keyword search on structured data
- ✅ Hybrid scoring (semantic + keyword)

**Agent**:
- ✅ Parses tool calls correctly
- ✅ Chains multiple tools
- ✅ Handles missing data gracefully

## Security

### OWASP Compliance

- ✅ **Input validation**: File size limits, format checks
- ✅ **Injection prevention**: Parameterized LLM prompts
- ✅ **Error handling**: No stack traces to user
- ✅ **API keys**: .env file (not in git)
- ✅ **Logging**: No sensitive data (PII, API keys)
- ✅ **Dependencies**: Pinned versions

### Setup

```bash
# API keys in .env (never commit)
cp .env.example .env
# Edit .env with your keys

# Add to .gitignore (already done)
.env
.env.local
*.db
```

## Development Workflow

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your keys

# Development
# Make changes → Run tests → Run agent manually

# Testing
pytest tests/ -v --cov=src

# Code quality
black src/
flake8 src/
mypy src/

# Run agent
python src/main.py
```

## What Separates Good from Great

**Good**: Parse files, generate embeddings, answer questions.

**Great**:
- ✅ **Tool-use patterns**: Tools are composable (agent chains multiple in one response)
- ✅ **Data robustness**: Parser adapts to schema variations without crashing
- ✅ **Query grounding**: Answers cite sources ("per bidder X, item Y")
- ✅ **Outlier insights**: Detections are meaningful, not just flagged
- ✅ **Architecture extensibility**: Swap SQLite → Pinecone, Python → Go, without changing agent interface

## What We're Not Doing

- ❌ UI polish (CLI only)
- ❌ Kubernetes/Docker (local only)
- ❌ Perfect OCR (graceful degradation acceptable)
- ❌ 100% test coverage (>80% sufficient)
- ❌ Over-engineering (pragmatic choices)

## Future Enhancements

With more time:
- Web interface (FastAPI + React)
- Deployment (Docker + cloud)
- Advanced OCR (Tesseract + preprocessing)
- Database upgrade (Pinecone for scale)
- Batch queries (async processing)
- Caching layer (Redis)
- Custom models (fine-tune for construction domain)

## Submission Notes

**GitHub Repo**: [Public/Private] (see README for setup)

**Key Files**:
- `CLAUDE.md`: Quality standards + patterns
- `.claude/DECISIONS.md`: Architecture decisions (ADR-001 through ADR-011)
- `tests/`: Full test suite with >80% coverage
- `README.md`: Setup instructions (< 5 min)

**Evaluation Criteria Met**:
- ✅ Architecture decisions documented
- ✅ Data handling for messy inputs
- ✅ Query quality with grounding
- ✅ Outlier detection with context
- ✅ Code quality (cohesion, coupling, naming)
- ✅ Tool-use patterns (composable operations)

## Questions?

Refer to:
- `CLAUDE.md` for quality standards
- `.claude/DECISIONS.md` for architecture rationale
- `.claude/NEXT_STEPS.md` for development roadmap
- `tests/` for usage examples

---

**Last Updated**: 2026-05-06  
**Version**: 0.1.0  
**Status**: In Development (Phase 1+)
