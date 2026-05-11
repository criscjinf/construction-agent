# 🔍 MODO DEBUG - Logging Detalhado

## O que é?

Modo DEBUG fornece **logs detalhados** de cada recurso acionado, mostrando:
- Qual ferramenta está sendo usada
- Qual arquivo está sendo processado
- Qual função está sendo executada
- Onde erros ocorrem exatamente

## Como Ativar?

### Opção 1: Variável de Ambiente (Recomendado)

Edite `.env`:
```env
LOG_LEVEL=DEBUG
LOG_FILE=logs/construction_agent.log
```

Execute normalmente:
```bash
python3 run_agent.py
```

### Opção 2: Via Linha de Comando

```bash
LOG_LEVEL=DEBUG python3 run_agent.py
```

---

## Exemplo de Saída em DEBUG Mode

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

## Níveis de Log

Configure `LOG_LEVEL` no `.env`:

| Nível | Símbolo | Cor | Mostra | Uso |
|-------|---------|-----|--------|-----|
| **DEBUG** | 🔍 | Cyan | DEBUG+INFO+WARN+ERROR+CRITICAL | Detalhes completos |
| **INFO** | ✅ | Green | INFO+WARN+ERROR+CRITICAL | Operações principais |
| **WARNING** | ⚠️ | Yellow | WARN+ERROR+CRITICAL | Apenas alertas |
| **ERROR** | ❌ | Red | ERROR+CRITICAL | Apenas erros |
| **CRITICAL** | 🚨 | Magenta | CRITICAL | Apenas críticos |

---

## Quando Usar LOG_LEVEL=DEBUG

### ✅ Use LOG_LEVEL=DEBUG quando:

1. **Debugar erros**
   - Qual recurso falhou?
   - Em qual ponto exato?

2. **Entender o fluxo**
   - Como o sistema processa dados?
   - Qual caminho o código segue?

3. **Otimizar performance**
   - Qual operação demora mais?
   - Onde está o gargalo?

4. **Desenvolvimento**
   - Adicionar novas features
   - Modificar comportamento

### ❌ Use LOG_LEVEL=INFO quando:

1. **Produção**
   - Menos overhead de logging
   - Saída mais limpa

2. **Usuário final**
   - Menos ruído no console
   - Apenas informações importantes

---

## Estrutura de Logs

### Console (com LOG_LEVEL=DEBUG):

```
timestamp | LEVEL    | module_name        | function_name | message
2026-05-08 14:32:45 | DEBUG   | document_loader    | load_and_index | Processing file...
```

### Arquivo Log:

Todos os logs são salvos em `logs/construction_agent.log` (inclui DEBUG mesmo se console mostrar INFO)

---

## Configuração no `.env`

```env
LOG_LEVEL=DEBUG    # Mostra logs detalhados no console
LOG_LEVEL=INFO     # Mostra apenas operações principais
LOG_LEVEL=WARNING  # Mostra apenas alertas
LOG_FILE=logs/construction_agent.log
```

---

## Interpretando Logs

### Exemplo 1: Carregamento de CSV

```
🔍 DEBUG | document_loader | load_and_index_csv | Processing: sample_bid_tabulation.csv
🔍 DEBUG | loaders | load | Auto-detected format: CSV
🔍 DEBUG | parsers | parse | Inferring schema from CSV...
✅ INFO  | document_loader | load_and_index_csv | Indexed 120 items
```

**Significa**: CSV foi detectado → esquema inferido → 120 items indexados ✅

### Exemplo 2: Erro em PDF

```
🔍 DEBUG | document_loader | load_and_index_pdf | Processing: plans.pdf
🔍 DEBUG | pdf_parser | _extract_text | Attempting PyPDF2 extraction...
⚠️ WARN  | pdf_parser | _extract_text | PyPDF2 failed, trying OCR...
❌ ERROR | document_loader | load_and_index_pdf | OCR extraction failed: tesseract not found
```

**Significa**: PyPDF2 falhou → tentou OCR → OCR não disponível → erro ❌

### Exemplo 3: Query do Agente

```
📍 INFO  | run_agent | main | User query: What are the top items?
🔄 DEBUG | run_agent | main | Executing agent.query()...
🔧 INFO  | run_agent | main | Agent processing query...
✅ INFO  | run_agent | main | Agent returned response
```

**Significa**: Query recebida → agente processou → resposta retornada ✅

---

## Configurações

### No `.env`:

```env
# Enable debug logging
DEBUG=true

# Log file path (created automatically)
LOG_FILE=logs/construction_agent.log
```

### Comportamento por Nível:

| DEBUG | Console | File |
|-------|---------|------|
| true | DEBUG + INFO + WARN + ERROR | DEBUG + INFO + WARN + ERROR |
| false | INFO + WARN + ERROR | DEBUG + INFO + WARN + ERROR |

---

## Analisando Problemas

### Problema: "Agent não retorna resposta"

**Passos:**
1. Ative DEBUG=true
2. Execute `python3 run_agent.py`
3. Faça a query
4. Procure por:
   ```
   🔧 INFO | Agent processing query...
   ✅ INFO | Agent returned response
   ```
5. Se o erro ocorre entre essas linhas, o problema está no agente

**Verifique no log:**
```bash
grep "ERROR\|CRITICAL" logs/construction_agent.log
```

### Problema: "PDF não indexou"

**Passos:**
1. Procure por logs do PDF:
   ```bash
   grep "pdf_parser\|PDF" logs/construction_agent.log
   ```

2. Se vir:
   ```
   ⚠️ No text extracted from PDF
   ```
   → PDF pode estar corrompido ou em formato não suportado

3. Se vir:
   ```
   ❌ tesseract not found
   ```
   → OCR não está instalado (opcional)

---

## Dicas Úteis

### Ver apenas ERRORs:
```bash
grep "ERROR\|CRITICAL" logs/construction_agent.log
```

### Ver fluxo completo:
```bash
tail -f logs/construction_agent.log
```

### Contar eventos por tipo:
```bash
grep "DEBUG\|INFO\|WARN\|ERROR" logs/construction_agent.log | sort | uniq -c
```

### Gerar relatório:
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
- Disk: ~1-5MB por sessão (log files)
- Console: Mais lento (mais output)

**LOG_LEVEL=INFO:**
- CPU: Normal
- Disk: Minimal
- Console: Rápido

**Recomendação:** Use LOG_LEVEL=DEBUG durante desenvolvimento, LOG_LEVEL=INFO em produção.

---

## Exemplo Completo de Sessão

```bash
$ DEBUG=true python3 run_agent.py
[Menu de seleção de documentos]
[Indexação com logs detalhados]
[Agent pronto]

📍 You: What are the top 3 items?

🤖 Claude is analyzing...
[Resposta do agente]

📍 You: quit
✅ Goodbye!

$ cat logs/construction_agent.log
[Todos os logs da sessão]
```

---

## Troubleshooting

### Logs não aparecem no console?

**Solução:**
1. Verifique `.env`:
   ```env
   LOG_LEVEL=DEBUG
   ```

2. Reinicie o script

3. Se ainda não funcionar:
   ```bash
   LOG_LEVEL=DEBUG python3 run_agent.py 2>&1 | tee debug.log
   ```

### Arquivo de log cresce muito?

**Solução:**
1. Limpe o antigo:
   ```bash
   rm logs/construction_agent.log
   ```

2. Ou comprima:
   ```bash
   gzip logs/construction_agent.log
   ```

3. Defina LOG_LEVEL=INFO para sessões normais

---

**Pronto para debugar! 🔍**

```bash
LOG_LEVEL=DEBUG python3 run_agent.py
```
