import os
import json
import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TILES_DIR = os.path.join(BASE_DIR, "assets", "Tiles")
MAPPING_FILE = os.path.join(BASE_DIR, "assets", "tile_mapping.json")

class TileMapperHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/tile_viewer.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Load current mapping
            mapping = {}
            if os.path.exists(MAPPING_FILE):
                try:
                    with open(MAPPING_FILE, "r") as f:
                        mapping = json.load(f)
                except Exception:
                    pass
            
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            current_page = int(query_params.get('page', ['1'])[0])
            search_query = query_params.get('q', [''])[0].lower()
            
            # Recursively find ALL tiles
            assets_dir = os.path.join(BASE_DIR, "assets")
            all_tiles = []
            for root, dirs, files in os.walk(assets_dir):
                for f in files:
                    if f.lower().endswith('.png'):
                        all_tiles.append(os.path.join(root, f))
            
            # Filter by search
            if search_query:
                all_tiles = [t for t in all_tiles if search_query in os.path.basename(t).lower()]
            else:
                all_tiles = sorted(all_tiles)
                
            tiles_per_page = 200
            total_pages = max(1, (len(all_tiles) + tiles_per_page - 1) // tiles_per_page)
            current_page = min(max(1, current_page), total_pages)
            
            start_idx = (current_page - 1) * tiles_per_page
            end_idx = start_idx + tiles_per_page
            tiles = all_tiles[start_idx:end_idx]
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SAGA Tile Mapper</title>
                <style>
                    body { background-color: #1a1a1a; color: #fff; font-family: sans-serif; padding: 20px; }
                    .header { position: sticky; top: 0; background: #222; padding: 15px; border-bottom: 2px solid #44FF44; z-index: 100;}
                    .grid { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px;}
                    .tile-card { background: #333; padding: 10px; border-radius: 8px; text-align: center; width: 100px; cursor: pointer; transition: transform 0.2s; }
                    .tile-card:hover { transform: scale(1.05); border-color: #44FF44; }
                    .tile-card img { max-width: 100%; border: 2px solid #555; border-radius: 4px; image-rendering: pixelated; pointer-events: none;}
                    .tile-name { margin-top: 10px; font-size: 10px; word-break: break-all; color: #aaa; pointer-events: none;}
                    select, input { padding: 8px; font-size: 14px; background: #333; color: white; border: 1px solid #777; margin-right: 10px;}
                    .status { color: #44FF44; font-weight: bold; margin-left: 10px;}
                    .badge { background: #44FF44; color: black; font-size: 10px; padding: 3px 6px; border-radius: 10px; margin-top: 5px; display: inline-block;}
                    .pagination { margin-top: 10px; }
                    .pagination a, .pagination span { padding: 5px 10px; background: #333; margin-right: 5px; text-decoration: none; color: white; border: 1px solid #555; }
                    .pagination a:hover { background: #555; }
                    .pagination .active { background: #44FF44; color: black; border: none; }
                </style>
                <script>
                    function selectTile(filepath) {
                        const terrainType = document.getElementById('terrainType').value;
                        fetch('/map_tile', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ terrain: terrainType, path: filepath })
                        })
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('status').innerText = 'Saved ' + terrainType + '!';
                            setTimeout(() => { document.getElementById('status').innerText = ''; }, 2000);
                        });
                    }
                </script>
            </head>
            <body>
                <div class="header">
                    <h1>SAGA Tile Mapper</h1>
                    <div style="margin-bottom: 10px;">
                        <label>Assign clicked tile to: </label>
                        <select id="terrainType">
                            <optgroup label="Biomes">
                                <option value="grass">Grassland</option>
                                <option value="forest">Forest</option>
                                <option value="desert">Desert</option>
                                <option value="tundra">Tundra</option>
                                <option value="swamp">Swamp</option>
                                <option value="jungle">Jungle</option>
                                <option value="mountains">Mountains</option>
                                <option value="hills">Hills</option>
                                <option value="wasteland">Wasteland</option>
                                <option value="volcanic">Volcanic</option>
                                <option value="taiga">Taiga</option>
                                <option value="savannah">Savannah</option>
                            </optgroup>
                            <optgroup label="Water Variants">
                                <option value="water">Shallow Water</option>
                                <option value="deep_water">Deep Water</option>
                                <option value="ocean">Ocean</option>
                                <option value="river">River</option>
                            </optgroup>
                            <optgroup label="Map Features">
                                <option value="road">Road</option>
                                <option value="dirt_path">Dirt Path</option>
                                <option value="village">Village</option>
                                <option value="town">Town</option>
                                <option value="city">City</option>
                                <option value="castle">Castle</option>
                                <option value="ruins">Ruins</option>
                                <option value="wall">Wall</option>
                            </optgroup>
                            <optgroup label="Entities">
                                <option value="player">Player</option>
                                <option value="enemy">Enemy</option>
                            </optgroup>
                        </select>
                        <span id="status" class="status"></span>
                    </div>
                    <div>
                        <form method="GET" action="/">
                            <input type="text" name="q" placeholder="Search (e.g. 'sword')" value="{search_query}">
                            <input type="submit" value="Search">
                        </form>
                    </div>
                    <div class="pagination">
            """
            
            # Pagination UI
            def make_url(p):
                return f"/?page={p}&q={urllib.parse.quote(search_query)}"
            
            if current_page > 1:
                html += f'<a href="{make_url(current_page-1)}">&laquo; Prev</a>'
            
            # Show a few pages around current
            p_start = max(1, current_page - 4)
            p_end = min(total_pages, current_page + 4)
            for p in range(p_start, p_end + 1):
                if p == current_page:
                    html += f'<span class="active">{p}</span>'
                else:
                    html += f'<a href="{make_url(p)}">{p}</a>'
                    
            if current_page < total_pages:
                html += f'<a href="{make_url(current_page+1)}">Next &raquo;</a>'
                
            html += f"<span style='margin-left: 15px; color:#aaa'>Total: {len(all_tiles)} tiles</span></div></div><div class='grid'>"
            
            # reverse lookup for mapping badges
            rev_map = {v: k for k, v in mapping.items()}
            
            for tile in tiles:
                filename = os.path.basename(tile)
                # We need relative path for the frontend image tag, but absolute for the saving
                rel_url = "/" + os.path.relpath(tile, BASE_DIR).replace(os.sep, '/')
                
                badge_html = ""
                if tile in rev_map:
                    badge_html = f"<div class='badge'>{rev_map[tile].upper()}</div>"
                    
                html += f"""
                    <div class="tile-card" onclick="selectTile('{tile.replace(os.sep, '/')}')">
                        <img src="{rel_url}" alt="{filename}">
                        <div class="tile-name">{filename}</div>
                        {badge_html}
                    </div>
                """
            
            html += """
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            return
            
        return super().do_GET()

    def do_POST(self):
        if self.path == '/map_tile':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            terrain = data.get('terrain')
            filepath = data.get('path')
            
            mapping = {}
            if os.path.exists(MAPPING_FILE):
                try:
                    with open(MAPPING_FILE, "r") as f:
                        mapping = json.load(f)
                except Exception:
                    pass
                    
            mapping[terrain] = filepath
            
            with open(MAPPING_FILE, "w") as f:
                json.dump(mapping, f, indent=4)
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            return

if __name__ == '__main__':
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, TileMapperHandler)
    print(f"Tile Mapper Server running at http://localhost:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
