"""
Context Model Builder — Will Breaker Delta-Detection Phase 2
Builds baseline context model from corpus for anomaly scoring.
"""

import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def tokenize(text):
    """Clean tokenization: lowercased alphanumeric words without punctuation."""
    if isinstance(text, list):
        text = " ".join(text)
    return re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())


class ContextModel:
    """Build and query baseline context model."""
    
    def __init__(self, corpus_path: Path = None):
        self.word_context = defaultdict(lambda: defaultdict(int))
        self.word_frequency = defaultdict(int)
        self.total_words = 0
        self.corpus_path = corpus_path
        
        if corpus_path:
            corpus_path = Path(corpus_path)
            if corpus_path.is_file():
                self.build_from_file(corpus_path)
            elif corpus_path.is_dir():
                self.build_from_directory(corpus_path)
    
    def build_from_file(self, file_path: Path):
        """Build context model from text or jsonl file."""
        file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                tokens = tokenize(line)
                if tokens:
                    self.add_document(tokens)
        print(f"[INFO] Built context model from {file_path}: {self.total_words} words, {len(self.word_frequency)} unique")
    
    def build_from_directory(self, dir_path: Path):
        """Build context model from all files in a directory."""
        dir_path = Path(dir_path)
        count = 0
        for p in dir_path.glob('*'):
            if p.is_file() and p.suffix in ('.txt', '.jsonl', '.md'):
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        tokens = tokenize(line)
                        if tokens:
                            self.add_document(tokens)
                count += 1
        print(f"[INFO] Built context model from {count} files in {dir_path}: {self.total_words} words, {len(self.word_frequency)} unique")
    
    def add_document(self, tokens: List[str]):
        """Add tokens from a document to the model."""
        if isinstance(tokens, str):
            tokens = tokenize(tokens)
        else:
            tokens = [t.lower() for t in tokens if t]
            
        for i, token in enumerate(tokens):
            self.word_frequency[token] += 1
            self.total_words += 1
            
            # Co-occurring words within window of 5 (excluding target token)
            start = max(0, i - 5)
            end = min(len(tokens), i + 6)
            for j in range(start, end):
                if j != i:
                    ctx_word = tokens[j]
                    self.word_context[token][ctx_word] += 1
    
    def get_expected_context(self, word: str) -> Dict[str, float]:
        """Get expected context distribution for a word."""
        word = word.strip().lower()
        contexts = self.word_context.get(word, {})
        
        if not contexts:
            return {}
        
        total = sum(contexts.values())
        if total == 0:
            return {}
        return {ctx: count / total for ctx, count in contexts.items()}
    
    def get_document_frequency(self, word: str) -> float:
        """Get document frequency for a word."""
        return self.word_frequency.get(word.strip().lower(), 0) / max(self.total_words, 1)
    
    def get_top_words(self, n: int = 100) -> List[Tuple[str, int]]:
        """Get top N most frequent words."""
        return sorted(self.word_frequency.items(), key=lambda x: -x[1])[:n]
    
    def get_word_entropy(self, word: str) -> float:
        """Get entropy of word's context distribution (measure of specificity)."""
        word = word.strip().lower()
        contexts = self.word_context.get(word, {})
        
        if not contexts:
            return 0.0
        
        total = sum(contexts.values())
        entropy = 0.0
        
        for count in contexts.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the model."""
        return {
            'total_words': self.total_words,
            'unique_words': len(self.word_frequency),
            'avg_contexts_per_word': sum(len(c) for c in self.word_context.values()) / max(len(self.word_context), 1)
        }


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    corpus_file = base_dir / 'corpus' / 'corpus.txt'
    built_dir = base_dir / 'corpus' / 'built'
    
    target_path = corpus_file if corpus_file.exists() else built_dir
    model = ContextModel(target_path)
    
    stats = model.get_model_stats()
    print(f"[STATS] Model: {stats['total_words']} words, {stats['unique_words']} unique")
    
    top_words = model.get_top_words(15)
    print(f"\n[TOP WORDS]:")
    for word, freq in top_words:
        print(f"  {word}: {freq}")
