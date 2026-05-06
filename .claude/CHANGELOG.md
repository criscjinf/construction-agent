# Changelog

## [2026-05-06] — Project Initialization

### Added
- **Project Setup**: Construction Estimating Multi-Modal Agent
- **Architecture**: 5-phase execution plan with clear separation of concerns
- **CLAUDE.md**: Quality standards, patterns, data handling guidelines
- **Decisions**: 11 architectural decisions documented (ADR-001 through ADR-011)
- **.claude/ Structure**: STATUS.md, DECISIONS.md, NEXT_STEPS.md, CHANGELOG.md
- **Git**: Repository initialized
- **Requirements**: Template requirements.txt ready for Phase 1

### Key Decisions Made
1. Python 3.11 (fast iteration)
2. SQLite vectors (local-only, <5min setup)
3. Claude API tool-use (composable, structured)
4. Schema inference for CSV (handles variability)
5. PyPDF2 + pytesseract (handles both PDF types)
6. Pydantic tools (type-safe, serializable)
7. Z-score + IQR outlier detection (configurable)

### Test Expectations
- Evaluate on: Architecture, data handling, query quality, outlier detection, code quality
- Separate good from great: Tool-use patterns where agent composes operations
- Data variability is the test: Parser must handle column variations
- No over-engineering: Pragmatic choices aligned with 3-4 hour expectation

### Next Phase
Phase 1: Data Models + CSV Parser (Schema inference, Pydantic models, validation)

---

## Development Log (to be updated)

Entries added as work progresses:
- When completing each phase
- When making significant decisions
- When encountering/resolving blockers
- When test coverage improves
