#!/usr/bin/env python
"""Fetch and sync reveal.js resources.

This script need to run these case.

* After editable install
* Before build package archives
"""

import argparse
import json
import logging
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Dict
from urllib.request import urlretrieve

ROOT_DIR = Path(__file__).parent.parent.absolute()

RULE = {
    "name": "reveal.js",
    "targets": {
        "package/css": "css",
        "package/dist": "dist",
        "package/plugin": "plugin",
        "package/LICENSE": "LICENSE",
    },
    "dest": "sphinx_revealjs/_static/revealjs",
}


def find_package(src: Path, name: str) -> dict:
    """Pick package file URL from package-lock.json."""
    package_lock = json.loads(src.read_text())
    package_name = f"node_modules/{name}"
    deps = [m for n, m in package_lock.get("packages", {}).items() if n == package_name]
    if len(deps) == 0:
        raise ValueError(f"Invalid name: ({name})")
    return deps[0]


def extract_archive(source: Path, dest: Path, targets: Dict[str, str]):  # noqa: D103
    extract_dir = Path(tempfile.mkdtemp())
    with tarfile.open(str(source)) as tr:
        for trf in tr.getmembers():
            is_target = False
            for name in targets.keys():
                if trf.name.startswith(f"{name}"):
                    is_target = True
                    continue
            if not is_target:
                continue
            tr.extract(trf, extract_dir)
    for s, d in targets.items():
        src_path = extract_dir / s
        dest_path = dest / d  # type: ignore
        if src_path.is_dir():
            for child in src_path.iterdir():
                stale = dest_path / child.name
                if stale.is_dir():
                    shutil.rmtree(stale)
                elif stale.exists():
                    stale.unlink()
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src_path, dest_path)


def main(args: argparse.Namespace):  # noqa: D103
    dest = Path(RULE["dest"])  # type: ignore
    # Extra plugins tracked in git (e.g. plugin/audio-slideshow) live in the same
    # tree, so dest is not removed: extract_archive replaces only fetched entries.
    if (dest / "dist").exists() and not args.force:
        print("Dest directory is already exists")
        sys.exit(1)
    lockfile_json = ROOT_DIR / "npm-shrinkwrap.json"
    package = find_package(lockfile_json, RULE["name"])  # type: ignore
    local_archive = ROOT_DIR / "var" / f"{RULE['name']}-{package['version']}.tgz"
    if not local_archive.exists():
        urlretrieve(package["resolved"], local_archive)
    extract_archive(local_archive, dest, RULE["targets"])  # type: ignore


if __name__ == "__main__":
    if Path.cwd() != ROOT_DIR:
        logging.error("This script can run only project root.")
        sys.exit(1)
    (ROOT_DIR / "var").mkdir(exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", default=False)
    args = parser.parse_args()
    main(args)
