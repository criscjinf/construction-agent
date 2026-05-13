# Configuration Management

## Overview

The Construction Estimating Agent uses a centralized `Config` class to manage all environment-based configuration. This ensures consistency across the application and makes it easy to customize behavior via environment variables.

## Configuration File

Create a `.env` file by copying the template:

```bash
cp .env.example .env
```

Then fill in your API keys and optional settings.

## Environment Variables

### Required Variables

#### `OPENAI_API_KEY`
- **Purpose**: Generate embeddings for semantic search
- **Required**: Yes
- **Get from**: https://platform.openai.com/api-keys
- **Example**: `sk-proj-sX7cz1uThNPY...`

#### `ANTHROPIC_API_KEY`
- **Purpose**: Power the Claude agent for natural language reasoning
- **Required**: Yes  
- **Get from**: https://console.anthropic.com/
- **Example**: `sk-ant-v3-sX7cz1uT...`

### Optional Variables

#### `EMBEDDING_MODEL`
- **Purpose**: Choose which OpenAI embedding model to use
- **Default**: `text-embedding-3-small`
- **Options**:
  - `text-embedding-3-small`: 1536 dimensions, ~$0.02 per 1M tokens (recommended)
  - `text-embedding-3-large`: 3072 dimensions, ~$0.13 per 1M tokens
- **Example**:
  ```
  EMBEDDING_MODEL=text-embedding-3-large
  ```

#### `AGENT_MODEL`
- **Purpose**: Choose which Claude model powers the agent
- **Default**: `claude-sonnet-4-6`
- **Options**:
  - `claude-sonnet-4-6`: Balanced speed/quality (recommended)
  - `claude-opus-4-7`: Most capable but slower
- **Example**:
  ```
  AGENT_MODEL=claude-opus-4-7
  ```

#### `LOG_LEVEL`
- **Purpose**: Control logging verbosity
- **Default**: `INFO`
- **Options**:
  - `DEBUG`: Verbose output with function names and line numbers
  - `INFO`: Standard operational messages
  - `WARNING`: Only warnings and errors
  - `ERROR`: Only errors
- **Example**:
  ```
  LOG_LEVEL=DEBUG
  ```

#### `LOG_FILE`
- **Purpose**: Write logs to a file in addition to console
- **Default**: Not set (console only)
- **Example**:
  ```
  LOG_FILE=logs/construction_agent.log
  ```

## Using Configuration in Code

### Access Configuration

```python
from src.config import Config

# Get models
embedding_model = Config.get_embedding_model()
agent_model = Config.get_agent_model()

# Check debug mode
if Config.is_debug():
    print("Debug mode enabled")

# View all config
print(Config.to_dict())
# Output: {
#   'embedding_model': 'text-embedding-3-small',
#   'agent_model': 'claude-sonnet-4-6',
#   'log_level': 'INFO',
#   'log_file': None
# }
```

### Creating Clients with Configuration

```python
from src.config import Config
from src.vectorstore.embeddings import OpenAIEmbeddingClient
from src.agent.executors import AnthropicAgentExecutor

# Embedding client uses Config by default
embedding = OpenAIEmbeddingClient()  # Uses Config.EMBEDDING_MODEL

# Agent executor uses Config by default
agent = AnthropicAgentExecutor(projects=projects)  # Uses Config.AGENT_MODEL

# Override per instance if needed
embedding = OpenAIEmbeddingClient(model="text-embedding-3-large")
agent = AnthropicAgentExecutor(projects=projects, model="claude-opus-4-7")
```

## Configuration Validation

The `Config` class includes a `validate()` method that checks critical settings:

```python
from src.config import Config

try:
    Config.validate()
    print("✅ Configuration is valid")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

This is useful in application startup to fail fast if keys are missing.

## Quick Reference

### Minimal Setup
```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Development Setup (Debug)
```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
LOG_LEVEL=DEBUG
LOG_FILE=logs/dev.log
```

### Production Setup (Fast)
```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_MODEL=text-embedding-3-small
AGENT_MODEL=claude-sonnet-4-6
LOG_LEVEL=INFO
```

### Production Setup (Capable)
```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_MODEL=text-embedding-3-large
AGENT_MODEL=claude-opus-4-7
LOG_LEVEL=WARNING
LOG_FILE=logs/production.log
```

## Cost Optimization

### Embeddings Cost
| Model | Cost per 1M | Dimensions | Use Case |
|-------|------------|-----------|----------|
| text-embedding-3-small | $0.02 | 1536 | Recommended for most uses |
| text-embedding-3-large | $0.13 | 3072 | High-precision search needed |

**Estimate**: Processing a 100-item CSV:
- 400-600 tokens per item for embedding
- ~50K tokens total → $0.001 per run with small model
- ~$0.006 per run with large model

### Agent Cost
| Model | Input | Output | Speed | Capability |
|-------|-------|--------|-------|------------|
| claude-sonnet-4-6 | $3/1M | $15/1M | Fast | Balanced ✓ |
| claude-opus-4-7 | $15/1M | $75/1M | Slower | Best |

**Estimate**: Agent query with 5 tool iterations:
- ~2000 tokens input, ~500 tokens output
- Sonnet: ~$0.01 per query
- Opus: ~$0.06 per query

## Troubleshooting

### "API key not configured"
```
Error: OPENAI_API_KEY not configured

Solution:
1. Check .env file exists
2. Check OPENAI_API_KEY is set (not commented out)
3. Check key format is valid: sk-proj-...
```

### "Unknown embedding model"
```
Error: embedding model 'text-embedding-4' not found

Solution:
1. Check EMBEDDING_MODEL spelling
2. Use only: text-embedding-3-small or text-embedding-3-large
3. Check you have access to the model in your OpenAI account
```

### "Unknown agent model"
```
Error: model 'gpt-4' not found or not available

Solution:
1. Check AGENT_MODEL spelling
2. Use only Claude models: claude-sonnet-4-6, claude-opus-4-7
3. Check you have access via https://console.anthropic.com/
```

## Advanced: Custom Configuration

To add custom configuration options:

1. **Add to Config class**:
   ```python
   # src/config.py
   CUSTOM_OPTION: str = os.getenv("CUSTOM_OPTION", "default")
   ```

2. **Add to .env.example**:
   ```bash
   # .env.example
   CUSTOM_OPTION=value
   ```

3. **Use in code**:
   ```python
   value = Config.CUSTOM_OPTION
   ```

4. **Add tests**:
   ```python
   # tests/unit/test_config.py
   def test_custom_option():
       assert Config.CUSTOM_OPTION == "value"
   ```

---

**Last updated**: 2026-05-13  
**Configuration version**: 1.0
