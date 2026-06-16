#!/usr/bin/env python3
"""
Capture images from Gazebo simulation for YOLO training.
Varies the model pose and fill light to generate diverse training data.

Usage:
    python3 capture_dataset.py --count 200 --output ./dataset
"""

import os
import sys
import time
import argparse
import math
import subprocess
from pathlib import Path
from PIL import ImageGrab
import json


def create_dataset_dirs(output_dir):
    """Create dataset directory structure for YOLO."""
    base = Path(output_dir)
    dirs = {
        'train_img': base / 'images' / 'train',
        'val_img': base / 'images' / 'val',
        'test_img': base / 'images' / 'test',
        'train_lbl': base / 'labels' / 'train',
        'val_lbl': base / 'labels' / 'val',
        'test_lbl': base / 'labels' / 'test',
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def capture_screenshot(output_path, delay=0.5):
    """Capture Gazebo window screenshot."""
    try:
        time.sleep(delay)  # brief delay to let Gazebo render
        # Grab entire screen (adjust if Gazebo is windowed; crop if needed)
        img = ImageGrab.grab()
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False


def euler_to_quaternion(roll, pitch, yaw):
    """Convert Euler angles to a quaternion."""
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def set_entity_pose(world_name, entity_name, x, y, z, roll=0.0, pitch=0.0, yaw=0.0):
    """Use Gazebo service to move an entity such as a model or light."""
    qx, qy, qz, qw = euler_to_quaternion(roll, pitch, yaw)
    req = (
        f'name: "{entity_name}" '
        f'position: {{x: {x}, y: {y}, z: {z}}} '
        f'orientation: {{x: {qx}, y: {qy}, z: {qz}, w: {qw}}}'
    )

    try:
        result = subprocess.run(
            [
                "gz", "service",
                "-s", f"/world/{world_name}/set_pose",
                "--reqtype", "gz.msgs.Pose",
                "--reptype", "gz.msgs.Boolean",
                "--timeout", "300",
                "--req", req,
            ],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        if result.returncode != 0:
            stderr = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(stderr or f"failed to move {entity_name}")
    except Exception as exc:
        raise RuntimeError(f"Unable to move {entity_name} in world '{world_name}': {exc}") from exc


def generate_capture_poses(count=200):
    """Generate varied model and light poses for diverse viewpoints and lighting."""
    poses = []
    for i in range(count):
        fraction = i / max(count, 1)
        angle = fraction * math.tau

        model_x = 0.20 * math.cos(angle)
        model_y = 0.20 * math.sin(angle)
        model_z = 0.02 * math.sin(angle * 2.0)
        model_yaw = angle + (math.pi / 2.0)
        model_pitch = 0.12 * math.sin(angle * 1.5)
        model_roll = 0.08 * math.cos(angle * 2.0)

        light_angle = angle + (math.pi / 3.0)
        light_x = 3.0 * math.cos(light_angle)
        light_y = 3.0 * math.sin(light_angle)
        light_z = 2.5 + 0.6 * math.sin(angle * 3.0)

        poses.append(
            {
                'model': {
                    'x': model_x,
                    'y': model_y,
                    'z': model_z,
                    'roll': model_roll,
                    'pitch': model_pitch,
                    'yaw': model_yaw,
                },
                'light': {
                    'x': light_x,
                    'y': light_y,
                    'z': light_z,
                },
            }
        )

    return poses


def main():
    parser = argparse.ArgumentParser(description='Capture YOLO training images from Gazebo')
    parser.add_argument('--count', type=int, default=200, help='Number of images to capture (default: 200)')
    parser.add_argument('--output', type=str, default='./dataset', help='Output dataset directory (default: ./dataset)')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between captures in seconds (default: 0.5)')
    parser.add_argument('--train-val-test', type=str, default='0.7,0.15,0.15', help='Train/val/test split (default: 0.7,0.15,0.15)')
    parser.add_argument('--world-name', type=str, default=os.environ.get('GZ_WORLD_NAME', 'valve_capture_world'), help='Gazebo world name (default: valve_capture_world or $GZ_WORLD_NAME)')
    parser.add_argument('--model-name', type=str, default='stl_visual', help='Model name to move while capturing (default: stl_visual)')
    parser.add_argument('--light-name', type=str, default='valve_fill_light', help='Light name to move while capturing (default: valve_fill_light)')
    
    args = parser.parse_args()
    
    # Parse split ratio
    splits = list(map(float, args.train_val_test.split(',')))
    if len(splits) != 3 or abs(sum(splits) - 1.0) > 1e-6:
        print("Error: train-val-test must sum to 1.0 (e.g., 0.7,0.15,0.15)")
        sys.exit(1)
    
    train_ratio, val_ratio, _ = splits
    
    print(f"Starting image capture: {args.count} images → {args.output}")
    print(f"Split: {train_ratio*100:.0f}% train, {val_ratio*100:.0f}% val, {(1-train_ratio-val_ratio)*100:.0f}% test")
    print("Ensure Gazebo is running in the container and the valve model is loaded!")
    print()
    
    dirs = create_dataset_dirs(args.output)
    capture_poses = generate_capture_poses(args.count)
    
    metadata = {
        'total_images': args.count,
        'train_ratio': train_ratio,
        'val_ratio': val_ratio,
        'captures': []
    }
    
    for i, pose in enumerate(capture_poses, start=1):
        # Determine split
        rand_val = (i / args.count)
        if rand_val < train_ratio:
            split = 'train'
        elif rand_val < train_ratio + val_ratio:
            split = 'val'
        else:
            split = 'test'
        
        # Generate filename
        filename = f"img_{i:04d}.png"
        img_path = dirs[f'{split}_img'] / filename
        
        # Move the model and the fill light to create different angles and lighting
        model = pose['model']
        light = pose['light']
        set_entity_pose(
            args.world_name,
            args.model_name,
            model['x'],
            model['y'],
            model['z'],
            model['roll'],
            model['pitch'],
            model['yaw'],
        )
        set_entity_pose(
            args.world_name,
            args.light_name,
            light['x'],
            light['y'],
            light['z'],
        )
        
        # Capture screenshot
        if capture_screenshot(str(img_path), delay=args.delay):
            print(f"[{i:3d}/{args.count}] Captured {filename} ({split})")
            metadata['captures'].append({
                'filename': filename,
                'split': split,
                'model_pose': model,
                'light_pose': light,
            })
        else:
            print(f"[{i:3d}/{args.count}] Failed to capture {filename}")
        
        time.sleep(args.delay)
    
    # Save metadata
    metadata_path = Path(args.output) / 'metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Captured {len(metadata['captures'])} images to {args.output}")
    print(f"✓ Metadata saved to {metadata_path}")
    print("\nNext steps:")
    print(f"1. Annotate images using LabelImg or Roboflow:")
    print(f"   - Place bounding boxes around your item")
    print(f"   - Export in YOLO format (.txt files)")
    print(f"2. Copy annotated .txt files to {args.output}/labels/[train|val|test]/")
    print(f"3. Create data.yaml (see dataset_config.yaml template)")
    print(f"4. Train: python3 -m yolov5.train --img 640 --batch 16 --epochs 100 --data {args.output}/data.yaml")


if __name__ == '__main__':
    main()
