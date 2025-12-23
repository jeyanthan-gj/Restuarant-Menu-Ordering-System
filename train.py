import sys
import os
import torch

# Fix Windows/CUDA Memory Issues
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Ultralytics Imports
import ultralytics.nn.modules as modules
import ultralytics.nn.modules.conv as conv
import ultralytics.nn.modules.block as block
import ultralytics.nn.tasks as tasks
from ultralytics import YOLO

# Import Custom Modules
from yolov8_mpeb_modules import MobileNetBlock, EMA, C2f_EMA, BiFPN_Concat

# Apply Patches
block.GhostBottleneck = MobileNetBlock
modules.GhostBottleneck = MobileNetBlock

block.C3 = C2f_EMA
modules.C3 = C2f_EMA

conv.Concat = BiFPN_Concat
modules.Concat = BiFPN_Concat

if hasattr(tasks, 'GhostBottleneck'): tasks.GhostBottleneck = MobileNetBlock
if hasattr(tasks, 'C3'): tasks.C3 = C2f_EMA
if hasattr(tasks, 'Concat'): tasks.Concat = BiFPN_Concat

if hasattr(tasks, 'block'):
    tasks.block.GhostBottleneck = MobileNetBlock
    tasks.block.C3 = C2f_EMA
if hasattr(tasks, 'conv'):
    tasks.conv.Concat = BiFPN_Concat

def train_main():
    print("Loading Model Configuration...")
    model = YOLO("yolov8_mpeb.yaml")
    
    model.info()
    
    print("\nStarting Training on RTX 2050...")
    
    # RTX 2050 OPTIMIZED SETTINGS
    results = model.train(
        data='VisDrone.yaml',
        epochs=100,
        
        # --- GPU MEMORY SETTINGS (CRITICAL) ---
        batch=2,              # Try 2. If OutOfMemory, change to 1.
        imgsz=640,            # If OutOfMemory, change to 512.
        amp=False,             # Keep True for memory savings. If nan loss/freeze, set False.
        workers=1,            # Windows requires low workers (1 or 0)
        # --------------------------------------
        
        device=0,
        project='runs/train',
        name='yolov8_mpeb_local',
        save=True,
        save_period=5,
        patience=20,
        optimizer='SGD',
        close_mosaic=10,
        verbose=True
    )

if __name__ == "__main__":
    # Required for Windows multiprocessing
    train_main()
