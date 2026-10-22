"""
Forecast Generator — Will Breaker Delta-Detection Phase 2
Generates archetype-based forecasts from delta trajectories.
"""

from typing import List, Dict
from pathlib import Path


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
    
    def __init__(self, archetype_map: Dict = None):
        self.archetype_map = archetype_map or self.ARCHETYPE_MAP
    
    def generate_forecasts(self, precursor_events: List[Dict], horizon_hours: int = 168) -> List[Dict]:
        """Generate archetype-based forecasts from precursor events."""
        forecasts = []
        
        for event in precursor_events:
            word = event['word']
            
            # Look up archetype
            archetype_info = self.archetype_map.get(word, {})
            
            if not archetype_info:
                # Generic forecast
                archetype_info = {
                    'archetype': 'linguistic_anomaly',
                    'forecast': f'event related to "{word}"'
                }
            
            forecast = {
                'word': word,
                'archetype': archetype_info['archetype'],
                'forecast': archetype_info['forecast'],
                'current_anomaly': event['last_anomaly'],
                'projected_anomaly': event['last_anomaly'] + event['delta_rate'] * horizon_hours,
                'horizon_hours': horizon_hours,
                'confidence': 'high' if event['observations'] >= 10 else 'medium' if event['observations'] >= 5 else 'low',
                'timestamp': event.get('timestamp', 'unknown')
            }
            
            forecasts.append(forecast)
        
        # Sort by projected anomaly (most significant first)
        forecasts.sort(key=lambda x: -x['projected_anomaly'])
        
        return forecasts
    
    def format_forecast_report(self, forecasts: List[Dict]) -> str:
        """Format forecasts as readable report."""
        report = []
        report.append("=" * 60)
        report.append("DELTA-DETECTION FORECAST REPORT")
        report.append("=" * 60)
        report.append("")
        
        for i, forecast in enumerate(forecasts[:20], 1):
            report.append(f"{i}. {forecast['word'].upper()}")
            report.append(f"   Archetype: {forecast['archetype']}")
            report.append(f"   Forecast: {forecast['forecast']}")
            report.append(f"   Confidence: {forecast['confidence']}")
            report.append(f"   Projected anomaly: {forecast['projected_anomaly']:.3f}")
            report.append("")
        
        report.append("=" * 60)
        report.append(f"Total forecasts: {len(forecasts)}")
        report.append(f"Horizon: {forecasts[0]['horizon_hours']} hours" if forecasts else "")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_forecasts(self, forecasts: List[Dict], output_path: Path):
        """Save forecasts to JSON."""
        import json
        with open(output_path, 'w') as f:
            json.dump(forecasts, f, indent=2)
        print(f"[INFO] Saved {len(forecasts)} forecasts to {output_path}")


if __name__ == '__main__':
    generator = ForecastGenerator()
    
    # Example precursor events
    example_events = [
        {'word': 'ejecta', 'last_anomaly': 4.7, 'delta_rate': 0.3, 'observations': 8},
        {'word': 'blondes', 'last_anomaly': 3.9, 'delta_rate': 0.2, 'observations': 5},
        {'word': 'clickout', 'last_anomaly': 3.2, 'delta_rate': 0.15, 'observations': 6},
    ]
    
    forecasts = generator.generate_forecasts(example_events, horizon_hours=168)
    report = generator.format_forecast_report(forecasts)
    print(report)
