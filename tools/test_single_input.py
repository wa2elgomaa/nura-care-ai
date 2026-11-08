#!/usr/bin/env python3
"""
Test Single Video/Image Through Complete Pipeline

Tests a specific video or image through the entire Nura AI pipeline:
1. Frame extraction (for video)
2. Person detection simulation
3. VLM Service AI analysis (Fast-path + VLM validation)
4. Alert generation (if violation detected)
5. Shows complete analysis results

Perfect for demos and testing specific scenarios!

Usage:
    # Test with video
    python tools/test_single_input.py --video tests/videos/classroom_6.mp4

    # Test with image
    python tools/test_single_input.py --image path/to/test_image.jpg

    # Test with specific camera name
    python tools/test_single_input.py --video tests/videos/classroom_6.mp4 --camera demo_classroom

    # Save detailed report
    python tools/test_single_input.py --video tests/videos/classroom_6.mp4 --output-report demo_results.json
"""

import argparse
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
import requests
import cv2
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import print as rprint

console = Console()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test single video/image through complete AI pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Test a video:
    python tools/test_single_input.py --video tests/videos/classroom_6.mp4

  Test an image:
    python tools/test_single_input.py --image tests/images/test_frame.jpg

  Analyze specific frame from video:
    python tools/test_single_input.py --video tests/videos/classroom_6.mp4 --frame-number 150

  Save detailed results:
    python tools/test_single_input.py --video tests/videos/classroom_6.mp4 --output-report results.json
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--video", type=str, help="Path to video file")
    input_group.add_argument("--image", type=str, help="Path to image file")

    # Analysis options
    parser.add_argument("--camera", type=str, default="demo_camera",
                       help="Camera ID to use in analysis (default: demo_camera)")
    parser.add_argument("--frame-number", type=int,
                       help="Specific frame number to analyze (for video)")
    parser.add_argument("--sample-rate", type=int, default=30,
                       help="Analyze every Nth frame (for video, default: 30)")
    parser.add_argument("--max-frames", type=int, default=5,
                       help="Maximum frames to analyze (for video, default: 5)")

    # Service configuration
    parser.add_argument("--vlm-url", type=str, default="http://localhost:8001",
                       help="VLM Service URL (default: http://localhost:8001)")
    parser.add_argument("--alert-url", type=str, default="http://localhost:3011",
                       help="Alert Service URL (default: http://localhost:3011)")

    # Output options
    parser.add_argument("--output-report", type=str,
                       help="Save detailed JSON report to file")
    parser.add_argument("--save-annotated", type=str,
                       help="Save annotated frame/video to file")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed debug information")

    return parser.parse_args()


def load_image(image_path):
    """Load image from file."""
    img = cv2.imread(str(image_path))
    if img is None:
        console.print(f"[red]✗ Failed to load image: {image_path}[/red]")
        sys.exit(1)
    return img


def extract_frames_from_video(video_path, frame_number=None, sample_rate=30, max_frames=5):
    """Extract frames from video."""
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        console.print(f"[red]✗ Failed to open video: {video_path}[/red]")
        sys.exit(1)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    duration = total_frames / fps if fps > 0 else 0

    console.print(f"[cyan]Video Info:[/cyan]")
    console.print(f"  Total frames: {total_frames}")
    console.print(f"  FPS: {fps}")
    console.print(f"  Duration: {duration:.2f}s")

    frames = []

    if frame_number is not None:
        # Extract specific frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if ret:
            frames.append((frame_number, frame))
            console.print(f"[green]✓ Extracted frame #{frame_number}[/green]")
        else:
            console.print(f"[red]✗ Failed to extract frame #{frame_number}[/red]")
    else:
        # Sample frames
        frame_idx = 0
        frames_extracted = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Extracting frames...", total=max_frames)

            while frames_extracted < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_rate == 0:
                    frames.append((frame_idx, frame))
                    frames_extracted += 1
                    progress.update(task, advance=1)

                frame_idx += 1

        console.print(f"[green]✓ Extracted {len(frames)} frames[/green]")

    cap.release()
    return frames, {"total_frames": total_frames, "fps": fps, "duration": duration}


