"""
Delta-Detection Anomaly Scorer — Will Breaker Prototype Phase 1
Modeled on Clif High's Web Bot methodology (research 007)

Core insight: anomaly = |actual_context - expected_context| × emotional_weight × log(1/frequency)
"""

import math
import csv
import re
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def tokenize(text):
    """Clean tokenization: lowercased alphanumeric words without punctuation."""
    if isinstance(text, list):
        text = " ".join(text)
    return re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())


class EmotionalLexicon:
    """Load and query emotional lexicons (NRC + VADER + Will Breaker weights)."""
    
    def __init__(self, nrc_path, vader_path, custom_weights_path=None):
        self.nrc = {}
        self.vader = {}
        self.custom_weights = {}
        if nrc_path and Path(nrc_path).exists():
            self._load_nrc(nrc_path)
        if vader_path and Path(vader_path).exists():
            self._load_vader(vader_path)
        if custom_weights_path and Path(custom_weights_path).exists():
            self._load_custom_weights(custom_weights_path)
    
    def _load_nrc(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['word'].strip().lower()
                self.nrc[word] = {
                    'joy': float(row.get('joy', 0)),
                    'trust': float(row.get('trust', 0)),
                    'fear': float(row.get('fear', 0)),
                    'surprise': float(row.get('surprise', 0)),
                    'sadness': float(row.get('sadness', 0)),
                    'disgust': float(row.get('disgust', 0)),
                    'anger': float(row.get('anger', 0)),
                    'anticipation': float(row.get('anticipation', 0))
                }
    
    def _load_vader(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['word'].strip().lower()
                self.vader[word] = {
                    'positive': float(row.get('positive', 0)),
                    'negative': float(row.get('negative', 0)),
                    'neutral': float(row.get('neutral', 0)),
                    'compound': float(row.get('compound', 0))
                }
    
    def _load_custom_weights(self, path):
        path = Path(path)
        try:
            if yaml and path.suffix in ('.yaml', '.yml'):
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        weights = data.get('will_breaker_weights', data)
                        for k, v in weights.items():
                            if isinstance(v, (int, float)):
                                self.custom_weights[k.strip().lower()] = float(v)
            elif path.suffix == '.csv':
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        word = row.get('word', '').strip().lower()
                        weight = float(row.get('weight', 1.0))
                        if word:
                            self.custom_weights[word] = weight
        except Exception as e:
            print(f"[WARN] Failed to load custom weights from {path}: {e}")
    
    def get_emotional_weight(self, word):
        """Compute composite emotional weight for a word."""
        word = word.strip().lower()
        
        nrc_weight = 0.0
        vader_weight = 0.0
        
        if word in self.nrc:
            emotions = self.nrc[word]
            nrc_weight = sum(emotions.values()) / max(len(emotions), 1)
        
        if word in self.vader:
            vader_scores = self.vader[word]
            vader_weight = abs(vader_scores['compound'])
        
        # Base weight: weighted average of NRC and VADER, with baseline default
        base_weight = 0.6 * nrc_weight + 0.4 * vader_weight
        if base_weight == 0.0:
            base_weight = 0.15  # Non-zero default for neutral/unknown words
        
        # Custom domain weight multiplier if defined
        if word in self.custom_weights:
            custom_mult = self.custom_weights[word]
            return base_weight * custom_mult
        
        return base_weight
    
    def get_emotion_profile(self, word):
        """Get full emotion profile for a word."""
        word = word.strip().lower()
        profile = {}
        if word in self.nrc:
            profile.update(self.nrc[word])
        if word in self.vader:
            profile['valence'] = self.vader[word]['compound']
        if word in self.custom_weights:
            profile['custom_weight'] = self.custom_weights[word]
        return profile


class BaselineContextModel:
    """Build baseline context model from corpus."""
    
    def __init__(self):
        # word -> context_word -> co-occurrence count
        self.word_context = defaultdict(lambda: defaultdict(int))
        self.word_frequency = defaultdict(int)
        self.total_words = 0
    
    def add_document(self, tokens):
        """Add tokens from a document to the baseline model."""
        if isinstance(tokens, str):
            tokens = tokenize(tokens)
        else:
            tokens = [t.lower() for t in tokens if t]
            
        for i, token in enumerate(tokens):
            self.word_frequency[token] += 1
            self.total_words += 1
            
            # Co-occurring words within window of 5 (excluding target token itself)
            start = max(0, i - 5)
            end = min(len(tokens), i + 6)
            for j in range(start, end):
                if j != i:
                    ctx_word = tokens[j]
                    self.word_context[token][ctx_word] += 1
    
    def get_expected_context(self, word):
        """Get expected context distribution for a word."""
        word = word.strip().lower()
        contexts = self.word_context.get(word, {})
        if not contexts:
            return None
        
        total = sum(contexts.values())
        if total == 0:
            return None
        return {ctx: count / total for ctx, count in contexts.items()}
    
    def get_document_frequency(self, word):
        """Get document frequency for a word."""
        return self.word_frequency.get(word.strip().lower(), 0) / max(self.total_words, 1)


class AnomalyScorer:
    """Score anomaly for words in documents."""
    
    def __init__(self, lexicon, baseline_model):
        self.lexicon = lexicon
        self.baseline = baseline_model
    
    def score_word(self, word, document_tokens):
        """Score anomaly for a single word in a document."""
        word = word.strip().lower()
        doc_freq = self.baseline.get_document_frequency(word)
        emotional_weight = self.lexicon.get_emotional_weight(word)
        inverse_freq = math.log(1 / max(doc_freq, 0.0001))
        
        # Get expected context
        expected = self.baseline.get_expected_context(word)
        if not expected:
            # No baseline data — use baseline context delta with frequency anomaly
            return self._frequency_anomaly(word, doc_freq)
        
        # Get actual context in document
        actual = self._compute_actual_context(word, document_tokens)
        
        # Compute context delta (Total Variation Distance: 0.0 to 1.0)
        context_delta = self._compute_context_delta(expected, actual)
        
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
        """Compute actual co-occurring context distribution for a word in tokens."""
        word = word.strip().lower()
        contexts = defaultdict(int)
        
        for i, token in enumerate(tokens):
            if token == word:
                start = max(0, i - 5)
                end = min(len(tokens), i + 6)
                for j in range(start, end):
                    if j != i:
                        contexts[tokens[j]] += 1
        
        total = sum(contexts.values())
        if total == 0:
            return {}
        
        return {ctx: count / total for ctx, count in contexts.items()}
    
    def _compute_context_delta(self, expected, actual):
        """Compute delta (Total Variation Distance) between expected and actual context."""
        if not expected or not actual:
            return 0.5
        all_contexts = set(expected.keys()) | set(actual.keys())
        if not all_contexts:
            return 0.0
        
        # Total variation distance: 0.5 * sum(|P(x) - Q(x)|) -> bounded in [0.0, 1.0]
        tv_dist = 0.5 * sum(abs(expected.get(ctx, 0.0) - actual.get(ctx, 0.0)) for ctx in all_contexts)
        return tv_dist
    
    def _frequency_anomaly(self, word, doc_freq):
        """Frequency-based anomaly when no baseline context is available."""
        inverse_freq = math.log(1 / max(doc_freq, 0.0001))
        emotional_weight = self.lexicon.get_emotional_weight(word)
        context_delta = 0.5  # Neutral default for unseen words
        anomaly = context_delta * emotional_weight * inverse_freq
        return {
            'word': word,
            'anomaly': anomaly,
            'context_delta': context_delta,
            'emotional_weight': emotional_weight,
            'inverse_frequency': inverse_freq,
            'document_frequency': doc_freq
        }
    
    def score_document(self, tokens, threshold=1.0):
        """Score entire document, return unique flagged words sorted by anomaly."""
        if isinstance(tokens, str):
            token_list = tokenize(tokens)
        else:
            token_list = [t.lower() for t in tokens if t]
        
        flagged = []
        unique_words = sorted(set(w for w in token_list if len(w) > 2))
        
        for word in unique_words:
            score = self.score_word(word, token_list)
            if score['anomaly'] > threshold:
                flagged.append(score)
        
        flagged.sort(key=lambda x: -x['anomaly'])
        return flagged
    
    def track_delta(self, flagged_words_t1, flagged_words_t2, time_delta_hours):
        """Track delta between two time points."""
        delta_results = []
        effective_hours = time_delta_hours if time_delta_hours and time_delta_hours > 0 else 1.0
        
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
                    'delta_rate': anomaly_delta / effective_hours
                })
        
        return delta_results


