"""
Corpus Builder — Will Breaker Delta-Detection Phase 2
Aggregates documents from all sources into unified corpus.
"""

import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


class CorpusBuilder:
    """Build and manage the delta-detection corpus."""
    
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_documents(self) -> List[Dict]:
        """Load all documents from all source files."""
        documents = []
        
        for file in self.corpus_dir.glob('*.jsonl'):
            with open(file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            doc = json.loads(line.strip())
                            documents.append(doc)
                        except json.JSONDecodeError:
                            print(f"[WARN] Invalid JSON in {file.name}")
        
        return documents
    
    def get_word_frequency(self) -> defaultdict:
        """Get word frequency across corpus."""
        freq = defaultdict(int)
        
        for doc in self.load_all_documents():
            content = doc.get('content', '') + ' ' + doc.get('title', '')
            tokens = content.lower().split()
            
            for token in tokens:
                # Simple tokenization — strip punctuation
                token = ''.join(c for c in token if c.isalnum())
                if token:
                    freq[token] += 1
        
        return freq
    
    def get_source_stats(self) -> Dict:
        """Get statistics about corpus by source."""
        stats = defaultdict(int)
        
        for file in self.corpus_dir.glob('*.jsonl'):
            count = sum(1 for _ in open(file))
            stats[file.stem] = count
        
        return dict(stats)
    
    def get_total_docs(self) -> int:
        """Get total document count."""
        return sum(1 for _ in self.corpus_dir.glob('*.jsonl')) if any(self.corpus_dir.glob('*.jsonl')) else 0
    
    def export_corpus_text(self, output_path: Path):
        """Export corpus as plain text (one document per line)."""
        with open(output_path, 'w') as f:
            for doc in self.load_all_documents():
                content = doc.get('content', '') + ' ' + doc.get('title', '')
                f.write(content + '\n')
        
        print(f"[INFO] Exported corpus to {output_path}")


if __name__ == '__main__':
    builder = CorpusBuilder(Path(__file__).parent.parent / 'corpus' / 'built')
    
    # Get stats
    stats = builder.get_source_stats()
    total = builder.get_total_docs()
    
    print(f"[STATS] Corpus: {total} documents")
    for source, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")
    
    # Export for baseline model building
    builder.export_corpus_text(Path(__file__).parent.parent / 'corpus' / 'corpus.txt')
    print(f"\n[INFO] Corpus exported to corpus/corpus.txt")
