# 🔍 DEBUG Mode - Detailed Logging

## What is it?

DEBUG mode provides **detailed logs** of each resource triggered, showing:
- Which tool is being used
- Which file is being processed
- Which function is executing
- Where errors occur exactly

## How to Enable?

### Option 1: Environment Variable (Recommended)

Edit `.env`:
```env
LOG_LEVEL=DEBUG
LOG_FILE=logs/construction_agent.log
```

Run normally:
```bash
python3 scripts/run_agent.py
```

### Option 2: Via Command Line

```bash
LOG_LEVEL=DEBUG python3 scripts/run_agent.py
```

---

## Example DEBUG Mode Output

### Console Output:

```
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Created temporary database: /tmp/tmp123.db
2026-05-08 14:32:45 | INFO    | run_agent            | main                 | 📊 Initializing SQLite vector store at /tmp/tmp123.db
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | ✅ Vector store initialized
2026-05-08 14:32:45 | INFO    | run_agent            | main                 | 📦 Initializing DocumentLoader with mock embeddings
2026-05-08 14:32:46 | DEBUG   | run_agent            | main                 | ✅ DocumentLoader initialized
2026-05-08 14:32:46 | INFO    | run_agent            | main                 | 📄 Starting indexing of 1 documents...
2026-05-08 14:32:46 | DEBUG   | run_agent            | main                 | 🔄 Indexing CSV: sample_bid_tabulation.csv
2026-05-08 14:32:47 | INFO    | run_agent            | main                 | ✅ CSV indexed: sample_bid_tabulation.csv (120 items)
```

### Log File (`logs/construction_agent.log`):

```
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Created temporary database: /tmp/tmp123.db
2026-05-08 14:32:45 | DEBUG   | run_agent            | main                 | Starting document loading process...
2026-05-08 14:32:45 | DEBUG   | document_loader      | load_and_index_csv   | Processing: sample_bid_tabulation.csv
2026-05-08 14:32:46 | DEBUG   | loaders              | load                 | Auto-detected format: CSV
2026-05-08 14:32:46 | DEBUG   | parsers              | parse                | Inferring schema from CSV...
2026-05-08 14:32:47 | DEBUG   | document_loader      | load_and_index_csv   | Embedded 120 items
2026-05-08 14:32:47 | INFO    | run_agent            | main                 | ✅ CSV indexed: sample_bid_tabulation.csv (120 items)
```

---

## Log Levels

Configure `LOG_LEVEL` in `.env`:

| Level | Symbol | Color | Shows | Use |
|-------|--------|-------|-------|-----|
| **DEBUG** | 🔍 | Cyan | DEBUG+INFO+WARN+ERROR+CRITICAL | Full details |
| **INFO** | ✅ | Green | INFO+WARN+ERROR+CRITICAL | Main operations |
| **WARNING** | ⚠️ | Yellow | WARN+ERROR+CRITICAL | Alerts only |
| **ERROR** | ❌ | Red | ERROR+CRITICAL | Errors only |
| **CRITICAL** | 🚨 | Magenta | CRITICAL | Critical only |

---

## When to Use LOG_LEVEL=DEBUG

### ✅ Use LOG_LEVEL=DEBUG when:

1. **Debugging errors**
   - Which resource failed?
   - At which exact point?

2. **Understanding the flow**
   - How does the system process data?
   - Which path does the code take?

3. **Optimizing performance**
   - Which operation takes longest?
   - Where is the bottleneck?

4. **Development**
   - Adding new features
   - Modifying behavior

### ❌ Use LOG_LEVEL=INFO when:

1. **Production**
   - Less logging overhead
   - Cleaner output

2. **End user**
   - Less noise in console
   - Only important information

---

## Log Structure

### Console (with LOG_LEVEL=DEBUG):

```
timestamp | LEVEL    | module_name        | function_name | message
2026-05-08 14:32:45 | DEBUG   | document_loader    | load_and_index | Processing file...
```

### Log File:

