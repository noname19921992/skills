"""Create a PNG contact sheet from explicitly selected review frames using FFmpeg."""

import argparse
import math
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
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=480)
    parser.add_argument("--max-frames", type=int, default=24)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("FFmpeg is required; run doctor first")
    if args.columns < 1 or args.thumb_width < 64 or args.max_frames < 1:
        raise SystemExit("Invalid contact-sheet dimensions")
    source = Path(args.input_dir).resolve()
    images = sorted(source.glob("review_*.png"))
    if not images:
        raise SystemExit("No review_*.png files found")
    if len(images) > args.max_frames:
        last = len(images) - 1
        indexes = sorted({round(index * last / (args.max_frames - 1))
                          for index in range(args.max_frames)}) if args.max_frames > 1 else [0]
        images = [images[index] for index in indexes]
    rows = math.ceil(len(images) / args.columns)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False)
    list_path = Path(handle.name)
    try:
        with handle:
            for image in images:
                handle.write("file '" + concat_escape(image) + "'\n")
                handle.write("duration 0.04\n")
            handle.write("file '" + concat_escape(images[-1]) + "'\n")
        filter_value = (
            f"scale={args.thumb_width}:-2,"
            f"tile={args.columns}x{rows}:nb_frames={len(images)}:padding=8:margin=8:color=black"
        )
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-vf", filter_value, "-frames:v", "1", str(output),
        ], check=True)
        if not output.is_file() or output.stat().st_size == 0:
            raise SystemExit("FFmpeg completed without creating a contact sheet")
    finally:
        list_path.unlink(missing_ok=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
