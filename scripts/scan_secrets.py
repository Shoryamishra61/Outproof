"""Fail on credential-shaped strings in versioned files; report paths, never values."""

import re
import subprocess
from pathlib import Path

PATTERN = re.compile(
    rb"(?:github_pat_[A-Za-z0-9_]{40,}|ghp_[A-Za-z0-9]{30,}|rnd_[A-Za-z0-9]{20,}|sntryu_[a-f0-9]{40,}|sk_[a-f0-9]{40,}|espr_[A-Za-z0-9_-]{30,})"
)


def main() -> None:
    files = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    failed = [
        name
        for name in files
        if name and Path(name).is_file() and PATTERN.search(Path(name).read_bytes())
    ]
    if failed:
        raise SystemExit("Credential-shaped strings: " + ", ".join(failed))
    print(f"Credential-pattern scan passed: {sum(bool(f) for f in files)} versioned paths")


if __name__ == "__main__":
    main()
