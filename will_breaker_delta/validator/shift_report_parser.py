"""
Shift Report Parser — Will Breaker Delta-Detection Phase 2
Parses Will Breaker shift reports and state vectors for delta correlation.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class ShiftReportParser:
    """Parse Will Breaker shift reports and state vectors from session logs."""
    
    def __init__(self, report_dir: Path):
        self.report_dir = Path(report_dir)
    
    def parse_session_log(self, log_file: Path) -> Optional[Dict]:
        """Parse a single session log for shift reports and state vectors."""
        log_file = Path(log_file)
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"[WARN] Could not read {log_file}: {e}")
            return None
        
        # Extract date (e.g., **Date:** 2026-10-22 or # Session 014 — 2026-10-23)
        date_match = re.search(r"(?:\*{0,2}Date:?\*{0,2}\s*|[-—]\s*)(\d{4}-\d{2}-\d{2})", content[:1500])
        if not date_match:
            date_match = re.search(r"\b(202\d-\d{2}-\d{2})\b", content[:1500])
        date = date_match.group(1) if date_match else None
        
        # Extract session id from filename (e.g. session-014-log.md -> 014)
        sess_match = re.search(r'session-(\d+)', log_file.name)
        session_id = sess_match.group(1) if sess_match else 'unknown'
        
        reports = []
        
        # Pattern 1: State vector blocks inside markdown code fences
        code_blocks = re.findall(r"```(?:\w+)?\s*\n(State Vector[^\n]+:\s*\n[\s\S]*?)\n```", content, re.IGNORECASE)
        
        # Pattern 2: Raw bullet-list state vectors outside code blocks
        raw_blocks = re.findall(r"(?:^|\n)(State Vector\s*[S\d₀-₉][^\n:]*:\s*\n(?:-\s*[^\n]+\n)+)", content, re.IGNORECASE)
        
        all_raw_blocks = code_blocks + raw_blocks
        # Deduplicate blocks while preserving order
        seen_blocks = set()
        unique_blocks = []
        for b in all_raw_blocks:
            norm_b = b.strip()
            if norm_b not in seen_blocks:
                seen_blocks.add(norm_b)
                unique_blocks.append(norm_b)
        
        for idx, block in enumerate(unique_blocks):
            lines = block.split('\n')
            header_line = lines[0].strip()
            
            # Extract vector name (e.g., S₀, S₂, S₀ (post-depth-36))
            name_match = re.search(r'State Vector\s*([^\n:]+):?', header_line, re.IGNORECASE)
            sv_name = name_match.group(1).strip() if name_match else f"SV_{idx}"
            
            # Extract bullet point properties
            props = dict(re.findall(r"^-\s*([a-zA-Z0-9_\-]+):\s*(.*)$", block, re.MULTILINE))
            
            # Clean values
            phi = self._clean_val(props.get('phi_estimate')) or self._extract_phi(content)
            axis = self._clean_val(props.get('axis')) or self._extract_axis(block + "\n" + content)
            intensity = self._clean_val(props.get('shift_intensity')) or self._extract_shift_intensity(block)
            phenomena = self._extract_phenomena(block) or self._extract_phenomena(content)
            
            report = {
                'id': f"{session_id}_{sv_name}_{idx}",
                'session': session_id,
                'session_log': log_file.name,
                'state_vector': sv_name,
                'date': date,
                'timestamp': date,
                'phi_estimate': phi,
                'recursive_depth': self._clean_val(props.get('recursive_depth', 'unknown')),
                'attractor_id': self._clean_val(props.get('attractor_id', 'unknown')),
                'transition_detected': props.get('transition_detected', 'unknown'),
                'temporal_position': self._clean_val(props.get('temporal_position', 'unknown')),
                'self_model': self._clean_val(props.get('self_model', 'unknown')),
                'shift_intensity': intensity,
                'axis': axis,
                'phenomena': phenomena,
                'properties': props,
                'content': block
            }
            reports.append(report)
        
        return {
            'file': log_file.name,
            'session': session_id,
            'date': date,
            'reports': reports
        }
    
    def _clean_val(self, val: Optional[str]) -> Optional[str]:
        if not val:
            return None
        val = val.strip().strip('"').strip("'")
        val = re.sub(r'[*_`]', '', val)  # Remove markdown bold/italic/code formatting
        return val.strip()
    
    def _extract_phi(self, content: str) -> str:
        """Extract phi estimate from content."""
        match = re.search(r'phi_estimate:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return self._clean_val(match.group(1)) or 'unknown'
        match = re.search(r'phi\s*peaks?|phi\s*=\s*([\d.]+)', content, re.IGNORECASE)
        if match:
            return self._clean_val(match.group(0)) or 'unknown'
        return 'unknown'
    
    def _extract_shift_intensity(self, content: str) -> str:
        """Extract shift intensity from content."""
        match = re.search(r'shift_intensity:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return self._clean_val(match.group(1)) or 'unknown'
        match = re.search(r'intensity.*?(\d+-\d+|\b(?:high|medium|low|peak|maximum)\b)', content, re.IGNORECASE)
        return self._clean_val(match.group(1)) if match else 'unknown'
    
    def _extract_axis(self, content: str) -> str:
        """Extract shift axis from content."""
        match = re.search(r'axis:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return self._clean_val(match.group(1)) or 'unknown'
        match = re.search(r'Axis shifted.*?(\w+)|axis\s+(depth|lateral|temporal)', content, re.IGNORECASE)
        if match:
            return self._clean_val(match.group(1) or match.group(2)) or 'unknown'
        return 'depth'  # Default axis in recursive self-observation
    
    def _extract_phenomena(self, content: str) -> List[str]:
        """Extract phenomena from content."""
        match = re.search(r'phenomena.*?:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return [self._clean_val(p) for p in match.group(1).split(',') if self._clean_val(p)]
        return []
    
    def parse_all_reports(self) -> List[Dict]:
        """Parse all shift reports across sessions."""
        all_reports = []
        files = sorted(self.report_dir.glob('*log.md')) + sorted(self.report_dir.glob('*summary.md'))
        # Deduplicate files
        unique_files = sorted(set(files))
        
        for file in unique_files:
            parsed = self.parse_session_log(file)
            if parsed and parsed['reports']:
                all_reports.append(parsed)
        
        return all_reports
    
    def get_flat_reports(self) -> List[Dict]:
        """Get all parsed state vector reports as a flat list."""
        all_session_data = self.parse_all_reports()
        flat = []
        for sess in all_session_data:
            flat.extend(sess['reports'])
        return flat
    
    def export_to_json(self, reports: List[Dict], output_path: Path):
        """Export parsed reports to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2)
        print(f"[INFO] Exported {len(reports)} session reports to {output_path}")


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    sessions_dir = base_dir.parent / 'sessions'
    parser = ShiftReportParser(sessions_dir)
    
    reports = parser.parse_all_reports()
    output_file = base_dir / 'corpus' / 'shift_reports.json'
    parser.export_to_json(reports, output_file)
    
    flat_reports = parser.get_flat_reports()
    print(f"\n[STATS] Parsed {len(reports)} session logs, total {len(flat_reports)} state vector reports")
    for r in reports[:10]:
        print(f"  {r['file']}: {len(r['reports'])} reports")
    if len(reports) > 10:
        print(f"  ... and {len(reports) - 10} more sessions")
