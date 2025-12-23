import os
from pathlib import Path
import yaml
import shutil
from ultralytics.utils.downloads import download
from ultralytics.utils import ASSETS_URL, TQDM
from PIL import Image

def visdrone2yolo(dir, split, source_name=None):
    """Convert VisDrone annotations to YOLO format."""
    source_dir = dir / (source_name or f"VisDrone2019-DET-{split}")
    images_dir = dir / "images" / split
    labels_dir = dir / "labels" / split
    
    # Create directories
    labels_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    # Move images
    source_images = source_dir / "images"
    if source_images.exists():
        print(f"Moving images from {source_images}...")
        for img in source_images.glob("*.jpg"):
            target = images_dir / img.name
            if not target.exists():
                img.rename(target)

    # Convert annotations
    print(f"Converting annotations for {split}...")
    annotations_dir = source_dir / "annotations"
    if annotations_dir.exists():
        for f in TQDM(list(annotations_dir.glob("*.txt")), desc=f"Converting {split}"):
            img_path = images_dir / f.with_suffix(".jpg").name
            if not img_path.exists(): continue
            
            try:
                # Open image to get dimensions
                with Image.open(img_path) as im:
                    w_img, h_img = im.size
            except: continue
            
            dw, dh = 1.0 / w_img, 1.0 / h_img
            lines = []
            
            with open(f, encoding="utf-8") as file:
                for row in [x.split(",") for x in file.read().strip().splitlines()]:
                    if len(row) > 5 and row[4] != "0":  # Skip ignored regions
                        x, y, w, h = map(int, row[:4])
                        cls = int(row[5]) - 1
                        if 0 <= cls <= 9:
                            # YOLO Format: class x_center y_center width height
                            xc, yc = (x + w / 2) * dw, (y + h / 2) * dh
                            wn, hn = w * dw, h * dh
                            lines.append(f"{cls} {xc:.6f} {yc:.6f} {wn:.6f} {hn:.6f}\n")
                            
            # Write label file
            (labels_dir / f.name).write_text("".join(lines), encoding="utf-8")

def main():
    # 1. Setup Absolute Paths
    current_dir = Path(os.getcwd())
    dataset_root = current_dir / "datasets" / "VisDrone"
    dataset_root.mkdir(parents=True, exist_ok=True)
    
    print(f"Dataset will be stored in: {dataset_root}")

    # 2. Download Data
    urls = [
        f"{ASSETS_URL}/VisDrone2019-DET-train.zip",
        f"{ASSETS_URL}/VisDrone2019-DET-val.zip",
        f"{ASSETS_URL}/VisDrone2019-DET-test-dev.zip"
    ]
    # Check if already downloaded to avoid re-downloading
    if not (dataset_root / "VisDrone2019-DET-train.zip").exists():
        print("Downloading dataset (this may take a while)...")
        download(urls, dir=dataset_root, threads=4)
    else:
        print("Zips found, skipping download.")

    # 3. Convert Data
    splits = {
        "VisDrone2019-DET-train": "train", 
        "VisDrone2019-DET-val": "val", 
        "VisDrone2019-DET-test-dev": "test"
    }
    
    for folder, split in splits.items():
        if (dataset_root / folder).exists() or (dataset_root / f"{folder}.zip").exists():
            # Unzip if needed (Ultralytics download handles unzip usually, but we ensure structure)
            visdrone2yolo(dataset_root, split, folder)

    # 4. Generate Correct VisDrone.yaml
    yaml_content = {
        'path': str(dataset_root.absolute()), # ABSOLUTE PATH to fix your error
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'names': {
            0: 'pedestrian', 1: 'people', 2: 'bicycle', 3: 'car', 4: 'van',
            5: 'truck', 6: 'tricycle', 7: 'awning-tricycle', 8: 'bus', 9: 'motor'
        }
    }
    
    with open('VisDrone.yaml', 'w') as f:
        yaml.dump(yaml_content, f)
    
    print("\n✅ Success! Data is ready and VisDrone.yaml has been updated.")

if __name__ == "__main__":
    main()
