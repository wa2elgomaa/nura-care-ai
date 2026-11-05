#!/usr/bin/env python3
"""
Video Analysis Script for NURA Childcare AI
Analyzes video files frame-by-frame using the hybrid detection system
"""
import cv2
import base64
import requests
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
VLM_API_URL = "http://localhost:8001/analyze/hybrid"
FRAME_SAMPLE_RATE = 30  # Analyze every Nth frame (30 frames = ~1 second at 30fps)
TIMEOUT = 120  # API timeout in seconds
DEFAULT_OUTPUT_DIR = "test-results"

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_header(text):
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")


def print_violation(frame_num, timestamp, result):
    """Print violation details"""
    print(f"\n{RED}⚠️  VIOLATION DETECTED{NC}")
    print(f"  Frame: {frame_num}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Type: {result['violation_type']}")
    print(f"  Severity: {result['severity']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Source: {result['source']}")
    print(f"  Details: {result['details']}")


def analyze_frame(frame, frame_num):
    """Analyze a single frame"""
    # Encode frame to JPEG
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        return None
    
    # Convert to base64
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Send to API
    try:
        response = requests.post(
            VLM_API_URL,
            json={
                'image_base64': image_base64,
                'camera_id': f'video_frame_{frame_num}'
            },
            timeout=TIMEOUT
        )
        
        if response.ok:
            return response.json()
        else:
            print(f"{RED}API error on frame {frame_num}: {response.status_code}{NC}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"{YELLOW}Timeout on frame {frame_num}{NC}")
        return None
    except Exception as e:
        print(f"{RED}Error on frame {frame_num}: {e}{NC}")
        return None


def format_timestamp(frame_num, fps):
    """Convert frame number to timestamp"""
    seconds = frame_num / fps
    return str(timedelta(seconds=int(seconds)))


def analyze_video(video_path, output_json=None):
    """Analyze entire video"""
    print_header(f"Video Analysis: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"{RED}Error: Could not open video file{NC}")
        return
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video Properties:")
    print(f"  Duration: {timedelta(seconds=int(duration))}")
    print(f"  Total Frames: {total_frames}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Sampling Rate: Every {FRAME_SAMPLE_RATE} frames (~{FRAME_SAMPLE_RATE/fps:.1f}s)")
    
    frames_to_analyze = total_frames // FRAME_SAMPLE_RATE
    print(f"\n{YELLOW}Will analyze ~{frames_to_analyze} frames{NC}")
    
    # Analysis results
    violations = []
    analyzed_count = 0
    violation_count = 0
    start_time = time.time()
    
    # Progress tracking
    frame_num = 0
    
    print(f"\n{BLUE}Starting analysis...{NC}\n")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Sample frames
        if frame_num % FRAME_SAMPLE_RATE == 0:
            timestamp = format_timestamp(frame_num, fps)
            
            # Show progress
            progress = (frame_num / total_frames) * 100
            print(f"[{progress:5.1f}%] Frame {frame_num}/{total_frames} ({timestamp})...", end=' ')
            
            # Analyze frame
            result = analyze_frame(frame, frame_num)
            
            if result:
                analyzed_count += 1
                processing_time = result.get('processing_time_ms', 0)
                print(f"{processing_time:.0f}ms", end='')
                
                if result['violation_detected']:
                    violation_count += 1
                    violations.append({
                        'frame': frame_num,
                        'timestamp': timestamp,
                        'result': result
                    })
                    print(f" {RED}VIOLATION{NC}")
                    print_violation(frame_num, timestamp, result)
                else:
                    print(f" {GREEN}OK{NC}")
            else:
                print(f"{RED}FAILED{NC}")
        
        frame_num += 1
    
    cap.release()
    elapsed = time.time() - start_time
    
    # Summary
    print_header("Analysis Complete")
    print(f"Frames Analyzed: {analyzed_count}/{frames_to_analyze}")
    print(f"Violations Found: {violation_count}")
    print(f"Total Time: {timedelta(seconds=int(elapsed))}")
    print(f"Avg Time/Frame: {elapsed/analyzed_count:.2f}s" if analyzed_count > 0 else "N/A")
    
    if violations:
        print(f"\n{RED}Violation Summary:{NC}")
        for v in violations:
            r = v['result']
            print(f"  {v['timestamp']} - {r['violation_type']} ({r['confidence']:.0%})")
    else:
        print(f"\n{GREEN}✓ No violations detected{NC}")
    
    # Save results
    if output_json:
        # Ensure output directory exists
        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            'video_path': video_path,
            'analyzed_at': datetime.now().isoformat(),
            'video_properties': {
                'duration_seconds': duration,
                'total_frames': total_frames,
                'fps': fps,
                'resolution': f"{width}x{height}"
            },
            'analysis_settings': {
                'frame_sample_rate': FRAME_SAMPLE_RATE,
                'frames_analyzed': analyzed_count
            },
            'summary': {
                'violations_found': violation_count,
                'elapsed_seconds': elapsed
            },
            'violations': violations
        }
        
        with open(output_json, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n{GREEN}Results saved to: {output_json}{NC}")


def main():
    if len(sys.argv) < 2:
        print(f"{RED}Usage: python3 tools/testing/analyze-video.py <video_file> [output.json]{NC}")
        print(f"\nExamples:")
        print(f"  python3 tools/testing/analyze-video.py tests/data/Videos/FightingA_Part1/Fighting013_x264A.mp4")
        print(f"  python3 tools/testing/analyze-video.py tests/data/Videos/FightingA_Part1/Fighting013_x264A.mp4 test-results/classroom.json")
        print(f"\nDefault output directory: {DEFAULT_OUTPUT_DIR}/")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Auto-generate output path in test-results if not specified
    if len(sys.argv) > 2:
        output_json = sys.argv[2]
    else:
        video_name = Path(video_path).stem
        output_json = f"{DEFAULT_OUTPUT_DIR}/video_{video_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"{BLUE}Auto-saving results to: {output_json}{NC}\n")
    
    if not Path(video_path).exists():
        print(f"{RED}Error: Video file not found: {video_path}{NC}")
        sys.exit(1)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if not response.ok:
            print(f"{RED}Error: VLM service not responding{NC}")
            print(f"{YELLOW}Start with: ./start.sh{NC}")
            sys.exit(1)
    except:
        print(f"{RED}Error: Cannot connect to VLM service{NC}")
        print(f"{YELLOW}Start with: ./start.sh{NC}")
        sys.exit(1)
    
    analyze_video(video_path, output_json)


if __name__ == '__main__':
    main()