All logs are saved to `logs/construction_agent.log` (includes DEBUG even if console shows INFO)

---

## Configuration in `.env`

```env
LOG_LEVEL=DEBUG    # Show detailed logs on console
LOG_LEVEL=INFO     # Show only main operations
LOG_LEVEL=WARNING  # Show alerts only
LOG_FILE=logs/construction_agent.log
```

---

## Interpreting Logs

### Example 1: CSV Loading

```
🔍 DEBUG | document_loader | load_and_index_csv | Processing: sample_bid_tabulation.csv
🔍 DEBUG | loaders | load | Auto-detected format: CSV
🔍 DEBUG | parsers | parse | Inferring schema from CSV...
✅ INFO  | document_loader | load_and_index_csv | Indexed 120 items
```

**Means**: CSV detected → schema inferred → 120 items indexed ✅

### Example 2: PDF Error

```
🔍 DEBUG | document_loader | load_and_index_pdf | Processing: plans.pdf
🔍 DEBUG | pdf_parser | _extract_text | Attempting PyPDF2 extraction...
⚠️ WARN  | pdf_parser | _extract_text | PyPDF2 failed, trying OCR...
❌ ERROR | document_loader | load_and_index_pdf | OCR extraction failed: tesseract not found
```

**Means**: PyPDF2 failed → tried OCR → OCR unavailable → error ❌

### Example 3: Agent Query

```
📍 INFO  | run_agent | main | User query: What are the top items?
🔄 DEBUG | run_agent | main | Executing agent.query()...
🔧 INFO  | run_agent | main | Agent processing query...
✅ INFO  | run_agent | main | Agent returned response
```

**Means**: Query received → agent processed → response returned ✅

---

## Useful Commands

### View only ERRORs:
```bash
grep "ERROR\|CRITICAL" logs/construction_agent.log
```

### View complete flow:
```bash
tail -f logs/construction_agent.log
```

### Count events by type:
```bash
grep "DEBUG\|INFO\|WARN\|ERROR" logs/construction_agent.log | sort | uniq -c
```

### Generate report:
```bash
python3 -c "
import re
with open('logs/construction_agent.log') as f:
    logs = f.readlines()
    levels = {}
    for line in logs:
        match = re.search(r'(DEBUG|INFO|WARN|ERROR|CRITICAL)', line)
        if match:
            level = match.group(1)
            levels[level] = levels.get(level, 0) + 1
    
    for level, count in sorted(levels.items()):
        print(f'{level}: {count}')
"
```

---

## Performance Impact

**LOG_LEVEL=DEBUG:**
- CPU: +5-10% (logging overhead)
- Disk: ~1-5MB per session (log files)
- Console: Slower (more output)

**LOG_LEVEL=INFO:**
- CPU: Normal
- Disk: Minimal
- Console: Fast

**Recommendation:** Use LOG_LEVEL=DEBUG during development, LOG_LEVEL=INFO in production.

---

## Complete Session Example

```bash
$ LOG_LEVEL=DEBUG python3 scripts/run_agent.py
[Document selection menu]
[Indexing with detailed logs]
[Agent ready]

📍 You: What are the top 3 items?

🤖 Claude is analyzing...
[Agent response]

📍 You: quit
✅ Goodbye!

$ cat logs/construction_agent.log
[All session logs]
```

---

## Troubleshooting

### Logs not appearing in console?

**Solution:**
1. Check `.env`:
   ```env
   LOG_LEVEL=DEBUG
   ```

2. Restart the script

3. If still not working:
   ```bash
   LOG_LEVEL=DEBUG python3 scripts/run_agent.py 2>&1 | tee debug.log
   ```

### Log file growing too large?

**Solution:**
1. Clean up old one:
   ```bash
   rm logs/construction_agent.log
   ```

2. Or compress:
   ```bash
   gzip logs/construction_agent.log
   ```

3. Set LOG_LEVEL=INFO for normal sessions

---

**Ready to debug! 🔍**

```bash
LOG_LEVEL=DEBUG python3 scripts/run_agent.py
```
