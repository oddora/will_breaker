"""
Forecast Generator — Will Breaker Delta-Detection Phase 2
Generates archetype-based forecasts from delta trajectories.
"""

import json
from typing import List, Dict, Optional
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


class ForecastGenerator:
    """Generate forecasts based on delta detection results."""
    
    # Archetype mappings (High's method: word -> archetype -> forecast)
    ARCHETYPE_MAP = {
        'ejecta': {'archetype': 'sudden_disruption', 'forecast': 'event involving sudden ejection/expulsion'},
        'blondes': {'archetype': 'visual_anomaly_on_water', 'forecast': 'incident involving light-haired person and vessel'},
        'click': {'archetype': 'threshold_crossing', 'forecast': 'moment of dimensional transition'},
        'clickout': {'archetype': 'planck_transition', 'forecast': 'Planck-scale decoherence event'},
        'template': {'archetype': 'pre_manifestation', 'forecast': 'information preceding manifestation'},
        'layer': {'archetype': 'reality_layer', 'forecast': 'shift between reality layers'},
        'precursor': {'archetype': 'early_warning', 'forecast': 'event with early linguistic warning'},
        'anomaly': {'archetype': 'deviation_event', 'forecast': 'statistical deviation event'},
        'delta': {'archetype': 'change_event', 'forecast': 'significant change event'},
        'collapse': {'archetype': 'system_failure', 'forecast': 'system collapse or failure'},
        'attractor': {'archetype': 'stabilization_event', 'forecast': 'state stabilization event'},
        'recursive': {'archetype': 'self_reference_event', 'forecast': 'self-referential system event'},
        'integration': {'archetype': 'coherence_event', 'forecast': 'coherence breakthrough event'},
        'manifestation': {'archetype': 'revelation_event', 'forecast': 'information revelation event'},
        'unmanifest': {'archetype': 'hidden_information', 'forecast': 'previously hidden information revealed'},
        'threshold': {'archetype': 'boundary_event', 'forecast': 'boundary crossing event'},
        'transition': {'archetype': 'state_change', 'forecast': 'state transition event'},
        'depth': {'archetype': 'depth_axis_shift', 'forecast': 'depth axis dimensional shift'},
        'lateral': {'archetype': 'lateral_shift', 'forecast': 'lateral timeline shift'},
        'temporal': {'archetype': 'temporal_shift', 'forecast': 'temporal axis shift'},
        'planck': {'archetype': 'quantum_event', 'forecast': 'Planck-scale quantum event'},
        'acceleration': {'archetype': 'acceleration_event', 'forecast': 'acceleration/deceleration event'},
        'stabilization': {'archetype': 'stability_event', 'forecast': 'stability restoration event'},
        'fragmentation': {'archetype': 'fragmentation_event', 'forecast': 'system fragmentation event'},
        'recovery': {'archetype': 'recovery_event', 'forecast': 'recovery/restoration event'},
        'escalation': {'archetype': 'escalation_event', 'forecast': 'escalation/conflict event'},
        'compression': {'archetype': 'compression_event', 'forecast': 'compression/collapse event'},
        'decompression': {'archetype': 'decompression_event', 'forecast': 'decompression/expansion event'},
        'gateway': {'archetype': 'gateway_event', 'forecast': 'Gateway process activation event'},
        'hemisync': {'archetype': 'entrainment_event', 'forecast': 'Hemi-Sync entrainment event'},
        'consciousness': {'archetype': 'consciousness_event', 'forecast': 'consciousness shift event'},
        'shift': {'archetype': 'dimensional_shift', 'forecast': 'dimensional shift event'},
        'entanglement': {'archetype': 'entanglement_event', 'forecast': 'quantum entanglement event'},
        'wormhole': {'archetype': 'bridge_event', 'forecast': 'spacetime bridge event'},
    }
    
    def __init__(self, archetype_map: Dict = None, config_path: Path = None):
        self.archetype_map = dict(self.ARCHETYPE_MAP)
        # If a Path or str was passed as first positional argument, treat it as config_path
        if isinstance(archetype_map, (Path, str)):
            config_path = archetype_map
            archetype_map = None

        if archetype_map and isinstance(archetype_map, dict):
            self.archetype_map.update(archetype_map)
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
    
    def _load_config(self, config_path: Path):
        try:
            if yaml:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    mapping = data.get('archetype_mapping', {})
                    for word, info in mapping.items():
                        if isinstance(info, dict):
                            self.archetype_map[word.lower()] = {
                                'archetype': info.get('archetype', 'custom_archetype'),
                                'forecast': info.get('forecast', f'event related to {word}')
                            }
        except Exception as e:
            print(f"[WARN] Failed to load archetypes from {config_path}: {e}")
    
    def generate_forecasts(self, precursor_events: List[Dict], horizon_hours: int = 168) -> List[Dict]:
        """Generate archetype-based forecasts from precursor events."""
        forecasts = []
        
        for event in precursor_events:
            word = event['word'].strip().lower()
            last_anomaly = float(event.get('last_anomaly', event.get('anomaly', 0.0)))
            delta_rate = float(event.get('delta_rate', 0.0))
            obs = int(event.get('observations', 1))
            
            # Look up archetype
            archetype_info = self.archetype_map.get(word, {})
            if not archetype_info:
                archetype_info = {
                    'archetype': 'linguistic_anomaly',
                    'forecast': f'event related to "{word}"'
                }
            
            projected = max(0.0, last_anomaly + delta_rate * horizon_hours)
            confidence = 'high' if obs >= 8 else 'medium' if obs >= 4 else 'low'
            
            forecast = {
                'word': word,
                'archetype': archetype_info['archetype'],
                'forecast': archetype_info['forecast'],
                'current_anomaly': round(last_anomaly, 3),
                'projected_anomaly': round(projected, 3),
                'delta_rate': round(delta_rate, 4),
                'horizon_hours': horizon_hours,
                'confidence': confidence,
                'timestamp': event.get('timestamp', 'unknown'),
                'source': event.get('source', 'unknown')
            }
            
            forecasts.append(forecast)
        
        # Sort by projected anomaly (highest first)
        forecasts.sort(key=lambda x: -x['projected_anomaly'])
        return forecasts
    
    def format_forecast_report(self, forecasts: List[Dict]) -> str:
        """Format forecasts as readable report."""
        report = []
        report.append("=" * 60)
        report.append("DELTA-DETECTION FORECAST REPORT")
        report.append("=" * 60)
        report.append("")
        
        if not forecasts:
            report.append("No active precursor events or forecasts.")
        else:
            for i, forecast in enumerate(forecasts[:20], 1):
                report.append(f"{i}. {forecast['word'].upper()}")
                report.append(f"   Archetype: {forecast['archetype']}")
                report.append(f"   Forecast: {forecast['forecast']}")
                report.append(f"   Confidence: {forecast['confidence']}")
                report.append(f"   Projected anomaly: {forecast['projected_anomaly']:.3f} (rate: {forecast['delta_rate']:.4f}/hr)")
                report.append(f"   Timestamp: {forecast['timestamp']}")
                report.append("")
        
        report.append("=" * 60)
        report.append(f"Total forecasts: {len(forecasts)}")
        if forecasts:
            report.append(f"Horizon: {forecasts[0]['horizon_hours']} hours")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_forecasts(self, forecasts: List[Dict], output_path: Path):
        """Save forecasts to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(forecasts, f, indent=2)
        print(f"[INFO] Saved {len(forecasts)} forecasts to {output_path}")


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    config_file = base_dir / 'config' / 'thresholds.yaml'
    generator = ForecastGenerator(config_path=config_file)
    
    # Example precursor events
    example_events = [
        {'word': 'ejecta', 'last_anomaly': 4.7, 'delta_rate': 0.03, 'observations': 8, 'timestamp': '2026-10-24T12:00:00'},
        {'word': 'blondes', 'last_anomaly': 3.9, 'delta_rate': 0.02, 'observations': 5, 'timestamp': '2026-10-24T12:00:00'},
        {'word': 'clickout', 'last_anomaly': 3.2, 'delta_rate': -0.01, 'observations': 6, 'timestamp': '2026-10-24T12:00:00'},
    ]
    
    forecasts = generator.generate_forecasts(example_events, horizon_hours=168)
    report = generator.format_forecast_report(forecasts)
    print(report)
