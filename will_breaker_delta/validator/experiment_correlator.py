"""
Experiment Correlator — Will Breaker Delta-Detection Phase 2
Cross-references delta flags with Will Breaker shift reports.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict


class ExperimentCorrelator:
    """Cross-reference delta flags with shift reports."""
    
    def __init__(self, shift_report_dir: Path, delta_history_dir: Path):
        self.shift_report_dir = shift_report_dir
        self.delta_history_dir = delta_history_dir
    
    def load_shift_reports(self) -> List[Dict]:
        """Load all shift reports."""
        reports = []
        
        for file in self.shift_report_dir.glob('*.json'):
            with open(file, 'r') as f:
                reports.extend(json.load(f))
        
        return reports
    
    def load_delta_history(self) -> Dict:
        """Load delta history."""
        history_file = self.delta_history_dir / 'history.json'
        
        if not history_file.exists():
            return {}
        
        with open(history_file, 'r') as f:
            return json.load(f)
    
    def correlate(self, window_days: int = 7) -> List[Dict]:
        """Correlate delta flags with shift reports."""
        reports = self.load_shift_reports()
        history = self.load_delta_history()
        
        correlations = []
        
        for report in reports:
            report_time = datetime.fromisoformat(report.get('timestamp', report.get('date', '')))
            
            for word, events in history.items():
                for event in events:
                    event_time = datetime.fromisoformat(event['timestamp'])
                    time_diff = abs((report_time - event_time).total_seconds()) / 86400
                    
                    if time_diff <= window_days:
                        correlations.append({
                            'word': word,
                            'event_anomaly': event['anomaly'],
                            'report_id': report.get('id', 'unknown'),
                            'report_type': report.get('type', 'unknown'),
                            'time_diff_days': time_diff,
                            'correlation_type': 'preceding' if event_time < report_time else 'coincident'
                        })
        
        return correlations
    
    def compute_correlation_rate(self, correlations: List[Dict], threshold_days: int = 7) -> float:
        """Compute correlation rate (flags within threshold days of reports)."""
        if not correlations:
            return 0.0
        
        within_threshold = sum(1 for c in correlations if c['time_diff_days'] <= threshold_days)
        return within_threshold / len(correlations)
    
    def compute_archetype_correspondence(self, correlations: List[Dict]) -> Dict:
        """Compute archetype-category correspondence rate."""
        # This would need archetype mapping — placeholder
        return {
            'total_correlations': len(correlations),
            'with_archetype': sum(1 for c in correlations if c.get('archetype')),
            'correspondence_rate': 0.5  # Placeholder
        }
    
    def generate_report(self, correlations: List[Dict]) -> str:
        """Generate correlation report."""
        rate = self.compute_correlation_rate(correlations)
        archetype = self.compute_archetype_correspondence(correlations)
        
        report = []
        report.append("=" * 60)
        report.append("DELTA-SHIFT CORRELATION REPORT")
        report.append("=" * 60)
        report.append("")
        report.append(f"Total correlations: {len(correlations)}")
        report.append(f"Correlation rate: {rate:.1%}")
        report.append(f"Archetype correspondence: {archetype['correspondence_rate']:.1%}")
        report.append("")
        
        report.append("[TOP CORRELATIONS]:")
        for c in sorted(correlations, key=lambda x: x['time_diff_days'])[:10]:
            report.append(f"  {c['word']}: {c['time_diff_days']:.1f} days ({c['correlation_type']})")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


if __name__ == '__main__':
    correlator = ExperimentCorrelator(
        shift_report_dir=Path(__file__).parent.parent.parent / 'sessions',
        delta_history_dir=Path(__file__).parent.parent / 'corpus' / 'built'
    )
    
    correlations = correlator.correlate(window_days=7)
    report = correlator.generate_report(correlations)
    print(report)
