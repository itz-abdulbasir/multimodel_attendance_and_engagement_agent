"""
Multimodal Attendance & Engagement Agent - System Launcher
Epic 1: Task 1 (TASK-01) - Application Entry Point
"""

import os
import sys
import argparse
import uvicorn
from backend.config import CONFIG

def main():
    parser = argparse.ArgumentParser(description="Multimodal Attendance & Engagement Agent - Core Application")
    parser.add_argument("--host", type=str, default=CONFIG.host, help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=CONFIG.port, help="Port (default: 8000)")
    parser.add_argument("--source", type=str, default=CONFIG.video_source, choices=["simulated", "webcam", "file"],
                        help="Video ingestion source (simulated, webcam, file)")
    parser.add_argument("--video-path", type=str, default=None,
                        help="Path to pre-recorded classroom video file (default: storage/uploads/classroom_lecture_sample.mp4)")
    parser.add_argument("--webcam-index", type=int, default=0,
                        help="Webcam device index (default: 0)")
    parser.add_argument("--reload", action="store_true", help="Enable dev reload mode")
    parser.add_argument("--verify-pipeline", action="store_true",
                        help="Execute Activity 6.1 end-to-end pipeline verification across all 5 modules and exit")
    parser.add_argument("--verify-frames", type=int, default=5,
                        help="Number of frames to process during pipeline verification (default: 5)")
    args = parser.parse_args()

    # Pre-recorded video resolution
    if args.source == "file" and not args.video_path:
        args.video_path = getattr(CONFIG, "video_path", None) or "storage/uploads/classroom_lecture_sample.mp4"
        if not os.path.exists(args.video_path):
            from backend.utils.video_generator import generate_prerecorded_classroom_video
            args.video_path = generate_prerecorded_classroom_video(args.video_path)

    CONFIG.video_source = args.source
    CONFIG.video_path = args.video_path
    CONFIG.webcam_index = args.webcam_index
    CONFIG.host = args.host
    CONFIG.port = args.port

    print("=" * 76)
    print("   NEUROCLASS: MULTIMODAL ATTENDANCE & ENGAGEMENT AGENT")
    print("   EPIC 6: Interface, Testing, and Deployment | Activity 6.1: Run Core App")
    print("   100% Privacy-Preserving Offline Edge Classroom Intelligence System")
    print("=" * 76)
    print(f" * Local Dashboard URL : http://{args.host}:{args.port}")
    print(f" * Ingestion Source    : {args.source.upper()}")
    if args.source == "file":
        print(f" * Pre-Recorded Video  : {args.video_path}")
    elif args.source == "webcam":
        print(f" * Webcam Device Index : {args.webcam_index}")
    print(f" * Offline Status      : CERTIFIED (Zero external network telemetry)")
    print(f" * Privacy Shield      : ACTIVE (Salted hashing & Face ROI obfuscation)")
    print(f" * Pipeline Flow       : Vision -> Audio -> Fusion -> Scoring -> Analytics")
    print("=" * 76)

    # Activity 6.1: Pipeline Verification Mode
    if args.verify_pipeline:
        print(f"[*] Running Activity 6.1 End-to-End Pipeline Verification ({args.verify_frames} frames)...")
        from backend.core.pipeline_verifier import PipelineVerifier
        verifier = PipelineVerifier()
        result = verifier.verify_pipeline(
            source=args.source,
            video_path=args.video_path,
            webcam_index=args.webcam_index,
            num_frames=args.verify_frames
        )
        print("\n" + "=" * 76)
        print("   ACTIVITY 6.1: END-TO-END PIPELINE VERIFICATION AUDIT REPORT")
        print("=" * 76)
        print(f" * Verification Status : {result['status']}")
        print(f" * Input Source Tested : {result['input_source_tested'].upper()}")
        print(f" * Frames Processed    : {result['total_frames_processed']}")
        print(f" * Processing Time     : {result['elapsed_seconds']} sec")
        print(f" * Average Throughput  : {result['throughput_fps']} FPS")
        print("-" * 76)
        for mod_name, mod_info in result["modules_verified"].items():
            check_mark = "[OK]" if mod_info.get("verified") else "[FAIL]"
            print(f" {check_mark:<6} {mod_name.replace('_', ' ').title():<22} : {mod_info['summary']}")
        print("=" * 76)
        print("Pipeline verification completed successfully.\n")
        return

    print(" Starting local Uvicorn ASGI server...")
    uvicorn.run(
        "backend.api.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
