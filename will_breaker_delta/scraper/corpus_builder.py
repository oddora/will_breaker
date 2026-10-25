"""
Corpus Builder — Will Breaker Delta-Detection Phase 2
Aggregates documents from all sources into unified corpus.
Supports both .jsonl and .txt (DOCUMENT ... --- format) files.
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


class CorpusBuilder:
    """Build and manage the delta-detection corpus."""
    
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = Path(corpus_dir)
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_documents(self) -> List[Dict]:
        """Load all documents from all source files (.jsonl and .txt)."""
        documents = []
        
        for file in sorted(self.corpus_dir.glob('*')):
            if not file.is_file():
                continue
                
            if file.suffix == '.jsonl':
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                doc = json.loads(line)
                                if isinstance(doc, dict):
                                    doc.setdefault('source_file', file.name)
                                    documents.append(doc)
                            except json.JSONDecodeError:
                                pass
            elif file.suffix == '.txt':
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if "DOCUMENT" in content:
                        raw_docs = content.split("---")
                        for idx, raw in enumerate(raw_docs):
                            raw = raw.strip()
                            if not raw:
                                continue
                            title_m = re.search(r"TITLE:\s*([^\n]+)", raw)
                            text_m = re.search(r"(?:ABSTRACT|TEXT):\s*([\s\S]+)$", raw)
                            title = title_m.group(1).strip() if title_m else ""
                            body = text_m.group(1).strip() if text_m else raw
                            documents.append({
                                'id': f"{file.stem}_{idx}",
                                'source': file.stem,
                                'source_file': file.name,
                                'title': title,
                                'content': body
                            })
                    else:
                        for idx, line in enumerate(content.splitlines()):
                            line = line.strip()
                            if line:
                                documents.append({
                                    'id': f"{file.stem}_{idx}",
                                    'source': file.stem,
                                    'source_file': file.name,
                                    'title': '',
                                    'content': line
                                })
                except Exception as e:
                    print(f"[WARN] Failed to read {file.name}: {e}")
        
        return documents
    
    def get_word_frequency(self) -> defaultdict:
        """Get word frequency across corpus."""
        freq = defaultdict(int)
        
        for doc in self.load_all_documents():
            content = (doc.get('title', '') + ' ' + doc.get('content', '')).lower()
            tokens = re.findall(r"\b[a-zA-Z0-9_\-]+\b", content)
            for token in tokens:
                if len(token) > 1:
                    freq[token] += 1
        
        return freq
    
    def get_source_stats(self) -> Dict[str, int]:
        """Get statistics about corpus documents by source file."""
        stats = defaultdict(int)
        
        for file in sorted(self.corpus_dir.glob('*')):
            if not file.is_file():
                continue
            
            if file.suffix == '.jsonl':
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        count = sum(1 for line in f if line.strip())
                    stats[file.name] = count
                except Exception:
                    pass
            elif file.suffix == '.txt':
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        txt = f.read()
                    if "DOCUMENT" in txt:
                        count = len(re.findall(r"^DOCUMENT\b", txt, re.MULTILINE))
                        if count == 0:
                            count = len([d for d in txt.split("---") if d.strip()])
                    else:
                        count = sum(1 for l in txt.splitlines() if l.strip())
                    stats[file.name] = count
                except Exception:
                    pass
                    
        return dict(stats)
    
    def get_total_docs(self) -> int:
        """Get total document count across all sources."""
        stats = self.get_source_stats()
        return sum(stats.values())
    
    def export_corpus_text(self, output_path: Path):
        """Export corpus as plain text (one document per line with normalized whitespace)."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        docs = self.load_all_documents()
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in docs:
                content = (doc.get('title', '') + ' ' + doc.get('content', '')).strip()
                # Normalize all newlines and whitespace to single spaces so it is 1 doc per line
                clean_line = ' '.join(content.split())
                if clean_line:
                    f.write(clean_line + '\n')
        
        print(f"[INFO] Exported {len(docs)} documents to {output_path}")


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    builder = CorpusBuilder(base_dir / 'corpus' / 'built')
    
    stats = builder.get_source_stats()
    total = builder.get_total_docs()
    
    print(f"[STATS] Corpus: {total} documents across {len(stats)} files")
    for source, count in sorted(stats.items(), key=lambda x: -x[1])[:10]:
        print(f"  {source}: {count}")
    if len(stats) > 10:
        print(f"  ... and {len(stats) - 10} more files")
    
    export_target = base_dir / 'corpus' / 'corpus.txt'
    builder.export_corpus_text(export_target)
