"""Encode sorted review PNG frames into an H.264 preview video using FFmpeg."""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def concat_escape(path):
    return str(path.resolve()).replace("'", "'\\''")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fps", type=float, required=True)
    parser.add_argument("--crf", type=int, default=20)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("FFmpeg is required; run doctor first")
    if args.fps <= 0:
        raise SystemExit("--fps must be positive")
    images = sorted(Path(args.input_dir).resolve().glob("review_*.png"))
    if not images:
        raise SystemExit("No review_*.png files found")
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = 1.0 / args.fps
    handle = tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False)
    list_path = Path(handle.name)
    try:
        with handle:
            for image in images:
                handle.write("file '" + concat_escape(image) + "'\n")
                handle.write("duration %.9f\n" % duration)
            handle.write("file '" + concat_escape(images[-1]) + "'\n")
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-c:v", "libx264", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output),
        ], check=True)
        if not output.is_file() or output.stat().st_size == 0:
            raise SystemExit("FFmpeg completed without creating a preview video")
    finally:
        list_path.unlink(missing_ok=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
