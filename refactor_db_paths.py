import os

files = ['app.py', 'ai_director.py', 'engine.py', 'ecology_engine.py', 'master_ingest.py']

for f in files:
    if os.path.exists(f):
        with open(f, 'r') as file:
            content = file.read()
        
        # We replace the hardcoded string with the config reference.
        # But we need to make sure config is imported.
        if 'import config' not in content:
            content = 'import config\n' + content
            
        content = content.replace("'okasha_world.db'", "config.ACTIVE_DB_PATH")
        content = content.replace('"okasha_world.db"', "config.ACTIVE_DB_PATH")
        
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")
