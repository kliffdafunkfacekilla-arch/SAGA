"""
fov_calculator.py
Provides Line of Sight (LoS) and Fog of War raycasting using Bresenham's line algorithm.
"""
import math
from typing import List, Dict, Set, Tuple

def get_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """Calculates points on a line using Bresenham's algorithm."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x, y))
    return points

def calculate_fov(grid: List[List[Dict]], start_x: int, start_y: int, radius: int) -> Set[Tuple[int, int]]:
    """
    Casts rays to the perimeter of a bounding box.
    Returns a set of all (x, y) coordinates visible from the start.
    Terminates a ray if it hits a node with the 'blocks_los' tag.
    """
    visible = set()
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    
    min_x = max(0, start_x - radius)
    max_x = min(width - 1, start_x + radius)
    min_y = max(0, start_y - radius)
    max_y = min(height - 1, start_y + radius)
    
    perimeter = []
    for x in range(min_x, max_x + 1):
        perimeter.append((x, min_y))
        perimeter.append((x, max_y))
    for y in range(min_y + 1, max_y):
        perimeter.append((min_x, y))
        perimeter.append((max_x, y))
        
    for px, py in perimeter:
        line = get_line(start_x, start_y, px, py)
        for lx, ly in line:
            # Enforce circular radius instead of square bounding box
            if (lx - start_x)**2 + (ly - start_y)**2 > radius**2:
                break
                
            visible.add((lx, ly))
            
            try:
                node = grid[ly][lx]
                if isinstance(node, dict):
                    tags = node.get("tags", [])
                    if "blocks_los" in tags:
                        break # Wall hit, stop ray
            except IndexError:
                break
                
    return visible
