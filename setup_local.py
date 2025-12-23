import os
from pathlib import Path
import yaml
import shutil
from tqdm import tqdm
from PIL import Image

def convert_visdrone_to_yolo(source_root, target_root):
    # Map source folder names to YOLO split names
    splits = {
        "VisDrone2019-DET-train": "train",
        "VisDrone2019-DET-val": "val",
        "VisDrone2019-DET-test-dev": "test"
    }

    target_root = Path(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    for source_folder, split_name in splits.items():
        source_path = Path(source_root) / source_folder
        
        if not source_path.exists():
            print(f"Skipping {split_name} (Folder not found: {source_path})")
            continue

        print(f"\nProcessing {split_name}...")
        
        # Define directories
        target_img_dir = target_root / "images" / split_name
        target_lbl_dir = target_root / "labels" / split_name
        target_img_dir.mkdir(parents=True, exist_ok=True)
        target_lbl_dir.mkdir(parents=True, exist_ok=True)

        # 1. Process Images
        src_imgs = source_path / "images"
        images_map = {} # Cache image sizes
        
        if src_imgs.exists():
            # Copy images
            files = list(src_imgs.glob("*.jpg"))
            for img_file in tqdm(files, desc=f"Copying {split_name} images"):
                shutil.copy2(img_file, target_img_dir / img_file.name)
                # We need image size for label conversion
                with Image.open(img_file) as im:
                    images_map[img_file.name] = im.size

        # 2. Process and Convert Annotations
        src_anns = source_path / "annotations"
        if src_anns.exists():
            ann_files = list(src_anns.glob("*.txt"))
            for ann_file in tqdm(ann_files, desc=f"Converting {split_name} labels"):
                img_name = ann_file.with_suffix(".jpg").name
                
                # We can only convert if we know the image size
                if img_name not in images_map:
                    # Try to find image in target if cache missed
                    if (target_img_dir / img_name).exists():
                         with Image.open(target_img_dir / img_name) as im:
                            w_img, h_img = im.size
                    else:
                        continue # Image missing for this label
                else:
                    w_img, h_img = images_map[img_name]

                dw, dh = 1.0 / w_img, 1.0 / h_img
                yolo_lines = []

                with open(ann_file, 'r') as f:
                    for line in f:
                        data = line.strip().split(',')
                        if len(data) > 5 and data[4] != '0': # Ignore 'ignored' regions
                            # VisDrone: x_min, y_min, w, h, score, class, ...
                            x, y, w, h = map(int, data[:4])
                            cls = int(data[5]) - 1 # VisDrone classes start at 1
                            
                            # Check valid class range (0-9)
                            if 0 <= cls <= 9:
                                # Convert to YOLO: x_center, y_center, w, h (Normalized)
                                xc = (x + w / 2) * dw
                                yc = (y + h / 2) * dh
                                wn = w * dw
                                hn = h * dh
                                yolo_lines.append(f"{cls} {xc:.6f} {yc:.6f} {wn:.6f} {hn:.6f}\n")

                # Save YOLO label file
                if yolo_lines:
                    with open(target_lbl_dir / ann_file.name, 'w') as f:
                        f.writelines(yolo_lines)

    # 3. Create VisDrone.yaml
    yaml_data = {
        'path': str(target_root.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'names': {
            0: 'pedestrian', 1: 'people', 2: 'bicycle', 3: 'car', 4: 'van',
            5: 'truck', 6: 'tricycle', 7: 'awning-tricycle', 8: 'bus', 9: 'motor'
        }
    }
    
    with open('VisDrone.yaml', 'w') as f:
        yaml.dump(yaml_data, f)
    
    print(f"\n✅ Ready! Dataset prepared at: {target_root}")
    print("VisDrone.yaml has been updated.")

if __name__ == "__main__":
    # Source: Where you pasted the folders
    source = "source_data" 
    # Target: Where YOLO will look
    target = "datasets/VisDrone" 
    
    convert_visdrone_to_yolo(source, target)
