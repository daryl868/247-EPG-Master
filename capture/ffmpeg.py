from pathlib import Path
import subprocess

def capture_frame(stream_url: str, output_path: Path, second: int = 5, timeout: int = 60) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", stream_url,
        "-t", str(second),
        "-frames:v", "1",
        "-update", "1",
        str(output_path)
    ]

    subprocess.run(cmd, check=True, timeout=timeout)
