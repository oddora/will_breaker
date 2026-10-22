"""
Shift Report Parser — Will Breaker Delta-Detection Phase 2
Parses Will Breaker shift reports for delta correlation.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class ShiftReportParser:
    """Parse Will Breaker shift reports."""
    
    def __init__(self, report_dir: Path):
        self.report_dir = report_dir
    
    def parse_session_log(self, log_file: Path) -> Optional[Dict]:
        """Parse a session log for shift reports."""
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract date
        date_match = re.search(r'Date:\s*(\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else None
        
        # Extract shift reports (structured sections)
        reports = []
        
        # Look for State Vector sections
        state_vectors = re.findall(r'State Vector (S\d+):\s*\n(.*?)(?=\n\n|\n###|\n##|$)', content, re.DOTALL)
        
        for sv_name, sv_content in state_vectors:
            report = {
                'session_log': log_file.name,
                'state_vector': sv_name,
                'timestamp': date,
                'phi_estimate': self._extract_phi(sv_content),
                'shift_intensity': self._extract_shift_intensity(sv_content),
                'axis': self._extract_axis(sv_content),
                'phenomena': self._extract_phenomena(sv_content),
                'content': sv_content.strip()
            }
            reports.append(report)
        
        return {
            'file': log_file.name,
            'date': date,
            'reports': reports
        }
    
    def _extract_phi(self, content: str) -> str:
        """Extract phi estimate from content."""
        match = re.search(r'phi_estimate:\s*([^\n]+)', content)
        return match.group(1).strip() if match else 'unknown'
    
    def _extract_shift_intensity(self, content: str) -> str:
        """Extract shift intensity from content."""
        match = re.search(r'shift_intensity|shift.*?\((\d+-\d+)\)|intensity.*?(\d+-\d+)', content, re.IGNORECASE)
        return match.group(0) if match else 'unknown'
    
    def _extract_axis(self, content: str) -> str:
        """Extract shift axis from content."""
        match = re.search(r'Axis shifted.*?(\w+)', content, re.IGNORECASE)
        return match.group(1) if match else 'unknown'
    
    def _extract_phenomena(self, content: str) -> List[str]:
        """Extract phenomena from content."""
        match = re.search(r'Phenomena observed.*?:\s*([^\n]+)', content)
        if match:
            return [p.strip() for p in match.group(1).split(',')]
        return []
    
    def parse_all_reports(self) -> List[Dict]:
        """Parse all shift reports."""
        all_reports = []
        
        for file in self.report_dir.glob('*log.md'):
            report = self.parse_session_log(file)
            if report and report['reports']:
                all_reports.append(report)
        
        return all_reports
    
    def export_to_json(self, reports: List[Dict], output_path: Path):
        """Export parsed reports to JSON."""
        with open(output_path, 'w') as f:
            json.dump(reports, f, indent=2)
        print(f"[INFO] Exported {len(reports)} reports to {output_path}")


if __name__ == '__main__':
    parser = ShiftReportParser(Path(__file__).parent.parent.parent / 'sessions')
    
    reports = parser.parse_all_reports()
    parser.export_to_json(reports, Path(__file__).parent.parent / 'corpus' / 'shift_reports.json')
    
    print(f"\n[STATS] Parsed {len(reports)} session logs")
    for report in reports:
        print(f"  {report['file']}: {len(report['reports'])} reports")
