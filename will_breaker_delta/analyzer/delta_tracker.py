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
    
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        self.word_history = defaultdict(list)  # word -> [(timestamp, anomaly_score)]
    
    def add_flagged_words(self, flagged_words: List[Dict], timestamp: datetime = None):
        """Add flagged words to history."""
        if timestamp is None:
            timestamp = datetime.now()
        
        for word_info in flagged_words:
            word = word_info['word']
            anomaly = word_info['anomaly']
            
            self.word_history[word].append({
                'timestamp': timestamp.isoformat(),
                'anomaly': anomaly,
                'source': word_info.get('source', 'unknown')
            })
    
    def compute_delta(self, word: str, window_hours: int = 24) -> Optional[Dict]:
        """Compute delta for a word within time window."""
        history = self.word_history.get(word, [])
        
        if len(history) < 2:
            return None
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        # Filter to window
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent = [h for h in history if datetime.fromisoformat(h['timestamp']) >= cutoff]
        
        if len(recent) < 2:
            return None
        
        # Compute delta
        first = recent[0]
        last = recent[-1]
        
        anomaly_delta = last['anomaly'] - first['anomaly']
        time_delta_hours = (datetime.fromisoformat(last['timestamp']) - datetime.fromisoformat(first['timestamp'])).total_seconds() / 3600
        
        return {
            'word': word,
            'anomaly_delta': anomaly_delta,
            'time_delta_hours': time_delta_hours,
            'delta_rate': anomaly_delta / max(time_delta_hours, 1),
            'first_anomaly': first['anomaly'],
            'last_anomaly': last['anomaly'],
            'observations': len(recent)
        }
    
    def get_precursor_events(self, threshold: float = 1.0, min_observations: int = 3) -> List[Dict]:
        """Get precursor events (words with significant delta)."""
        events = []
        
        for word in self.word_history:
            delta = self.compute_delta(word)
            
            if delta and abs(delta['anomaly_delta']) > threshold and delta['observations'] >= min_observations:
                events.append(delta)
        
        # Sort by delta rate (most significant first)
        events.sort(key=lambda x: -abs(x['delta_rate']))
        
        return events
    
    def generate_forecast(self, precursor_events: List[Dict], forecast_horizon_hours: int = 168) -> List[Dict]:
        """Generate forecasts based on delta trajectories."""
        forecasts = []
        
        for event in precursor_events:
            word = event['word']
            rate = event['delta_rate']
            
            # Project forward
            projected_anomaly = event['last_anomaly'] + rate * forecast_horizon_hours
            
            forecasts.append({
                'word': word,
                'current_anomaly': event['last_anomaly'],
                'projected_anomaly': projected_anomaly,
                'forecast_horizon_hours': forecast_horizon_hours,
                'confidence': 'low' if event['observations'] < 5 else 'medium' if event['observations'] < 10 else 'high'
            })
        
        return forecasts
    
    def export_history(self, output_path: Path):
        """Export word history to JSON."""
        export_data = {}
        
        for word, history in self.word_history.items():
            export_data[word] = sorted(history, key=lambda x: x['timestamp'])
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"[INFO] Exported history to {output_path}")


if __name__ == '__main__':
    tracker = DeltaTracker(Path(__file__).parent.parent / 'corpus' / 'built')
    
    # Example: load some flagged words (from anomaly_scorer output)
    # tracker.add_flagged_words([{'word': 'ejecta', 'anomaly': 4.7, 'source': 'reddit'}])
    
    events = tracker.get_precursor_events(threshold=1.0, min_observations=2)
    
    print(f"[PRECORSOR EVENTS]: {len(events)} events found")
    for event in events[:10]:
        print(f"  {event['word']}: delta={event['anomaly_delta']:.3f}, rate={event['delta_rate']:.3f}/hr")
