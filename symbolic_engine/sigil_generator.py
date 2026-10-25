"""
Procedural Sigil Generator — Algorithmic Geometry of Solomonic & Hermetic Seals
Generates SVG vector seals using concentric boundary rings, inscribed regular/star polygons,
and topological Rose-Cross coordinate walks derived deterministically from entity names.
Supports harmonic planetary geometries, animated SVG rotations, and dynamic boundary strain.
"""

import math
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


# Classical 7-Planet Sacred Geometry & Harmonic Color Profiles
PLANETARY_MATRICES = {
    "sol": {"polygon_points": 6, "gold_color": "#f1c40f", "accent_color": "#e67e22", "rot_speed_sec": 30},
    "luna": {"polygon_points": 9, "gold_color": "#bdc3c7", "accent_color": "#95a5a6", "rot_speed_sec": 40},
    "mercury": {"polygon_points": 8, "gold_color": "#1abc9c", "accent_color": "#16a085", "rot_speed_sec": 20},
    "venus": {"polygon_points": 7, "gold_color": "#2ecc71", "accent_color": "#27ae60", "rot_speed_sec": 35},
    "mars": {"polygon_points": 5, "gold_color": "#e74c3c", "accent_color": "#c0392b", "rot_speed_sec": 25},
    "jupiter": {"polygon_points": 4, "gold_color": "#9b59b6", "accent_color": "#8e44ad", "rot_speed_sec": 45},
    "saturn": {"polygon_points": 3, "gold_color": "#7f8c8d", "accent_color": "#34495e", "rot_speed_sec": 60},
}


@dataclass
class SigilConfig:
    size: int = 500
    stroke_width: float = 2.0
    bg_color: str = "#0d1117"
    primary_color: str = "#c9d1d9"
    accent_color: str = "#58a6ff"
    gold_color: str = "#d29922"
    polygon_points: int = 6  # 5=pentagram, 6=hexagram, 7=septagram, 8=octagram, 9=enneagram
    include_ticks: bool = True
    include_central_walk: bool = True
    animated: bool = False
    circle_integrity: float = 1.0  # 0.0 to 1.0 (shows boundary strain if < 1.0)
    planet: Optional[str] = None   # "sol", "luna", "mercury", "venus", "mars", "jupiter", "saturn"


