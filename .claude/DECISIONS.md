# Architectural Decisions

## ADR-001: Language Selection (APPROVED)

**Decision**: Use Python 3.11  
**Date**: 2026-05-06  

**Why**: 
- Fast iteration (matches 3-4 hour expectation)
- Rich ecosystem: pandas (CSV), pytesseract (OCR), scikit-learn (stats)
- Data transformation is idiomatic

**Trade-offs**:
- ✅ Fast development
- ❌ Slower than Go/Rust at runtime (acceptable for this scale)

---

## ADR-002: Vector Store Backend (APPROVED)

**Decision**: SQLite with in-memory vector column (not Pinecone/Weaviate)  
**Date**: 2026-05-06  

**Why**:
- Local-only requirement
- <5 minute setup (pip install, no API signup)
- Inspectable (SQLite browser)
- Easy to test (no network calls)

**Trade-offs**:
- ✅ Zero external dependencies
- ❌ Slower than managed solutions at scale (acceptable for test)
- ❌ Sequential search (fine for <10k embeddings)

**Swap Strategy**: Interface abstraction in `vectorstore/storage.py` allows swapping to Pinecone later.

---

## ADR-003: Agent Framework (APPROVED)

**Decision**: Anthropic Claude API with tool-use (not LangChain)  
**Date**: 2026-05-06  

**Why**:
- Native structured tool-use
- Composable: agent can call multiple tools in one response
- Cleaner API (no abstraction overhead)
- Better for this specific use case

**Trade-offs**:
- ✅ Composable tools
- ✅ Structured outputs (Pydantic)
- ❌ Less flexible than LangChain for complex workflows (not needed)

---

## ADR-004: Embedding Model (APPROVED)

**Decision**: OpenAI text-embedding-3-small  
**Date**: 2026-05-06  

**Why**:
- Fast (1536 dimensions vs 3072 for large)
- Cheap (2x cost difference)
- Good enough for construction data (semantic similarity is clear)
- Required by spec

**Trade-offs**:
- ✅ Speed + cost
- ❌ Slightly lower quality than 3-large (acceptable for this domain)

---

## ADR-005: CSV Parsing Strategy (APPROVED)

**Decision**: Schema inference (auto-detect columns) + adaptive parsing  
**Date**: 2026-05-06  

**Why**:
- Core test requirement: "handle data that varies significantly"
- Don't assume column names/order/presence
- Fallback: skip unknown columns, log warnings

**Implementation**:
```python
# CSVParser.infer_schema():
1. Read first N rows
2. Detect column types (numeric, string, date)
3. Handle aliases (ENG_EST_UNIT_PR vs eng_est_unit_pr)
4. Mark missing columns with warning
5. Return normalized schema
```

**Trade-offs**:
- ✅ Handles variability
- ❌ More complex than hardcoded schema
- ❌ May misidentify column types (solved by testing)

---

## ADR-006: PDF Extraction (APPROVED)

**Decision**: PyPDF2 (text) + pytesseract (OCR fallback)  
**Date**: 2026-05-06  

**Why**:
- Handle both text-native and scanned PDFs
- Graceful degradation (extract what we can)
- Open source (no vendor lock-in)

**Fallback Strategy**:
1. Try PyPDF2 (fast, works for text-native PDFs)
2. If OCR needed: pytesseract (requires tesseract binary)
3. If OCR fails: return "Could not extract text" + continue

**Trade-offs**:
- ✅ Handles both PDF types
- ❌ Requires tesseract system library
- ❌ OCR is imperfect (accepted by spec: "perfect OCR not evaluated")

---

## ADR-007: Tool Definitions as Pydantic Models (APPROVED)

**Decision**: Tools are Pydantic models with examples  
**Date**: 2026-05-06  

**Why**:
- Type-safe: agent can reason about inputs/outputs
- Serializable: easy to send to LLM
- Composable: agent chains tools based on query
- Structured: agent responses are predictable

**Example**:
```python
class DetectOutliersInput(BaseModel):
    item_type: str = Field(..., description="Category of items (e.g., 'ASPHALT PAVING')")
    method: str = Field("zscore", description="Method: 'zscore' or 'iqr'")
    sensitivity: float = Field(2.0, description="Threshold (e.g., 2.0σ)")

class DetectOutliersOutput(BaseModel):
    outliers: list[Outlier]
    method_used: str
    threshold_value: float
```

---

## ADR-008: Outlier Detection Approach (APPROVED)

**Decision**: Z-score (primary) + IQR (fallback), configurable sensitivity  
**Date**: 2026-05-06  

**Why**:
- Z-score: works on normally distributed data (construction costs often are)
- IQR: robust to extreme values
- Configurable: agent can adjust sensitivity per query

**Edge Cases Handled**:
- All values equal: return empty (nothing is an outlier)
- Single value: return empty (need context)
- <3 values: skip (insufficient data)

**Output**: 
```python
# Returns: [Outlier(value=660, zscore=3.2, percentile=99.1, description="3.2σ above mean")]
```

---

## ADR-009: Project Structure (APPROVED)

**Decision**: Modular organization by responsibility  
**Date**: 2026-05-06  

**Structure**:
```
src/
├── data/          # Loading, parsing, models, validation
├── vectorstore/   # Embeddings, storage, retrieval
├── analysis/      # Statistics, outlier detection, comparisons
├── agent/         # LLM orchestration and tools
└── config.py      # Config management
```

**Why**:
- High cohesion (related code together)
- Low coupling (data → analysis → agent one-way)
- Easy to test (each module independent)

---

## ADR-010: Testing Strategy (APPROVED)

**Decision**: Unit + Integration, >80% coverage, fixtures for sample data  
**Date**: 2026-05-06  

**Coverage Target**:
- `data/`: 85% (parsers are critical)
- `analysis/`: 85% (outlier detection must be correct)
- `vectorstore/`: 75% (mostly integration)
- `agent/`: 70% (harder to test LLM interactions)

**Testing Approach**:
- Mock OpenAI API (don't call real endpoint in tests)
- Use real sample CSV/PDF (in tests/fixtures/)
- Integration tests: end-to-end flow

---

## ADR-011: Security Approach (APPROVED)

**Decision**: OWASP Top 10 compliance, stored in .env, no logging of sensitive data  
**Date**: 2026-05-06  

**Specific**:
- API keys in .env (not committed)
- Input validation: file size, extension, format
- Injection prevention: parameterize prompts
- Error handling: generic messages to user, full logs internally
- Dependencies: pinned versions

---

## Decision Status Summary

| ADR | Decision | Status | Impact |
|-----|----------|--------|--------|
| 001 | Python 3.11 | ✅ APPROVED | Medium (tooling choice) |
| 002 | SQLite vectors | ✅ APPROVED | High (architecture) |
| 003 | Claude API | ✅ APPROVED | High (agent core) |
| 004 | OpenAI embeddings | ✅ APPROVED | Medium (search quality) |
| 005 | Schema inference | ✅ APPROVED | High (data handling) |
| 006 | PDF strategy | ✅ APPROVED | Medium (robustness) |
| 007 | Pydantic tools | ✅ APPROVED | High (tool-use) |
| 008 | Z-score + IQR | ✅ APPROVED | Medium (analysis) |
| 009 | Modular structure | ✅ APPROVED | High (maintainability) |
| 010 | Testing strategy | ✅ APPROVED | Medium (quality gate) |
| 011 | Security approach | ✅ APPROVED | High (compliance) |

All decisions made with "extensibility first" mindset: swap SQLite → Pinecone, Python → Go, etc. without breaking interfaces.
