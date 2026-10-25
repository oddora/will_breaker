"""
Experiment Correlator — Will Breaker Delta-Detection Phase 2
Cross-references delta flags with Will Breaker shift reports and validates semantic overlap.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None

import sys
# Add parent dir to path so we can import neighboring modules if needed
sys.path.insert(0, str(Path(__file__).parent.parent))
from validator.shift_report_parser import ShiftReportParser
from analyzer.anomaly_scorer import AnomalyScorer, BaselineContextModel, load_lexicons, tokenize


class ExperimentCorrelator:
    """Cross-reference delta flags with shift reports and evaluate correlation."""
    
    def __init__(self, shift_report_dir: Path, delta_history_dir: Path):
        self.shift_report_dir = Path(shift_report_dir)
        self.delta_history_dir = Path(delta_history_dir)
    
    def load_shift_reports(self) -> List[Dict]:
        """Load flat list of all shift reports."""
        reports = []
        
        # 1. If path is a single json file
        if self.shift_report_dir.is_file() and self.shift_report_dir.suffix == '.json':
            try:
                with open(self.shift_report_dir, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if 'reports' in item and isinstance(item['reports'], list):
                                reports.extend(item['reports'])
                            else:
                                reports.append(item)
            except Exception as e:
                print(f"[WARN] Error reading {self.shift_report_dir}: {e}")
            return reports
        
        # 2. Check if shift_reports.json exists in corpus dir or shift_report_dir
        json_candidates = [
            self.shift_report_dir / 'shift_reports.json',
            self.shift_report_dir.parent / 'corpus' / 'shift_reports.json',
            self.delta_history_dir.parent / 'corpus' / 'shift_reports.json',
            self.delta_history_dir / 'shift_reports.json'
        ]
        for candidate in json_candidates:
            if candidate.exists() and candidate.is_file():
                try:
                    with open(candidate, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if 'reports' in item and isinstance(item['reports'], list):
                                    reports.extend(item['reports'])
                                else:
                                    reports.append(item)
                            if reports:
                                return reports
                except Exception:
                    pass
        
        # 3. If directory contains session markdown files, parse them directly
        if self.shift_report_dir.is_dir():
            parser = ShiftReportParser(self.shift_report_dir)
            reports = parser.get_flat_reports()
        
        return reports
    
    def load_delta_history(self) -> Dict:
        """Load delta word history."""
        candidates = [
            self.delta_history_dir / 'history.json',
            self.delta_history_dir / 'delta_history.json',
            self.delta_history_dir.parent / 'corpus' / 'delta_history.json'
        ]
        
        for cand in candidates:
            if cand.exists() and cand.is_file():
                try:
                    with open(cand, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    pass
        
        return {}
    
    def build_history_from_reports(self, reports: List[Dict], scorer: AnomalyScorer) -> Dict:
        """Build delta history on the fly by scoring reports."""
        history = defaultdict(list)
        
        for report in reports:
            text = report.get('content', '') + " " + report.get('phi_estimate', '')
            date_str = report.get('timestamp') or report.get('date') or datetime.now().strftime('%Y-%m-%d')
            flagged = scorer.score_document(text, threshold=0.8)
            
            for item in flagged:
                history[item['word']].append({
                    'timestamp': date_str,
                    'anomaly': item['anomaly'],
                    'source': report.get('session_log', report.get('id', 'unknown'))
                })
        
        return dict(history)
    
    def correlate(self, window_days: int = 7) -> List[Dict]:
        """Correlate temporal delta flags with shift reports."""
        reports = self.load_shift_reports()
        history = self.load_delta_history()
        
        # If no history file exists, synthesize from baseline and reports
        if not history and reports:
            base_dir = Path(__file__).parent.parent
            lex = load_lexicons(
                base_dir / 'lexicon' / 'nrc_emotion_lexicon.csv',
                base_dir / 'lexicon' / 'vader_lexicon.csv',
                base_dir / 'config' / 'lexicon_weights.yaml'
            )
            base_model = BaselineContextModel()
            for r in reports:
                base_model.add_document(tokenize(r.get('content', '')))
            scorer = AnomalyScorer(lex, base_model)
            history = self.build_history_from_reports(reports, scorer)
        
        correlations = []
        
        for report in reports:
            date_val = report.get('timestamp') or report.get('date')
            if not date_val:
                continue
            
            try:
                report_time = datetime.fromisoformat(str(date_val).split('T')[0])
            except Exception:
                continue
            
            for word, events in history.items():
                for event in events:
                    event_ts = event.get('timestamp')
                    if not event_ts:
                        continue
                    try:
                        event_time = datetime.fromisoformat(str(event_ts).split('T')[0])
                    except Exception:
                        continue
                    
                    time_diff = abs((report_time - event_time).total_seconds()) / 86400.0
                    
                    if time_diff <= window_days:
                        correlations.append({
                            'word': word,
                            'event_anomaly': event.get('anomaly', 0.0),
                            'report_id': report.get('id', report.get('session_log', 'unknown')),
                            'report_type': report.get('state_vector', 'state_vector'),
                            'phi_estimate': report.get('phi_estimate', 'unknown'),
                            'time_diff_days': time_diff,
                            'correlation_type': 'preceding' if event_time < report_time else 'coincident'
                        })
        
        return correlations
    
    def correlate_document_overlap(self, documents: List[Dict], scorer: AnomalyScorer, threshold: float = 0.8) -> Dict:
        """
        Compute document semantic overlap (Phase 2 validation methodology).
        Evaluates anomaly word sharing across document pairs.
        """
        doc_flags = []
        for doc in documents:
            title = doc.get('title', '')
            content = doc.get('content', '')
            full_text = f"{title}\n{content}"
            flagged = scorer.score_document(full_text, threshold=threshold)
            flagged_words = set(f['word'] for f in flagged)
            doc_flags.append({
                'title': title,
                'words': flagged_words
            })
        
        n_docs = len(doc_flags)
        if n_docs < 2:
            return {'total_pairs': 0, 'pairs_with_overlap': 0, 'correlation_percent': 0.0}
        
        total_pairs = (n_docs * (n_docs - 1)) // 2
        pairs_with_overlap = 0
        
        for i in range(n_docs):
            for j in range(i + 1, n_docs):
                overlap = doc_flags[i]['words'] & doc_flags[j]['words']
                if overlap:
                    pairs_with_overlap += 1
        
        correlation_percent = (pairs_with_overlap / total_pairs) * 100.0 if total_pairs > 0 else 0.0
        
        return {
            'docs_scored': n_docs,
            'total_pairs': total_pairs,
            'pairs_with_overlap': pairs_with_overlap,
            'correlation_percent': round(correlation_percent, 1),
            'target': 30.0,
            'verdict': 'PASS' if correlation_percent >= 30.0 else 'FAIL'
        }
    
    def compute_correlation_rate(self, correlations: List[Dict], threshold_days: int = 7) -> float:
        """Compute correlation rate."""
        if not correlations:
            return 0.0
        within_threshold = sum(1 for c in correlations if c['time_diff_days'] <= threshold_days)
        return within_threshold / len(correlations)
    
    def compute_archetype_correspondence(self, correlations: List[Dict]) -> Dict:
        """Compute correspondence between flagged words and shift reports."""
        if not correlations:
            return {'total_correlations': 0, 'correspondence_rate': 0.0}
        
        # Valid domain words corresponding to shifting concepts
        domain_anchors = {'shift', 'click', 'clickout', 'ejecta', 'template', 'layer', 'planck', 'phi', 'recursive', 'attractor', 'depth'}
        matched = sum(1 for c in correlations if c['word'] in domain_anchors)
        rate = matched / len(correlations) if correlations else 0.0
        
        return {
            'total_correlations': len(correlations),
            'with_archetype': matched,
            'correspondence_rate': rate
        }
    
    def generate_report(self, correlations: List[Dict], overlap_stats: Optional[Dict] = None) -> str:
        """Generate correlation report."""
        rate = self.compute_correlation_rate(correlations)
        archetype = self.compute_archetype_correspondence(correlations)
        
        report = []
        report.append("=" * 60)
        report.append("DELTA-SHIFT CORRELATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        if overlap_stats:
            report.append("[DOCUMENT-PAIR OVERLAP CORRELATION]:")
            report.append(f"  Docs Scored: {overlap_stats.get('docs_scored', 0)}")
            report.append(f"  Total Pairs: {overlap_stats.get('total_pairs', 0)}")
            report.append(f"  Pairs with Overlap: {overlap_stats.get('pairs_with_overlap', 0)}")
            report.append(f"  Correlation: {overlap_stats.get('correlation_percent', 0.0)}% (Target: >=30%)")
            report.append(f"  Verdict: {overlap_stats.get('verdict', 'UNKNOWN')}")
            report.append("")
        
        report.append("[TEMPORAL EVENT CORRELATION]:")
        report.append(f"  Total correlations: {len(correlations)}")
        report.append(f"  Correlation rate (within 7 days): {rate:.1%}")
        report.append(f"  Archetype correspondence: {archetype['correspondence_rate']:.1%}")
        report.append("")
        
        if correlations:
            report.append("[TOP CORRELATIONS]:")
            for c in sorted(correlations, key=lambda x: x['time_diff_days'])[:10]:
                report.append(f"  {c['word']}: {c['time_diff_days']:.1f} days ({c['correlation_type']}) — Report: {c['report_id']}")
        
        report.append("")
        report.append("=" * 60)
        return "\n".join(report)


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    sessions_dir = base_dir.parent / 'sessions'
    built_dir = base_dir / 'corpus' / 'built'
    
    correlator = ExperimentCorrelator(
        shift_report_dir=sessions_dir,
        delta_history_dir=built_dir
    )
    
    correlations = correlator.correlate(window_days=7)
    
    # Also evaluate document-pair overlap across Will Breaker internal documents
    lex = load_lexicons(
        base_dir / 'lexicon' / 'nrc_emotion_lexicon.csv',
        base_dir / 'lexicon' / 'vader_lexicon.csv',
        base_dir / 'config' / 'lexicon_weights.yaml'
    )
    from scraper.internal_collector import InternalCollector
    internal_col = InternalCollector(wb_dir=base_dir.parent)
    
    wb_docs = []
    for f in (base_dir.parent / 'sessions').glob('session-*.md'):
        wb_docs.append({'title': f.name, 'content': f.read_text(encoding='utf-8', errors='ignore')})
    for f in (base_dir.parent / 'research').glob('*.md'):
        wb_docs.append({'title': f.name, 'content': f.read_text(encoding='utf-8', errors='ignore')})
    
    base_model = BaselineContextModel()
    for d in wb_docs:
        base_model.add_document(tokenize(d['content']))
    scorer = AnomalyScorer(lex, base_model)
    
    overlap_results = correlator.correlate_document_overlap(wb_docs[:35], scorer, threshold=0.8)
    
    report = correlator.generate_report(correlations, overlap_stats=overlap_results)
    print(report)
