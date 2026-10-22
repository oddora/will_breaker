"""
Context Model Builder — Will Breaker Delta-Detection Phase 2
Builds baseline context model from corpus for anomaly scoring.
"""

import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class ContextModel:
    """Build and query baseline context model."""
    
    def __init__(self, corpus_path: Path = None):
        self.word_context = defaultdict(lambda: defaultdict(int))
        self.word_frequency = defaultdict(int)
        self.total_words = 0
        self.corpus_path = corpus_path
        
        if corpus_path and corpus_path.exists():
            self.build_from_corpus(corpus_path)
    
    def build_from_corpus(self, corpus_path: Path):
        """Build context model from corpus text file."""
        with open(corpus_path, 'r') as f:
            for line in f:
                tokens = line.strip().split()
                self.add_document(tokens)
        
        print(f"[INFO] Built context model from {corpus_path}: {self.total_words} words")
    
    def add_document(self, tokens: List[str]):
        """Add tokens from a document to the model."""
        for i, token in enumerate(tokens):
            token = token.lower()
            self.word_frequency[token] += 1
            self.total_words += 1
            
            # Context = surrounding tokens (window of 5)
            context_window = tokens[max(0, i-5):min(len(tokens), i+6)]
            context = tuple(context_window)
            self.word_context[token][context] += 1
    
    def get_expected_context(self, word: str) -> Dict[Tuple, float]:
        """Get expected context distribution for a word."""
        word = word.lower()
        contexts = self.word_context.get(word, {})
        
        if not contexts:
            return {}
        
        total = sum(contexts.values())
        return {ctx: count / total for ctx, count in contexts.items()}
    
    def get_document_frequency(self, word: str) -> float:
        """Get document frequency for a word."""
        return self.word_frequency.get(word.lower(), 0) / max(self.total_words, 1)
    
    def get_top_words(self, n: int = 100) -> List[Tuple[str, int]]:
        """Get top N most frequent words."""
        return sorted(self.word_frequency.items(), key=lambda x: -x[1])[:n]
    
    def get_word_entropy(self, word: str) -> float:
        """Get entropy of word's context distribution (measure of specificity)."""
        word = word.lower()
        contexts = self.word_context.get(word, {})
        
        if not contexts:
            return 0
        
        total = sum(contexts.values())
        entropy = 0
        
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
    model = ContextModel(Path(__file__).parent.parent / 'corpus' / 'corpus.txt')
    
    stats = model.get_model_stats()
    print(f"[STATS] Model: {stats['total_words']} words, {stats['unique_words']} unique")
    
    top_words = model.get_top_words(20)
    print(f"\n[TOP WORDS]:")
    for word, freq in top_words:
        print(f"  {word}: {freq}")
