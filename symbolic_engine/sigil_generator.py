"""
Procedural Sigil Generator — Algorithmic Geometry of Solomonic & Hermetic Seals
Generates SVG vector seals using concentric boundary rings, inscribed regular/star polygons,
and topological Rose-Cross coordinate walks derived deterministically from entity names.
"""

import math
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


@dataclass
class SigilConfig:
    size: int = 500
    stroke_width: float = 2.0
    bg_color: str = "#0d1117"
    primary_color: str = "#c9d1d9"
    accent_color: str = "#58a6ff"
    gold_color: str = "#d29922"
    polygon_points: int = 6  # 5=pentagram, 6=hexagram, 7=septagram, 8=octagram
    include_ticks: bool = True
    include_central_walk: bool = True


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

        r_outer = sz * 0.46
        r_inner = sz * 0.41
        r_poly = sz * 0.35
        r_core = sz * 0.22

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sz} {sz}" width="{sz}" height="{sz}">',
            f'  <defs>',
            f'    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">',
            f'      <feGaussianBlur stdDeviation="2" result="blur" />',
            f'      <feMerge>',
            f'        <feMergeNode in="blur" />',
            f'        <feMergeNode in="SourceGraphic" />',
            f'      </feMerge>',
            f'    </filter>',
            f'  </defs>',
            f'  <rect width="100%" height="100%" fill="{cfg.bg_color}" />',
        ]

        # 1. Outer Concentric Boundary Rings
        svg_parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="{cfg.primary_color}" stroke-width="{cfg.stroke_width * 1.5}" />'
        )
        svg_parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="{cfg.primary_color}" stroke-width="{cfg.stroke_width}" />'
        )

        # 2. Circular Band Ticks / Degrees
        if cfg.include_ticks:
            num_ticks = 72  # Solomonic 72 divisions
            for i in range(num_ticks):
                ang = i * (2 * math.pi / num_ticks)
                is_major = (i % 6 == 0)
                tick_r1 = r_inner
                tick_r2 = r_inner + (r_outer - r_inner) * (0.8 if is_major else 0.4)
                x1, y1 = self._polar_to_cartesian(cx, cy, tick_r1, ang)
                x2, y2 = self._polar_to_cartesian(cx, cy, tick_r2, ang)
                color = cfg.gold_color if is_major else cfg.primary_color
                width = cfg.stroke_width * (1.2 if is_major else 0.6)
                svg_parts.append(
                    f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" opacity="0.75" />'
                )

        # 3. Inscribed Regular Star Polygon
        n = cfg.polygon_points
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
                f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cfg.gold_color}" stroke-width="{cfg.stroke_width}" opacity="0.85" />'
            )

        # Radial spokes to vertices
        for vx, vy in poly_vertices:
            svg_parts.append(
                f'  <line x1="{cx}" y1="{cy}" x2="{vx}" y2="{vy}" stroke="{cfg.primary_color}" stroke-width="{cfg.stroke_width * 0.7}" stroke-dasharray="3,3" opacity="0.5" />'
            )
            # Terminal circles on vertices
            svg_parts.append(
                f'  <circle cx="{vx}" cy="{vy}" r="{cfg.stroke_width * 2}" fill="{cfg.bg_color}" stroke="{cfg.accent_color}" stroke-width="{cfg.stroke_width}" />'
            )

        # Core circle
        svg_parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r_core}" fill="none" stroke="{cfg.accent_color}" stroke-width="{cfg.stroke_width}" opacity="0.6" />'
        )

        # 4. Central Topological Walk (Rose-Cross method)
        if cfg.include_central_walk and name:
            clean_name = "".join(ch for ch in name.upper() if ch.isalnum())
            if not clean_name:
                clean_name = "SEAL"
            
            walk_points = []
            for idx, char in enumerate(clean_name):
                char_val = ord(char)
                ang = (char_val * 137.5 * (math.pi / 180.0)) % (2 * math.pi)  # Golden angle distribution
                dist = r_core * 0.25 + (r_core * 0.7) * ((char_val % 10) / 10.0)
                walk_points.append(self._polar_to_cartesian(cx, cy, dist, ang))

            # Connect walk points
            if len(walk_points) >= 2:
                path_d = [f"M {walk_points[0][0]} {walk_points[0][1]}"]
                for pt in walk_points[1:]:
                    path_d.append(f"L {pt[0]} {pt[1]}")
                svg_parts.append(
                    f'  <path d="{" ".join(path_d)}" fill="none" stroke="{cfg.accent_color}" stroke-width="{cfg.stroke_width * 1.5}" filter="url(#glow)" />'
                )

                # Start node circle
                sx, sy = walk_points[0]
                svg_parts.append(
                    f'  <circle cx="{sx}" cy="{sy}" r="{cfg.stroke_width * 3}" fill="{cfg.accent_color}" opacity="0.9" />'
                )

                # Terminal bar across final segment
                fx, fy = walk_points[-1]
                svg_parts.append(
                    f'  <circle cx="{fx}" cy="{fy}" r="{cfg.stroke_width * 2}" fill="none" stroke="{cfg.gold_color}" stroke-width="{cfg.stroke_width * 1.5}" />'
                )

        # 5. Label at bottom inside ring
        svg_parts.append(
            f'  <text x="{cx}" y="{sz * 0.96}" text-anchor="middle" fill="{cfg.primary_color}" font-family="monospace" font-size="12" letter-spacing="3" opacity="0.8">{name.upper()}</text>'
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
