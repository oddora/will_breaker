"""
Delta-Detection Anomaly Scorer — Will Breaker Prototype Phase 1
Modeled on Clif High's Web Bot methodology (research 007)

Core insight: anomaly = |actual_context - expected_context| × emotional_weight × log(1/frequency)
"""

import math
import csv
from collections import defaultdict
from pathlib import Path


class EmotionalLexicon:
    """Load and query emotional lexicons (NRC + VADER)."""
    
    def __init__(self, nrc_path, vader_path):
        self.nrc = {}
        self.vader = {}
        self._load_nrc(nrc_path)
        self._load_vader(vader_path)
    
    def _load_nrc(self, path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['word'].lower()
                self.nrc[word] = {
                    'joy': float(row['joy']),
                    'trust': float(row['trust']),
                    'fear': float(row['fear']),
                    'surprise': float(row['surprise']),
                    'sadness': float(row['sadness']),
                    'disgust': float(row['disgust']),
                    'anger': float(row['anger']),
                    'anticipation': float(row['anticipation'])
                }
    
    def _load_vader(self, path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['word'].lower()
                self.vader[word] = {
                    'positive': float(row['positive']),
                    'negative': float(row['negative']),
                    'neutral': float(row['neutral']),
                    'compound': float(row['compound'])
                }
    
    def get_emotional_weight(self, word):
        """Compute composite emotional weight for a word."""
        word = word.lower()
        
        nrc_weight = 0
        vader_weight = 0
        
        if word in self.nrc:
            emotions = self.nrc[word]
            # High-emotion words get higher weight
            nrc_weight = sum(emotions.values()) / len(emotions)
        
        if word in self.vader:
            vader_scores = self.vader[word]
            # Compound score indicates emotional intensity
            vader_weight = abs(vader_scores['compound'])
        
        # Composite: weighted average of NRC and VADER
        return 0.6 * nrc_weight + 0.4 * vader_weight
    
    def get_emotion_profile(self, word):
        """Get full emotion profile for a word."""
        word = word.lower()
        profile = {}
        if word in self.nrc:
            profile.update(self.nrc[word])
        if word in self.vader:
            profile['valence'] = self.vader[word]['compound']
        return profile


class BaselineContextModel:
    """Build baseline context model from corpus."""
    
    def __init__(self):
        self.word_context = defaultdict(lambda: defaultdict(int))
        self.word_frequency = defaultdict(int)
        self.total_words = 0
    
    def add_document(self, tokens):
        """Add tokens from a document to the baseline model."""
        for i, token in enumerate(tokens):
            token = token.lower()
            self.word_frequency[token] += 1
            self.total_words += 1
            
            # Context = surrounding tokens (window of 5)
            context_window = tokens[max(0, i-5):min(len(tokens), i+6)]
            context = tuple(context_window)
            self.word_context[token][context] += 1
    
    def get_expected_context(self, word):
        """Get expected context distribution for a word."""
        word = word.lower()
        contexts = self.word_context.get(word, {})
        if not contexts:
            return None
        
        total = sum(contexts.values())
        return {ctx: count / total for ctx, count in contexts.items()}
    
    def get_document_frequency(self, word):
        """Get document frequency for a word."""
        return self.word_frequency.get(word.lower(), 0) / max(self.total_words, 1)


class AnomalyScorer:
    """Score anomaly for words in documents."""
    
    def __init__(self, lexicon, baseline_model):
        self.lexicon = lexicon
        self.baseline = baseline_model
    
    def score_word(self, word, document_tokens):
        """Score anomaly for a single word in a document."""
        word = word.lower()
        
        # Get expected context
        expected = self.baseline.get_expected_context(word)
        if not expected:
            # No baseline data — use simple frequency-based anomaly
            doc_freq = self.baseline.get_document_frequency(word)
            return self._frequency_anomaly(word, doc_freq)
        
        # Get actual context in document
        actual = self._compute_actual_context(word, document_tokens)
        
        # Compute context delta
        context_delta = self._compute_context_delta(expected, actual)
        
        # Get emotional weight
        emotional_weight = self.lexicon.get_emotional_weight(word)
        
        # Get inverse frequency
        doc_freq = self.baseline.get_document_frequency(word)
        inverse_freq = math.log(1 / max(doc_freq, 0.0001))
        
        # Final anomaly score
        anomaly = context_delta * emotional_weight * inverse_freq
        
        return {
            'word': word,
            'anomaly': anomaly,
            'context_delta': context_delta,
            'emotional_weight': emotional_weight,
            'inverse_frequency': inverse_freq,
            'document_frequency': doc_freq
        }
    
    def _compute_actual_context(self, word, tokens):
        """Compute actual context distribution for a word in tokens."""
        word = word.lower()
        contexts = defaultdict(int)
        
        for i, token in enumerate(tokens):
            if token.lower() == word:
                window = tokens[max(0, i-5):min(len(tokens), i+6)]
                contexts[tuple(window)] += 1
        
        total = sum(contexts.values())
        if total == 0:
            return {}
        
        return {ctx: count / total for ctx, count in contexts.items()}
    
    def _compute_context_delta(self, expected, actual):
        """Compute delta between expected and actual context."""
        delta = 0
        all_contexts = set(expected.keys()) | set(actual.keys())
        
        for ctx in all_contexts:
            exp_prob = expected.get(ctx, 0)
            act_prob = actual.get(ctx, 0)
            delta += abs(exp_prob - act_prob)
        
        return delta / len(all_contexts) if all_contexts else 0
    
    def _frequency_anomaly(self, word, doc_freq):
        """Simple frequency-based anomaly (no baseline data)."""
        inverse_freq = math.log(1 / max(doc_freq, 0.0001))
        emotional_weight = self.lexicon.get_emotional_weight(word)
        return inverse_freq * emotional_weight * 0.5  # 0.5 = baseline multiplier
    
    def score_document(self, tokens, threshold=1.0):
        """Score entire document, return flagged words."""
        flagged = []
        
        for token in tokens:
            score = self.score_word(token, tokens)
            if score['anomaly'] > threshold:
                flagged.append(score)
        
        return flagged
    
    def track_delta(self, flagged_words_t1, flagged_words_t2, time_delta_hours):
        """Track delta between two time points."""
        delta_results = []
        
        for word1 in flagged_words_t1:
            word = word1['word']
            # Find matching word in t2
            word2 = next((w for w in flagged_words_t2 if w['word'] == word), None)
            
            if word2:
                anomaly_delta = word2['anomaly'] - word1['anomaly']
                freq_delta = word2['document_frequency'] - word1['document_frequency']
                
                delta_results.append({
                    'word': word,
                    'anomaly_delta': anomaly_delta,
                    'frequency_delta': freq_delta,
                    'time_delta_hours': time_delta_hours,
                    'delta_rate': anomaly_delta / max(time_delta_hours, 1)
                })
        
        return delta_results


def load_lexicons(nrc_path, vader_path):
    """Load emotional lexicons."""
    lexicon = EmotionalLexicon(nrc_path, vader_path)
    return lexicon


def build_baseline(corpus_paths):
    """Build baseline context model from corpus."""
    model = BaselineContextModel()
    
    for path in corpus_paths:
        with open(path, 'r') as f:
            for line in f:
                tokens = line.strip().split()
                model.add_document(tokens)
    
    return model


def score_document(document_text, lexicon, baseline, threshold=1.0):
    """Score a document for anomalies."""
    scorer = AnomalyScorer(lexicon, baseline)
    tokens = document_text.strip().split()
    return scorer.score_document(tokens, threshold)


if __name__ == '__main__':
    # Test on sample text
    lexicon = load_lexicons(
        Path(__file__).parent.parent / 'lexicon' / 'nrc_emotion_lexicon.csv',
        Path(__file__).parent.parent / 'lexicon' / 'vader_lexicon.csv'
    )
    
    baseline = BaselineContextModel()
    # Add sample corpus
    sample_text = """
    The template layer of information exists prior to manifestation.
    Consciousness transcends spacetime through coherent brainwave states.
    The planck distance represents the threshold between time-space and non-time-space.
    Ejecta was detected off the coast, suggesting sudden disruption.
    Blondes on boats incident confirmed the precursor anomaly.
    """
    baseline.add_document(sample_text.strip().split())
    
    scorer = AnomalyScorer(lexicon, baseline)
    flagged = scorer.score_document(sample_text.strip().split(), threshold=0.5)
    
    print("Flagged anomalies:")
    for f in flagged:
        print(f"  {f['word']}: anomaly={f['anomaly']:.3f}, "
              f"delta={f['context_delta']:.3f}, "
              f"emotional={f['emotional_weight']:.3f}, "
              f"freq={f['document_frequency']:.6f}")
