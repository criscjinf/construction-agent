# Unmapped Fields: Handling Unknown CSV Columns

## Overview

The Construction Estimating Agent now automatically captures and utilizes unknown CSV columns (fields not in the predefined schema). This enables flexible analysis of CSVs with custom or varying column structures.

## How It Works

### 1. **Automatic Detection**

When you load a CSV, the system:
- Detects all columns that don't match known field names
- Automatically infers each column's type: `numeric`, `date`, or `string`
- Stores both the raw value and any inferred numeric parsing

### 2. **Type Inference Strategy**

For each unmapped column, the system samples the first non-null value and classifies it:

```
"1500.50"     → numeric (can be converted to float)
"2026-05-13"  → date (parseable as datetime)
"HIGH"        → string (not numeric or date)
""            → string (empty strings default to string)
```

### 3. **Storage in BidItem**

Each bid item stores unmapped fields in a dictionary:

```python
item.unmapped_fields = {
    "CUSTOM_COST": UnmappedField(
        raw="1500.50",
        inferred_type="numeric",
        parsed_value=1500.50
    ),
    "NOTES": UnmappedField(
        raw="Good quality",
        inferred_type="string",
        parsed_value=None
    )
}
```

## Example: CSV with Custom Columns

**Input CSV:**
```
PROJ_ID,ITEM_NO,ITEM_DESC,UNIT,QTY,UNIT_PR,EXT_AMT,BIDDER,CUSTOM_COST,QC_RATING,SUPPLIER
001,1001,EXCAVATION,CY,100,25.50,2550.00,Bidder A,1500,9.5,Smith Bros
001,1002,PAVING,TON,50,75.00,3750.00,Bidder A,2000,8.8,Asphalt Co
001,1001,EXCAVATION,CY,100,24.75,2475.00,Bidder B,1400,9.2,Jones Inc
001,1002,PAVING,TON,50,76.50,3825.00,Bidder B,2100,8.5,Paving Plus
```

**System Detection:**
```
Unmapped columns detected:
  CUSTOM_COST → numeric
  QC_RATING   → numeric  
  SUPPLIER    → string
```

**Agent Capabilities:**

You can now ask the agent:

```
"What is the total CUSTOM_COST across all bids?"
→ Aggregates all CUSTOM_COST values: 6000

"What is the average QC_RATING?"
→ Computes: (9.5 + 8.8 + 9.2 + 8.5) / 4 = 9.0

"Find suppliers mentioned in the data"
→ Extracts SUPPLIER column values: Smith Bros, Asphalt Co, Jones Inc, Paving Plus

"Get statistics for CUSTOM_COST"
→ Returns: min=1400, max=2100, avg=1750, median=1750
```

## Aggregation Operations

For unmapped numeric fields, the agent supports:

| Operation | Description | Example |
|-----------|-------------|---------|
| `sum` | Total of all values | `1500 + 2000 + 1400 + 2100 = 7000` |
| `avg` | Average value | `(1500+2000+1400+2100) / 4 = 1750` |
| `min` | Minimum value | `1400` |
| `max` | Maximum value | `2100` |
| `median` | Middle value | `1750` |

## Type Safety & Conversion

The system is intelligent about type handling:

### Numeric Fields
- If detected as `numeric` during parsing, uses the pre-parsed float value
- If detected as `string` but looks numeric, converts on-demand
- Silently skips non-convertible values (e.g., "N/A", "TBD")

```python
# Example: Aggregating with some invalid values
COST values: [1500, 2000, "N/A", 2100]
Aggregation result: sum = 5600 (skipped "N/A")
```

### Date Fields
- Automatically detected but preserved as strings for now
- Future enhancement: temporal analysis

### String Fields  
- Preserved as-is
- No conversion attempts
- Useful for categorical analysis

## Implementation Details

### UnmappedField Model

```python
class UnmappedField(BaseModel):
    raw: str                                      # Original CSV value
    inferred_type: Literal["numeric", "date", "string"]
    parsed_value: Optional[float]                 # Numeric value if applicable
```

### Detection Logic (ValueConverter.detect_type)

```python
def detect_type(value: Any) -> str:
    # Try float conversion
    try:
        float(value)
        return "numeric"
    except:
        pass
    
    # Try date parsing
    try:
        pd.to_datetime(value)
        return "date"
    except:
        pass
    
    # Default to string
    return "string"
```

### Aggregation Method

```python
# In AggregationService:
def aggregate_unmapped_field(
    projects: list[Project],
    field_name: str,
    operation: str = "sum"  # sum|avg|min|max|median
) -> Optional[float]:
    # Collect numeric values from all items
    # Handle both pre-parsed and string values
    # Perform aggregation
```

## Agent Tool Integration

The `aggregate_items` tool now accepts unmapped field names:

**Before:**
```json
{
  "metric": "unit_price",  // Only: unit_price, qty, ext_amt
  "limit": 5,
  "order": "desc"
}
```

**After:**
```json
{
  "metric": "CUSTOM_COST",    // Any field name, including unmapped
  "operation": "sum",         // Aggregation operation
  "limit": 5,
  "order": "desc"
}
```

## Use Cases

1. **Custom Cost Tracking**
   - CSVs with proprietary cost columns
   - Agent can sum/average without re-mapping

2. **Quality Metrics**
   - QC ratings, compliance scores
   - Automatic aggregation and statistics

3. **Supplementary Data**
   - Supplier names, dates, project codes
   - Preserved for reference in responses

4. **Schema Evolution**
   - Add new columns to existing CSVs
   - System auto-detects and includes in analysis
   - No code changes needed

## Limitations & Future Work

### Current
- Type detection happens once during parsing
- String values in numeric fields require conversion attempt
- No explicit field ordering/prioritization

### Future Enhancements
- Temporal analysis for detected date fields
- Custom type rules per field name
- Field-specific conversion strategies
- Export unmapped fields with results

## Testing

The implementation includes comprehensive tests for:

- Type detection edge cases (empty, None, mixed)
- Parsing with unmapped columns
- Aggregation operations (sum, avg, min, max, median)
- Invalid value handling (non-convertible strings)
- Multi-project aggregation

Run tests:
```bash
pytest tests/unit/test_unmapped_fields.py -v
```

## Example Query Walkthrough

**User:** *"Analyze the CUSTOM_COST field for all items"*

1. **Agent receives:** Query about "CUSTOM_COST"
2. **Field lookup:** Finds CUSTOM_COST in item.unmapped_fields
3. **Type check:** Detected as "numeric"
4. **Aggregation:** Calls `aggregate_unmapped_field(projects, "CUSTOM_COST", "sum")`
5. **Service logic:**
   - Iterates all projects → all items
   - For each item, extracts CUSTOM_COST value
   - Uses pre-parsed numeric value (if available)
   - Sums: 1500 + 2000 + 1400 + 2100 = 7000
6. **Response:** "Total CUSTOM_COST: $7000 (4 items, avg: $1750)"

---

**Key Insight:** The agent doesn't need to know about CUSTOM_COST in advance. The system dynamically discovers, types, and aggregates any column.
