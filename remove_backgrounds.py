import os
import glob
from rembg import remove
from PIL import Image

def process_sprites():
    sprites_dir = r"c:\Users\krazy\Desktop\SAGA\assets\sprites"
    output_dir = os.path.join(sprites_dir, "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PNG and JPG files
    images = glob.glob(os.path.join(sprites_dir, "*.png")) + glob.glob(os.path.join(sprites_dir, "*.jpg"))
    print(f"Found {len(images)} images in {sprites_dir}.")
    print(f"Saving outputs to {output_dir}")
    print("Starting background removal...")
    
    for i, img_path in enumerate(images):
        basename = os.path.basename(img_path)
        out_path = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}_nobg.png")
        
        # Skip if already processed to save time
        if os.path.exists(out_path):
            continue
            
        print(f"[{i+1}/{len(images)}] Processing {basename}...")
        try:
            with open(img_path, 'rb') as i_file:
                input_data = i_file.read()
            output_data = remove(input_data)
            with open(out_path, 'wb') as o_file:
                o_file.write(output_data)
        except Exception as e:
            print(f"Error processing {basename}: {e}")
            
    print("Background removal complete! Check the 'processed' folder.")

if __name__ == "__main__":
    process_sprites()