def image_to_base64(image):
    """Convert OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')


def analyze_frame_with_vlm(frame, camera_id, vlm_url, verbose=False):
    """Send frame to VLM service for AI analysis."""

    # Convert to base64
    image_base64 = image_to_base64(frame)

    # Prepare request
    payload = {
        "image_base64": image_base64,
        "camera_id": camera_id
    }

    if verbose:
        console.print(f"[dim]Sending request to {vlm_url}/analyze/hybrid...[/dim]")

    try:
        # Send to VLM service
        response = requests.post(
            f"{vlm_url}/analyze/hybrid",
            json=payload,
            timeout=120  # 2 minutes for first request (model loading)
        )

        response.raise_for_status()
        result = response.json()

        return result

    except requests.exceptions.Timeout:
        return {"error": "VLM service timeout (may be loading models on first request)"}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to VLM service at {vlm_url}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from VLM service"}


def display_analysis_results(result, frame_number=None):
    """Display AI analysis results in a nice format."""

    console.print()

    if "error" in result:
        console.print(Panel(
            f"[red]✗ Error: {result['error']}[/red]",
            title="❌ Analysis Failed",
            border_style="red"
        ))
        return

    # Create results table
    table = Table(title=f"🤖 AI Analysis Results{f' (Frame #{frame_number})' if frame_number else ''}")

    table.add_column("Detector", style="cyan", no_wrap=True)
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Detected", justify="center")
    table.add_column("Threshold", justify="right", style="dim")

    # Fast-path detector results
    if "fast_path_scores" in result:
        scores = result["fast_path_scores"]

        detectors = [
            ("Violence", scores.get("violence", 0), scores.get("violence_detected", False)),
            ("Distress", scores.get("distress", 0), scores.get("distress_detected", False)),
            ("Body Language", scores.get("body_language", 0), scores.get("intimidation", False)),
            ("Supervision", scores.get("supervision", 0), scores.get("supervision_violation", False)),
        ]

        for name, score, detected in detectors:
            detected_icon = "🔴 YES" if detected else "✅ NO"
            detected_style = "red bold" if detected else "green"

            table.add_row(
                name,
                f"{score:.3f}",
                f"[{detected_style}]{detected_icon}[/{detected_style}]",
                "varies"
            )

    console.print(table)

    # Overall decision
    violation_detected = result.get("violation_detected", False)

    if violation_detected:
        violation_type = result.get("violation_type", "unknown")
        severity = result.get("severity", "unknown")
        confidence = result.get("confidence", 0)

        console.print(Panel(
            f"[red bold]🚨 VIOLATION DETECTED[/red bold]\n\n"
            f"[yellow]Type:[/yellow] {violation_type}\n"
            f"[yellow]Severity:[/yellow] {severity}\n"
            f"[yellow]Confidence:[/yellow] {confidence:.2%}",
            title="⚠️  Alert Generated",
            border_style="red"
        ))

        # VLM reasoning (if available)
        if "vlm_reasoning" in result:
            console.print(Panel(
                result["vlm_reasoning"],
                title="🧠 VLM Analysis",
                border_style="blue"
            ))
    else:
        console.print(Panel(
            "[green]✓ No violations detected[/green]\n"
            "[dim]Scene appears safe[/dim]",
            title="✅ Safe Scene",
            border_style="green"
        ))

    # Temporal detection (if available)
    if "temporal" in result:
        temporal = result["temporal"]
        console.print()
        console.print(f"[cyan]Temporal Analysis:[/cyan] {temporal.get('score', 0):.3f} "
                     f"({'Violent' if temporal.get('detected', False) else 'Normal'})")

    # Person tracking (if available)
    if "persons" in result:
        persons = result["persons"]
        console.print(f"[cyan]Persons Detected:[/cyan] {len(persons)}")
        for person in persons:
            person_id = person.get("id", "unknown")
            name = person.get("name", "Unknown")
            console.print(f"  - Person {person_id}: {name}")


def save_annotated_frame(frame, result, output_path):
    """Save frame with analysis annotations."""
    annotated = frame.copy()

    # Add text overlay
    violation = result.get("violation_detected", False)

    if violation:
        text = f"VIOLATION: {result.get('violation_type', 'unknown')}"
        color = (0, 0, 255)  # Red
    else:
        text = "SAFE - No violations"
        color = (0, 255, 0)  # Green

    # Add background rectangle for text
    cv2.rectangle(annotated, (10, 10), (600, 60), (0, 0, 0), -1)
    cv2.putText(annotated, text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Add detector scores
    if "fast_path_scores" in result:
        scores = result["fast_path_scores"]
        y_pos = 100

        for name, key in [("Violence", "violence"), ("Distress", "distress"),
                          ("Body Lang", "body_language"), ("Supervision", "supervision")]:
            score = scores.get(key, 0)
            detected = scores.get(f"{key}_detected", False) or \
                      scores.get("intimidation", False) if key == "body_language" else \
                      scores.get("supervision_violation", False) if key == "supervision" else False

            text = f"{name}: {score:.2f} {'[ALERT]' if detected else ''}"
            color = (0, 0, 255) if detected else (255, 255, 255)

            cv2.rectangle(annotated, (10, y_pos - 25), (300, y_pos + 5), (0, 0, 0), -1)
            cv2.putText(annotated, text, (15, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_pos += 35

    cv2.imwrite(str(output_path), annotated)
    console.print(f"[green]✓ Annotated frame saved: {output_path}[/green]")


def save_report(results, output_path, video_info=None):
    """Save detailed JSON report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "video_info": video_info,
        "total_frames_analyzed": len(results),
        "violations_detected": sum(1 for r in results if r.get("result", {}).get("violation_detected", False)),
        "frames": results
    }

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    console.print(f"[green]✓ Report saved: {output_path}[/green]")


