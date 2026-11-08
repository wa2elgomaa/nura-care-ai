#!/usr/bin/env python3
"""
Prepare Distress Detection Dataset from ToddlerActions

Creates a binary classification dataset:
- Distress (Class 1): Crying, Yawning (tired/upset)
- Non-Distress (Class 0): Smiling, Eating, Drinking, Playing

Usage:
    python training/prepare_distress_dataset.py
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm

# Configuration
SOURCE_DIR = Path("tests/data/ToddlerActions")
TARGET_DIR = Path("datasets/distress_binary")

# Class mapping
DISTRESS_CLASSES = [
    "Toddler crying",
    "Toddler yawning",  # Can indicate tiredness/distress
]

NON_DISTRESS_CLASSES = [
    "Toddler smiling",
    "Toddler eating",
    "Toddler drinking",
    "Toddler palying stacking ring",  # Note: typo in original dataset
    "Toddler playing swing",
    "Toddler sleeping",  # Peaceful state
]

# Classes to exclude (safety hazards handled separately)
EXCLUDE_CLASSES = [
    "Toddler with knife",
    "Toddler on staircase",
    "Toddler in W-sitting",  # Posture, not emotion
]


def prepare_dataset():
    """Prepare binary distress detection dataset."""

    print("=" * 60)
    print("Preparing Distress Detection Dataset")
    print("=" * 60)

    # Create target directories
    for split in ["train", "valid", "test"]:
        for label in ["distress", "non_distress"]:
            target_path = TARGET_DIR / split / label
            target_path.mkdir(parents=True, exist_ok=True)

    stats = {
        "train": {"distress": 0, "non_distress": 0},
        "valid": {"distress": 0, "non_distress": 0},
        "test": {"distress": 0, "non_distress": 0},
    }

    # Process each split
    for split in ["train", "valid", "test"]:
        source_split = SOURCE_DIR / split

        if not source_split.exists():
            print(f"⚠ Warning: {split} split not found, skipping...")
            continue

        print(f"\n📂 Processing {split} split...")

        # Get all class directories
        class_dirs = [d for d in source_split.iterdir() if d.is_dir()]

        for class_dir in tqdm(class_dirs, desc=f"  {split}"):
            class_name = class_dir.name

            # Determine target label
            if class_name in DISTRESS_CLASSES:
                target_label = "distress"
            elif class_name in NON_DISTRESS_CLASSES:
                target_label = "non_distress"
            elif class_name in EXCLUDE_CLASSES:
                continue  # Skip excluded classes
            else:
                print(f"  ⚠ Unknown class: {class_name}, skipping...")
                continue

            # Copy images
            target_class_dir = TARGET_DIR / split / target_label
            image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))

            for img_file in image_files:
                # Create unique filename to avoid collisions
                new_name = f"{class_name.replace(' ', '_')}_{img_file.name}"
                target_file = target_class_dir / new_name

                # Copy file
                shutil.copy2(img_file, target_file)
                stats[split][target_label] += 1

    # Print statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)

    total_distress = 0
    total_non_distress = 0

    for split in ["train", "valid", "test"]:
        distress = stats[split]["distress"]
        non_distress = stats[split]["non_distress"]
        total = distress + non_distress

        total_distress += distress
        total_non_distress += non_distress

        print(f"\n{split.upper()}:")
        print(f"  Distress:     {distress:5d} images")
        print(f"  Non-Distress: {non_distress:5d} images")
        print(f"  Total:        {total:5d} images")

        if total > 0:
            ratio = (distress / total) * 100
            print(f"  Balance:      {ratio:.1f}% distress")

    print(f"\nGRAND TOTAL:")
    print(f"  Distress:     {total_distress:5d} images")
    print(f"  Non-Distress: {total_non_distress:5d} images")
    print(f"  Total:        {total_distress + total_non_distress:5d} images")

    # Class balance check
    if total_distress + total_non_distress > 0:
        balance = (total_distress / (total_distress + total_non_distress)) * 100
        print(f"\nOverall Balance: {balance:.1f}% distress, {100-balance:.1f}% non-distress")

        if balance < 30 or balance > 70:
            print(f"⚠ Warning: Imbalanced dataset ({balance:.1f}% distress)")
            print(f"  Consider using class_weight in training")

    print(f"\n✅ Dataset prepared at: {TARGET_DIR}")
    print("=" * 60)

    # Save metadata
    metadata_file = TARGET_DIR / "dataset_info.txt"
    with open(metadata_file, "w") as f:
        f.write("Distress Detection Binary Dataset\n")
        f.write("=" * 60 + "\n\n")
        f.write("Source: ToddlerActions (Roboflow Universe)\n")
        f.write("License: CC BY 4.0\n\n")
        f.write("Classes:\n")
        f.write("  Distress (1):\n")
        for cls in DISTRESS_CLASSES:
            f.write(f"    - {cls}\n")
        f.write("\n  Non-Distress (0):\n")
        for cls in NON_DISTRESS_CLASSES:
            f.write(f"    - {cls}\n")
        f.write(f"\nTotal Images: {total_distress + total_non_distress}\n")
        f.write(f"  Distress: {total_distress}\n")
        f.write(f"  Non-Distress: {total_non_distress}\n")

    return stats


if __name__ == "__main__":
    prepare_dataset()
