import os
import glob

tiles_dir = os.path.join("assets", "Tiles")
html_path = "tile_viewer.html"

if not os.path.exists(tiles_dir):
    print("Tiles directory not found!")
    exit(1)

tiles = sorted(glob.glob(os.path.join(tiles_dir, "*.png")))

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>SAGA Tile Viewer</title>
    <style>
        body { background-color: #1a1a1a; color: #fff; font-family: sans-serif; padding: 20px; }
        .grid { display: flex; flex-wrap: wrap; gap: 20px; }
        .tile-card { background: #333; padding: 10px; border-radius: 8px; text-align: center; width: 150px; }
        .tile-card img { max-width: 100%; border: 2px solid #555; border-radius: 4px; image-rendering: pixelated; }
        .tile-name { margin-top: 10px; font-size: 12px; word-break: break-all; color: #aaa; }
    </style>
</head>
<body>
    <h1>SAGA Tile Viewer</h1>
    <p>Here are all the tiles in your assets/Tiles folder. Find the ones you want for grass, water, wall, and road!</p>
    <div class="grid">
"""

for tile in tiles:
    filename = os.path.basename(tile)
    html_content += f"""
        <div class="tile-card">
            <img src="{tile.replace(os.sep, '/')}" alt="{filename}">
            <div class="tile-name">{filename}</div>
        </div>
    """

html_content += """
    </div>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Viewer created at {os.path.abspath(html_path)}")
