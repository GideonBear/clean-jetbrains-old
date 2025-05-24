import re
import subprocess
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from shutil import rmtree

from packaging.version import Version

REGEX = re.compile(r"([a-zA-Z]+)([0-9\.]+)")


def clear(args: Namespace, dir: Path) -> None:
    tools: defaultdict[str, list[tuple[Version, Path]]] = defaultdict(list)
    for item in dir.iterdir():
        match = REGEX.match(item.name)
        if match is None:
            continue
        tool, version = match.groups()
        tools[tool].append((Version(version), item))
    for _tool, versions in tools.items():
        if len(versions) <= 1:
            continue
        keep = max(x[0] for x in versions)
        for (version, item) in versions:
            if version == keep:
                continue
            modified_time = datetime.fromtimestamp(item.stat().st_mtime)
            modified_ago = datetime.now() - modified_time
            if modified_ago < timedelta(days=30):
                continue
            print(f"Removing {item}")
            remove(args, item)


def remove(args: Namespace, item: Path) -> None:
    if args.remove_mode == "rm":
        rmtree(item)
    elif args.remove_mode == "trash":
        subprocess.run(["trash", item], check=True)
    else:
        raise AssertionError("Unreachable")


def parse_args() -> Namespace:
    parser = ArgumentParser()

    remove_mode_group = parser.add_mutually_exclusive_group()
    remove_mode_group.add_argument(
        "-r",
        "--rm",
        dest="remove_mode",
        action="store_const",
        const="rm",
        default="rm",
        help="Remove files permanently (default)",
    )
    remove_mode_group.add_argument(
        "-t",
        "--trash",
        dest="remove_mode",
        action="store_const",
        const="trash",
        help="Move files to trash using trash-cli",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    clear(args, Path.home() / ".cache/JetBrains")
    clear(args, Path.home() / ".local/share/JetBrains")
    clear(args, Path.home() / ".config/JetBrains")
