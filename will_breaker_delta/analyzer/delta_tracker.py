"""
Delta Tracker — Will Breaker Delta-Detection Phase 2
Tracks delta in flagged words over time.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional


class DeltaTracker:
    """Track delta in flagged words over time."""
    
    def __init__(self, corpus_dir: Path = None):
        self.corpus_dir = Path(corpus_dir) if corpus_dir else None
        self.word_history = defaultdict(list)  # word -> [{'timestamp': ..., 'anomaly': ..., 'source': ...}]
    
    def add_flagged_words(self, flagged_words: List[Dict], timestamp: datetime = None, source: str = 'unknown'):
        """Add flagged words to history."""
        if timestamp is None:
            timestamp = datetime.now()
        ts_str = timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp)
        
        for word_info in flagged_words:
            word = word_info['word'].strip().lower()
            anomaly = float(word_info.get('anomaly', 0.0))
            doc_source = word_info.get('source', source)
            
            self.word_history[word].append({
                'timestamp': ts_str,
                'anomaly': anomaly,
                'source': doc_source,
                'document_frequency': float(word_info.get('document_frequency', 0.0))
            })
    
    def compute_delta(self, word: str, window_hours: Optional[int] = None) -> Optional[Dict]:
        """Compute delta for a word within time window (relative to latest observation)."""
        word = word.strip().lower()
        history = self.word_history.get(word, [])
        
        if len(history) < 2:
            return None
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        # Filter to window if requested
        if window_hours is not None and history:
            try:
                latest_time = max(datetime.fromisoformat(h['timestamp']) for h in history)
                cutoff = latest_time - timedelta(hours=window_hours)
                recent = [h for h in history if datetime.fromisoformat(h['timestamp']) >= cutoff]
            except Exception:
                recent = history
        else:
            recent = history
        
        if len(recent) < 2:
            return None
        
        first = recent[0]
        last = recent[-1]
        
        anomaly_delta = last['anomaly'] - first['anomaly']
        try:
            t0 = datetime.fromisoformat(first['timestamp'])
            t1 = datetime.fromisoformat(last['timestamp'])
            time_delta_hours = (t1 - t0).total_seconds() / 3600.0
        except Exception:
            time_delta_hours = 1.0
            
        effective_hours = time_delta_hours if time_delta_hours > 0 else 1.0
        delta_rate = anomaly_delta / effective_hours
        
        return {
            'word': word,
            'anomaly_delta': anomaly_delta,
            'time_delta_hours': time_delta_hours,
            'delta_rate': delta_rate,
            'first_anomaly': first['anomaly'],
            'last_anomaly': last['anomaly'],
            'observations': len(recent),
            'timestamp': last['timestamp'],
            'source': last.get('source', 'unknown')
        }
    
    def get_precursor_events(self, threshold: float = 0.5, min_observations: int = 2, window_hours: Optional[int] = None) -> List[Dict]:
        """Get precursor events (words with significant delta)."""
        events = []
        
        for word in self.word_history:
            delta = self.compute_delta(word, window_hours=window_hours)
            
            if delta and abs(delta['anomaly_delta']) >= threshold and delta['observations'] >= min_observations:
                events.append(delta)
        
        # Sort by absolute delta rate (most significant first)
        events.sort(key=lambda x: -abs(x['delta_rate']))
        
        return events
    
    def generate_forecast(self, precursor_events: List[Dict], forecast_horizon_hours: int = 168) -> List[Dict]:
        """Generate forecasts based on delta trajectories."""
        forecasts = []
        
        for event in precursor_events:
            word = event['word']
            rate = event['delta_rate']
            
            # Project forward (lower-bounded at 0.0)
            projected_anomaly = max(0.0, event['last_anomaly'] + rate * forecast_horizon_hours)
            
            forecasts.append({
                'word': word,
                'current_anomaly': event['last_anomaly'],
                'projected_anomaly': projected_anomaly,
                'delta_rate': rate,
                'forecast_horizon_hours': forecast_horizon_hours,
                'timestamp': event.get('timestamp', datetime.now().isoformat()),
                'confidence': 'low' if event['observations'] < 3 else 'medium' if event['observations'] < 6 else 'high'
            })
        
        return forecasts
    
    def export_history(self, output_path: Path):
        """Export word history to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        export_data = {}
        
        for word, history in self.word_history.items():
            export_data[word] = sorted(history, key=lambda x: x['timestamp'])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"[INFO] Exported history for {len(export_data)} words to {output_path}")
    
    def import_history(self, input_path: Path):
        """Import word history from JSON."""
        input_path = Path(input_path)
        if not input_path.exists():
            print(f"[WARN] History file not found: {input_path}")
            return
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for word, history in data.items():
                self.word_history[word.strip().lower()].extend(history)
        print(f"[INFO] Imported history for {len(data)} words from {input_path}")


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    tracker = DeltaTracker(base_dir / 'corpus' / 'built')
    
    # Example: simulate historical timestamps
    t0 = datetime.now() - timedelta(hours=48)
    t1 = datetime.now() - timedelta(hours=24)
    t2 = datetime.now()
    
    tracker.add_flagged_words([
        {'word': 'ejecta', 'anomaly': 2.1, 'source': 'session-007'},
        {'word': 'clickout', 'anomaly': 1.8, 'source': 'session-007'},
    ], timestamp=t0)
    
    tracker.add_flagged_words([
        {'word': 'ejecta', 'anomaly': 3.5, 'source': 'session-012'},
        {'word': 'clickout', 'anomaly': 2.4, 'source': 'session-012'},
    ], timestamp=t1)
    
    tracker.add_flagged_words([
        {'word': 'ejecta', 'anomaly': 4.7, 'source': 'session-018'},
        {'word': 'clickout', 'anomaly': 3.2, 'source': 'session-018'},
    ], timestamp=t2)
    
    events = tracker.get_precursor_events(threshold=0.5, min_observations=2)
    
    print(f"[PRECURSOR EVENTS]: {len(events)} events found")
    for event in events:
        print(f"  {event['word']}: delta={event['anomaly_delta']:.3f}, rate={event['delta_rate']:.3f}/hr, obs={event['observations']}")