def main():
    """Main function."""
    args = parse_args()

    console.print(Panel.fit(
        "[bold cyan]🧪 NURA AI Pipeline Tester[/bold cyan]\n"
        "Test single video/image through complete pipeline",
        border_style="cyan"
    ))

    # Check VLM service
    console.print()
    console.print("[yellow]Checking VLM service...[/yellow]")
    try:
        response = requests.get(f"{args.vlm_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            console.print(f"[green]✓ VLM Service is healthy[/green]")
            console.print(f"  Model: {health.get('vlm_model', 'unknown')}")
            console.print(f"  Model loaded: {health.get('model_loaded', False)}")
        else:
            console.print(f"[red]✗ VLM Service returned status {response.status_code}[/red]")
    except requests.exceptions.ConnectionError:
        console.print(f"[red]✗ Cannot connect to VLM service at {args.vlm_url}[/red]")
        console.print(f"[yellow]  Start with: ./runner/run_vlm_service.sh[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Health check failed: {e}[/red]")
        sys.exit(1)

    # Load input
    console.print()
    console.print("[cyan]═══════════════════════════════════════════════[/cyan]")
    console.print("[cyan]Loading Input[/cyan]")
    console.print("[cyan]═══════════════════════════════════════════════[/cyan]")

    video_info = None

    if args.video:
        video_path = Path(args.video)
        if not video_path.exists():
            console.print(f"[red]✗ Video not found: {video_path}[/red]")
            sys.exit(1)

        console.print(f"[cyan]Video:[/cyan] {video_path}")
        frames, video_info = extract_frames_from_video(
            video_path,
            frame_number=args.frame_number,
            sample_rate=args.sample_rate,
            max_frames=args.max_frames
        )
    else:
        image_path = Path(args.image)
        if not image_path.exists():
            console.print(f"[red]✗ Image not found: {image_path}[/red]")
            sys.exit(1)

        console.print(f"[cyan]Image:[/cyan] {image_path}")
        img = load_image(image_path)
        frames = [(0, img)]
        console.print(f"[green]✓ Image loaded ({img.shape[1]}x{img.shape[0]})[/green]")

    # Analyze frames
    console.print()
    console.print("[cyan]═══════════════════════════════════════════════[/cyan]")
    console.print("[cyan]AI Analysis[/cyan]")
    console.print("[cyan]═══════════════════════════════════════════════[/cyan]")

    results = []

    for frame_idx, frame in frames:
        console.print()
        console.print(f"[bold]Analyzing frame #{frame_idx}...[/bold]")

        with console.status("[yellow]Analyzing with AI...[/yellow]", spinner="dots"):
            result = analyze_frame_with_vlm(
                frame,
                args.camera,
                args.vlm_url,
                verbose=args.verbose
            )

        display_analysis_results(result, frame_idx)

        results.append({
            "frame_number": frame_idx,
            "result": result
        })

        # Save annotated frame if requested
        if args.save_annotated and len(frames) == 1:
            save_annotated_frame(frame, result, args.save_annotated)

    # Summary
    console.print()
    console.print("[cyan]═══════════════════════════════════════════════[/cyan]")
    console.print("[cyan]Summary[/cyan]")
    console.print("[cyan]═══════════════════════════════════════════════[/cyan]")

    total_analyzed = len(results)
    total_violations = sum(1 for r in results if r["result"].get("violation_detected", False))

    summary_table = Table(title="📊 Analysis Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", justify="right", style="yellow")

    summary_table.add_row("Frames Analyzed", str(total_analyzed))
    summary_table.add_row("Violations Detected", str(total_violations))
    summary_table.add_row("Safe Frames", str(total_analyzed - total_violations))

    if total_analyzed > 0:
        violation_rate = (total_violations / total_analyzed) * 100
        summary_table.add_row("Violation Rate", f"{violation_rate:.1f}%")

    console.print(summary_table)

    # Save report if requested
    if args.output_report:
        console.print()
        save_report(results, args.output_report, video_info)

    console.print()
    console.print("[green]✓ Analysis complete![/green]")


if __name__ == "__main__":
    main()
