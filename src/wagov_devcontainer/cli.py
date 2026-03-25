"""CLI entry point for wagov-devcontainer."""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import tempfile
from importlib.resources import files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provision the wagov devcontainer toolchain on the local machine")
    parser.add_argument("--user", dest="setup_user", help="User to configure (default: current user)")
    args, pyinfra_args = parser.parse_known_args(argv)

    if args.setup_user:
        os.environ["SETUP_USER"] = args.setup_user

    deploy_source = files("wagov_devcontainer").joinpath("deploy.py").read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", encoding="utf-8", delete=False) as tmpfile:
        tmpfile.write(deploy_source)
        deploy_path = tmpfile.name

    from pyinfra_cli.main import cli

    try:
        sys.argv = ["pyinfra", "@local", *pyinfra_args, "-y", deploy_path]
        cli()
    finally:
        pathlib.Path(deploy_path).unlink(missing_ok=True)

    return 0