def load_lexicons(nrc_path, vader_path, custom_weights_path=None):
    """Load emotional lexicons and custom weights."""
    return EmotionalLexicon(nrc_path, vader_path, custom_weights_path)


def build_baseline(corpus_paths):
    """Build baseline context model from corpus."""
    model = BaselineContextModel()
    
    for path in corpus_paths:
        path = Path(path)
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                tokens = tokenize(line)
                if tokens:
                    model.add_document(tokens)
    
    return model


def score_document(document_text, lexicon, baseline, threshold=1.0):
    """Score a document for anomalies."""
    scorer = AnomalyScorer(lexicon, baseline)
    return scorer.score_document(document_text, threshold)


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    lexicon = load_lexicons(
        base_dir / 'lexicon' / 'nrc_emotion_lexicon.csv',
        base_dir / 'lexicon' / 'vader_lexicon.csv',
        base_dir / 'config' / 'lexicon_weights.yaml'
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
    baseline.add_document(tokenize(sample_text))
    
    scorer = AnomalyScorer(lexicon, baseline)
    
    # Test on test document with known and unseen words
    test_text = "Ejecta detected near coastline with unmanifest blondes on boats and unexpected clickout phenomenon."
    flagged = scorer.score_document(test_text, threshold=0.5)
    
    print(f"Flagged anomalies ({len(flagged)}):")
    for f in flagged:
        print(f"  {f['word']}: anomaly={f['anomaly']:.3f}, "
              f"delta={f['context_delta']:.3f}, "
              f"emotional={f['emotional_weight']:.3f}, "
              f"freq={f['document_frequency']:.6f}")
