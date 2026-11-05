#!/usr/bin/env python3
"""
Train MViT V2 for Violence Detection (Phase 3C Alternative)

MViT (Multiscale Vision Transformer) is Meta's state-of-the-art video model.
Performance: Similar to X3D but available in torchvision!

Usage:
    python3 tools/training/train_mvit_detector.py \
        --violent-dir datasets/videos/violence \
        --normal-dir datasets/videos/normal \
        --epochs 20 \
        --output models/mvit_violence.pth
"""
import sys
import argparse
from pathlib import Path
import numpy as np
from tqdm import tqdm
import time

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    from torchvision.models.video import mvit_v2_s, MViT_V2_S_Weights
    from torchvision.transforms import functional as F
    import cv2
    HAS_DEPS = True
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install: pip install torch torchvision opencv-python")
    HAS_DEPS = False


# ANSI colors
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'


class ViolenceDataset(Dataset):
    """Dataset for violence detection videos"""

    def __init__(self, violent_videos, normal_videos, num_frames=16, target_fps=15):
        self.videos = []
        self.labels = []
        self.num_frames = num_frames
        self.target_fps = target_fps

        # Add violent videos (label=1)
        for video in violent_videos:
            self.videos.append(video)
            self.labels.append(1)

        # Add normal videos (label=0)
        for video in normal_videos:
            self.videos.append(video)
            self.labels.append(0)

    def __len__(self):
        return len(self.videos)

    def load_video(self, video_path):
        """Load video and sample frames"""
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            return None

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames < self.num_frames:
            cap.release()
            return None

        # Sample frames uniformly
        frame_indices = np.linspace(0, total_frames - 1, self.num_frames, dtype=int)

        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()

            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize to 224x224
                frame = cv2.resize(frame, (224, 224))
                frames.append(frame)

        cap.release()

        if len(frames) != self.num_frames:
            return None

        return np.array(frames)

    def __getitem__(self, idx):
        video_path = self.videos[idx]
        label = self.labels[idx]

        frames = self.load_video(video_path)

        if frames is None:
            # Fallback: return zeros
            frames = np.zeros((self.num_frames, 224, 224, 3), dtype=np.uint8)

        # Convert to tensor: (T, H, W, C) -> (C, T, H, W)
        frames = torch.from_numpy(frames).permute(3, 0, 1, 2).float()

        # Normalize (ImageNet stats) - need to normalize each frame
        frames = frames / 255.0
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1, 1)
        frames = (frames - mean) / std

        return frames, label


def train_model(violent_dir, normal_dir, epochs=20, batch_size=4, learning_rate=0.0001, output_path='models/mvit_violence.pth'):
    """Train MViT V2 on violence detection"""

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}MViT V2 VIOLENCE DETECTOR TRAINING (Phase 3C){NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    # Find videos
    violent_videos = list(Path(violent_dir).rglob("*.mp4"))[:100]  # Limit for faster training
    normal_videos = list(Path(normal_dir).rglob("*.mp4"))[:100]

    print(f"Dataset:")
    print(f"  Violent videos: {len(violent_videos)}")
    print(f"  Normal videos: {len(normal_videos)}")
    print(f"  Total: {len(violent_videos) + len(normal_videos)}")
    print()

    # Create dataset
    dataset = ViolenceDataset(violent_videos, normal_videos, num_frames=16)

    # Train/val split
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"Splits:")
    print(f"  Training: {len(train_dataset)}")
    print(f"  Validation: {len(val_dataset)}")
    print()

    # Load pre-trained MViT
    print(f"{YELLOW}Loading pre-trained MViT V2...{NC}")
    weights = MViT_V2_S_Weights.DEFAULT
    model = mvit_v2_s(weights=weights)

    # Replace classification head (400 classes -> 2 classes)
    num_features = model.head[1].in_features
    model.head[1] = nn.Linear(num_features, 2)

    print(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print()

    # Training setup
    device = torch.device("cpu")  # Use CPU for now
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3)

    # Training loop
    print(f"{BLUE}Training...{NC}\n")
    best_val_acc = 0.0

    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for frames, labels in pbar:
            frames, labels = frames.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(frames)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

            pbar.set_postfix({'loss': f'{loss.item():.3f}', 'acc': f'{100.*train_correct/train_total:.1f}%'})

        train_acc = 100. * train_correct / train_total

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for frames, labels in val_loader:
                frames, labels = frames.to(device), labels.to(device)
                outputs = model(frames)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = 100. * val_correct / val_total

        print(f"Epoch {epoch+1}/{epochs}: Train Acc: {train_acc:.2f}%, Val Acc: {val_acc:.2f}%")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
            }, output_path)
            print(f"{GREEN}✓ Saved best model (Val Acc: {val_acc:.2f}%){NC}")

        scheduler.step(val_acc)

    print(f"\n{GREEN}Training complete!{NC}")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Train MViT for violence detection')

    parser.add_argument('--violent-dir', required=True, help='Directory with violent videos')
    parser.add_argument('--normal-dir', required=True, help='Directory with normal videos')
    parser.add_argument('--epochs', type=int, default=20, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=4, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.0001, help='Learning rate')
    parser.add_argument('--output', default='models/mvit_violence.pth', help='Output model path')

    args = parser.parse_args()

    if not HAS_DEPS:
        sys.exit(1)

    train_model(
        args.violent_dir,
        args.normal_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_path=args.output
    )


if __name__ == '__main__':
    main()
