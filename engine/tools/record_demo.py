"""Record the real offline demo and render its output for the README.

Run with the engine virtualenv Python. Requires ffmpeg with drawtext;
no model service or additional Python dependency is used.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "assets")
    parser.add_argument("--font", type=Path, default=Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
    args = parser.parse_args()
    if not shutil.which("ffmpeg") or not args.font.is_file():
        parser.error("ffmpeg and a monospace font are required (set --font if needed)")

    result = subprocess.run(
        [str(ROOT / "bin" / "agentcrew"), "demo"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    output = result.stdout
    if "Final decision: ready_for_human_approval" not in output:
        raise RuntimeError("The recorded demo did not complete successfully")
    blocks = output.strip().split("\n\n")
    pages = ["\n\n".join(blocks[:2]), blocks[2], "\n\n".join(blocks[3:])]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "agentcrew-demo.txt").write_text("$ agentcrew demo\n" + output)
    events = [{"version": 2, "width": 96, "height": 22,
               "title": "AgentCrew offline demo; pauses added for readability",
               "duration": 27.0, "env": {"TERM": "xterm-256color"}}]

    with TemporaryDirectory(prefix="agentcrew-recording-") as directory:
        temporary = Path(directory)
        filters = []
        for index, content in enumerate(pages):
            start = index * 9
            lines = ["$ agentcrew demo" if index == 0 else "(continued)", ""]
            for line in content.splitlines():
                lines.extend(textwrap.wrap(line, width=84, subsequent_indent="  ") or [""])
            events.append([start, "o", "\u001b[2J\u001b[H"])
            for row, line in enumerate(lines):
                timestamp = start + row * 0.25
                events.append([timestamp, "o", line + "\r\n"])
                if not line:
                    continue
                path = temporary / f"page{index}-line{row}.txt"
                path.write_text(line)
                color = "0x93c5fd" if row == 0 else "0xe5e7eb"
                if "ready_for_human_approval" in line or "Validation:" in line:
                    color = "0x86efac"
                if "CEO approval" in line:
                    color = "0xfde68a"
                filters.append(
                    "drawtext="
                    f"fontfile='{args.font}':textfile='{path}':expansion=none:"
                    f"fontsize=22:fontcolor={color}:x=44:y={110 + row * 31}:"
                    f"enable='gte(t,{timestamp})*lt(t,{start + 9})'"
                )
        title = temporary / "title.txt"
        title.write_text("AgentCrew | offline scripted demo")
        footer = temporary / "footer.txt"
        footer.write_text("Actual command output. Playback pauses added for readability.")
        filters[:0] = [
            "drawbox=x=0:y=0:w=iw:h=72:color=0x243244:t=fill",
            f"drawtext=fontfile='{args.font}':textfile='{title}':expansion=none:"
            "fontsize=24:fontcolor=white:x=44:y=24",
            f"drawtext=fontfile='{args.font}':textfile='{footer}':expansion=none:"
            "fontsize=18:fontcolor=0x94a3b8:x=44:y=680",
        ]
        filter_path = temporary / "render.filters"
        filter_path.write_text(
            ",".join(filters)
            + ",split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=none[out]"
        )
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
             "-i", "color=c=0x101820:s=1200x720:r=4:d=27",
             "-filter_complex_script", str(filter_path), "-map", "[out]", "-loop", "0",
             str(args.output_dir / "agentcrew-demo.gif")],
            check=True,
        )
    (args.output_dir / "agentcrew-demo.cast").write_text(
        "\n".join(json.dumps(event, separators=(",", ":")) for event in events) + "\n"
    )
    print(f"Recorded and rendered the successful offline demo in {args.output_dir}")


if __name__ == "__main__":
    main()
