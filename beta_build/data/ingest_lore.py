import os
import logging

# Assuming this script is run from the project root or SAGA directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from beta_build.data.memory_store import MemoryStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LoreIngester")

def chunk_markdown(content: str) -> List[str]:
    """
    Splits markdown content into semantic chunks based on headers.
    """
    chunks = []
    current_chunk = []
    
    for line in content.split('\n'):
        if line.startswith('#') and current_chunk:
            # We hit a new header, save the old chunk
            chunk_text = '\n'.join(current_chunk).strip()
            if len(chunk_text) > 20: # ignore tiny empty chunks
                chunks.append(chunk_text)
            current_chunk = [line]
        else:
            current_chunk.append(line)
            
    # append the last chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if len(chunk_text) > 20:
            chunks.append(chunk_text)
            
    return chunks

def ingest_lore(lore_dir: str):
    store = MemoryStore()
    
    if not os.path.exists(lore_dir):
        logger.error(f"Lore directory not found: {lore_dir}")
        return
        
    logger.info(f"Starting lore ingestion from {lore_dir}...")
    
    total_chunks = 0
    for filename in os.listdir(lore_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(lore_dir, filename)
            logger.info(f"Processing {filename}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            chunks = chunk_markdown(content)
            for chunk in chunks:
                metadata = {
                    "source": filename,
                    "type": "world_lore"
                }
                store.store_event(chunk, metadata)
                total_chunks += 1
                
    logger.info(f"Ingestion complete! Successfully added {total_chunks} lore chunks to the Vector Database.")

if __name__ == "__main__":
    lore_directory = r"C:\Users\krazy\Desktop\Okasha"
    ingest_lore(lore_directory)
