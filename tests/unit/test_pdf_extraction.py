#!/usr/bin/env python3
"""Quick test of PDF extraction capabilities"""

from dotenv import load_dotenv
load_dotenv(".env")

from pathlib import Path
from src.data.parsers import PDFParser

print("=" * 80)
print("🧪 TESTE DE EXTRAÇÃO DE PDFs")
print("=" * 80)

pdf_files = list(Path("data").glob("*.pdf"))
print(f"\nEncontrados {len(pdf_files)} PDFs\n")

for pdf_file in pdf_files:
    print(f"📄 {pdf_file.name} ({pdf_file.stat().st_size / 1024 / 1024:.1f}MB)")
    
    parser = PDFParser(verbose=False)
    text = parser._extract_text(str(pdf_file))
    
    if text:
        print(f"   ✅ Extraído: {len(text)} caracteres")
        print(f"   Primeiras linhas:\n{text[:300]}...\n")
    else:
        print(f"   ❌ Nenhum texto extraído\n")

print("=" * 80)