class SigilGenerator:
    """Generates procedural SVG seals based on input name seeds and geometric rules."""

    def __init__(self, config: Optional[SigilConfig] = None):
        self.config = config or SigilConfig()

    @staticmethod
    def _seed_from_text(text: str) -> int:
        """Compute stable 32-bit integer seed from text."""
        h = hashlib.sha256(text.strip().lower().encode("utf-8")).digest()
        return int.from_bytes(h[:4], "big")

    def _polar_to_cartesian(self, cx: float, cy: float, r: float, angle_rad: float) -> Tuple[float, float]:
        """Convert polar (r, theta) to cartesian (x, y)."""
        x = cx + r * math.cos(angle_rad)
        y = cy + r * math.sin(angle_rad)
        return round(x, 2), round(y, 2)

    def generate_svg(self, name: str, seed: Optional[int] = None) -> str:
        """Generate complete, standalone SVG markup for a name/entity."""
        s = seed if seed is not None else self._seed_from_text(name)
        cfg = self.config
        sz = cfg.size
        cx = sz / 2.0
        cy = sz / 2.0

        # Apply planetary matrix presets if requested
        poly_pts = cfg.polygon_points
        gold_col = cfg.gold_color
        accent_col = cfg.accent_color
        rot_speed = 30
        if cfg.planet and cfg.planet.lower() in PLANETARY_MATRICES:
            pm = PLANETARY_MATRICES[cfg.planet.lower()]
            poly_pts = pm["polygon_points"]
            gold_col = pm["gold_color"]
            accent_col = pm["accent_color"]
            rot_speed = pm["rot_speed_sec"]

        r_outer = sz * 0.46
        r_inner = sz * 0.41
        r_poly = sz * 0.35
        r_core = sz * 0.22

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sz} {sz}" width="{sz}" height="{sz}">',
            f'  <defs>',
            f'    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">',
            f'      <feGaussianBlur stdDeviation="2.5" result="blur">',
        ]

        if cfg.animated:
            svg_parts.append(
                f'        <animate attributeName="stdDeviation" values="2;4;2" dur="3s" repeatCount="indefinite" />'
            )

        svg_parts.extend([
            f'      </feGaussianBlur>',
            f'      <feMerge>',
            f'        <feMergeNode in="blur" />',
            f'        <feMergeNode in="SourceGraphic" />',
            f'      </feMerge>',
            f'    </filter>',
            f'  </defs>',
            f'  <rect width="100%" height="100%" fill="{cfg.bg_color}" />',
        ])

        # 1. Outer Boundary Ring (Breached / Corrupted if integrity < 0.5)
        outer_stroke = cfg.primary_color
        if cfg.circle_integrity < 0.5:
            outer_stroke = "#e74c3c"
        elif cfg.circle_integrity < 0.75:
            outer_stroke = "#e67e22"

        svg_parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="{outer_stroke}" stroke-width="{cfg.stroke_width * 1.5}" />'
        )
        svg_parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="{cfg.primary_color}" stroke-width="{cfg.stroke_width}" />'
        )

        # 2. Circular Band Ticks / Degrees (72 Solomonic divisions)
        if cfg.include_ticks:
            tick_group_start = "  <g>"
            if cfg.animated:
                tick_group_start = (
                    f'  <g>\n'
                    f'    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="-360 {cx} {cy}" dur="{rot_speed * 1.5}s" repeatCount="indefinite" />'
                )
            svg_parts.append(tick_group_start)

            num_ticks = 72
            for i in range(num_ticks):
                ang = i * (2 * math.pi / num_ticks)
                is_major = (i % 6 == 0)
                tick_r1 = r_inner
                tick_r2 = r_inner + (r_outer - r_inner) * (0.8 if is_major else 0.4)
                x1, y1 = self._polar_to_cartesian(cx, cy, tick_r1, ang)
                x2, y2 = self._polar_to_cartesian(cx, cy, tick_r2, ang)
                color = gold_col if is_major else cfg.primary_color
                width = cfg.stroke_width * (1.2 if is_major else 0.6)
                svg_parts.append(
                    f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" opacity="0.75" />'
                )

            svg_parts.append("  </g>")

        # 3. Inscribed Regular Star Polygon
        poly_group_start = "  <g>"
        if cfg.animated:
            poly_group_start = (
                f'  <g>\n'
                f'    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{rot_speed}s" repeatCount="indefinite" />'
            )
        svg_parts.append(poly_group_start)

        n = poly_pts
        step = 2 if n >= 5 else 1
        poly_vertices = []
        for i in range(n):
            ang = (i * 2 * math.pi / n) - (math.pi / 2.0)
            poly_vertices.append(self._polar_to_cartesian(cx, cy, r_poly, ang))

        # Star edges
        for i in range(n):
            x1, y1 = poly_vertices[i]
            x2, y2 = poly_vertices[(i + step) % n]
            svg_parts.append(
                f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{gold_col}" stroke-width="{cfg.stroke_width}" opacity="0.85" />'
            )

        # Radial spokes to vertices
        for vx, vy in poly_vertices:
            svg_parts.append(
                f'    <line x1="{cx}" y1="{cy}" x2="{vx}" y2="{vy}" stroke="{cfg.primary_color}" stroke-width="{cfg.stroke_width * 0.7}" stroke-dasharray="3,3" opacity="0.5" />'
            )
            svg_parts.append(
                f'    <circle cx="{vx}" cy="{vy}" r="{cfg.stroke_width * 2}" fill="{cfg.bg_color}" stroke="{accent_col}" stroke-width="{cfg.stroke_width}" />'
            )

        svg_parts.append("  </g>")

        # Core circle
        svg_parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r_core}" fill="none" stroke="{accent_col}" stroke-width="{cfg.stroke_width}" opacity="0.6" />'
        )

        # 4. Central Topological Walk (Rose-Cross method)
        if cfg.include_central_walk and name:
            clean_name = "".join(ch for ch in name.upper() if ch.isalnum())
            if not clean_name:
                clean_name = "SEAL"
            
            walk_points = []
            for idx, char in enumerate(clean_name):
                char_val = ord(char)
                ang = (char_val * 137.5 * (math.pi / 180.0)) % (2 * math.pi)
                dist = r_core * 0.25 + (r_core * 0.7) * ((char_val % 10) / 10.0)
                walk_points.append(self._polar_to_cartesian(cx, cy, dist, ang))

            if len(walk_points) >= 2:
                path_d = [f"M {walk_points[0][0]} {walk_points[0][1]}"]
                for pt in walk_points[1:]:
                    path_d.append(f"L {pt[0]} {pt[1]}")
                svg_parts.append(
                    f'  <path d="{" ".join(path_d)}" fill="none" stroke="{accent_col}" stroke-width="{cfg.stroke_width * 1.5}" filter="url(#glow)" />'
                )
                sx, sy = walk_points[0]
                svg_parts.append(
                    f'  <circle cx="{sx}" cy="{sy}" r="{cfg.stroke_width * 3}" fill="{accent_col}" opacity="0.9" />'
                )
                fx, fy = walk_points[-1]
                svg_parts.append(
                    f'  <circle cx="{fx}" cy="{fy}" r="{cfg.stroke_width * 2}" fill="none" stroke="{gold_col}" stroke-width="{cfg.stroke_width * 1.5}" />'
                )

        # 5. Visual Integrity Degradation / Strain Fissures
        if cfg.circle_integrity < 0.95:
            strain_factor = 1.0 - cfg.circle_integrity
            fissure_count = int(strain_factor * 12) + 2
            svg_parts.append(f'  <!-- Containment Strain Overlay (Integrity: {cfg.circle_integrity:.2f}) -->')
            for f_idx in range(fissure_count):
                f_ang = (f_idx * (2 * math.pi / fissure_count) + (s % 10) * 0.1) % (2 * math.pi)
                r_start = r_inner * 0.85
                r_end = r_outer * 1.05
                fx1, fy1 = self._polar_to_cartesian(cx, cy, r_start, f_ang)
                fx2, fy2 = self._polar_to_cartesian(cx, cy, r_end, f_ang + 0.05)
                f_color = "#e74c3c" if cfg.circle_integrity < 0.5 else "#f39c12"
                svg_parts.append(
                    f'  <line x1="{fx1}" y1="{fy1}" x2="{fx2}" y2="{fy2}" stroke="{f_color}" stroke-width="{cfg.stroke_width * 1.8}" stroke-dasharray="4,2" opacity="0.9" />'
                )

        # 6. Entity Label & Integrity HUD
        svg_parts.append(
            f'  <text x="{cx}" y="{sz * 0.95}" text-anchor="middle" fill="{cfg.primary_color}" font-family="monospace" font-size="12" letter-spacing="3" opacity="0.85">{name.upper()}</text>'
        )
        if cfg.circle_integrity < 1.0:
            status_col = "#2ecc71" if cfg.circle_integrity >= 0.75 else ("#f39c12" if cfg.circle_integrity >= 0.5 else "#e74c3c")
            svg_parts.append(
                f'  <text x="{cx}" y="{sz * 0.98}" text-anchor="middle" fill="{status_col}" font-family="monospace" font-size="10" letter-spacing="1">INTEGRITY: {int(cfg.circle_integrity * 100)}%</text>'
            )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def save_svg(self, name: str, output_path: Path, seed: Optional[int] = None) -> Path:
        """Generate and save SVG to file."""
        svg_content = self.generate_svg(name, seed=seed)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg_content, encoding="utf-8")
        return output_path
