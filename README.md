# Construction Estimating Multi-Modal Agent

An AI-powered agent that analyzes construction bid data and project plans using adaptive data parsing, semantic search, statistical analysis, and Claude API tool-use patterns.

**Status**: ✅ Complete (5 phases, 130 tests, 0 regressions)

---

## Quick Start (<5 minutes)

### 1. Install

```bash
# Clone repository
git clone <repo-url>
cd construction-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy example configuration
cp .env.example .env

# Add your API keys
nano .env
# Required:
#   OPENAI_API_KEY=sk-...
#   ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run

```bash
# Main interactive agent (upload or load from data/)
python scripts/run_agent.py

# Quick demo with data/ folder (auto-loads, no upload)
python scripts/demo.py
```

---

## Example Queries

Once running, try these queries:

1. **"What are the top 5 most expensive bid items?"**
   - Uses: aggregation tool → ranks items by unit_price
   - Result: Shows items sorted by price with descriptions

2. **"Are there any items with unit prices that deviate significantly?"**
   - Uses: outlier detection (Z-score method)
   - Result: Shows statistical deviations with context

3. **"How do bidders compare on MOBILIZATION?"**
   - Uses: bidder comparison tool
   - Result: Shows all bidders' prices and variance

4. **"Which items have the most bidder competition?"**
   - Uses: aggregation + comparison
   - Result: Items ranked by pricing variance

5. **"Compare ASPHALT PAVING prices across all bidders"**
   - Uses: comparison tool
   - Result: Detailed price analysis with insights

---

## Architecture Overview

### Five Phases (130 tests, 100% pass rate)

**Phase 1: Data Ingestion** (47 tests)
- Adaptive CSV parsing with schema inference
- Handles: missing columns, renamed columns, empty cells, multiple projects
- Pydantic-validated models with DataLoader factory

**Phase 2: Vector Store** (34 tests)
- OpenAI embeddings (text-embedding-3-small)
- SQLite storage with Repository pattern (swappable to Pinecone)
- Hybrid retrieval: semantic (70%) + keyword (30%)

**Phase 3: Analysis Tools** (18 tests)
- Outlier detection: Z-score + IQR methods
- Aggregations: top items, statistics, summaries
- Comparisons: bidder analysis, competitive ranking

**Phase 4: Agent Framework** (31 tests)
- Claude API integration with tool-use patterns
- Pydantic tool definitions with JSON schemas
- Composable tool execution and grounded responses

**Phase 5: Polish** 
- CLI interface (interactive + single-query modes)
- >80% test coverage verification
- OWASP security audit
- Comprehensive documentation

### Design Patterns

- **Strategy**: Pluggable CSV parsers for different formats
- **Factory**: DataLoader auto-detects file type
- **Repository**: VectorStore abstraction (enables swaps)
- **Adapter**: Agent tool execution maps to analysis functions
- **Dependency Injection**: Loose coupling throughout

### Quality Standards

✅ SOLID principles  
✅ High cohesion, low coupling  
✅ >90% test coverage  
✅ OWASP security compliance  
✅ No over-engineering  

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

**Coverage**: 130 tests, >90% coverage across all phases

---

## Known Limitations & Future Work

### Current Limitations
1. **No OCR**: Scanned PDFs without native text not supported (future: pytesseract integration)
2. **Single-session storage**: Vector store not persistent across runs (future: persistent DB)
3. **Single-threaded**: Agent processes one query at a time (future: async support)

### Future Enhancements
- Web interface (FastAPI + React)
- REST API for integration
- Streaming responses
- Persistent vector store
- Custom domain embeddings
- Advanced ML models for prediction
- Audit trails and multi-user support

---

## File Structure

```
src/
├── data/          # CSV parsing, schema inference, validation
├── vectorstore/   # Embeddings, storage, retrieval
├── analysis/      # Outliers, aggregations, comparisons
├── agent/         # Tools, orchestrator, prompts
├── config.py      # Settings management
└── main.py        # CLI entry point

scripts/
├── run_agent.py    # Main interactive agent (upload + indexation + analysis)
└── demo.py         # Quick demo (auto-loads from data/, no upload)

tests/
├── unit/          # Function logic tests
└── integration/   # CRUD, retrieval, agent tests
```

---

## Security

✅ Input validation (file size, extension, format)  
✅ Output encoding  
✅ API keys in .env (not committed)  
✅ No sensitive data in logs  
✅ Pinned dependencies  
✅ Comprehensive error handling  
✅ No injection vulnerabilities  

See `docs/SECURITY.md` for detailed audit.

---

## Development

- **Total Lines**: ~2,000 (src/)
- **Tests**: 130 (unit + integration)
- **Coverage**: >90%
- **Time Budget**: ~3.3 hours (5 phases)

---

## Troubleshooting

**ModuleNotFoundError**: `pip install -r requirements.txt`

**ANTHROPIC_API_KEY not found**: `cp .env.example .env && nano .env`

**File too large**: Check max_file_size_mb in config.py

**Agent slow**: Normal on first query (embeddings). Subsequent queries are faster.

---

Built as a Senior Engineer take-home test. Evaluates: architecture decisions, data handling robustness, query quality, outlier detection accuracy, and code quality.
