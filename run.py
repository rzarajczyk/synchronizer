#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

def log(level: str, msg: str):
    print(f"[{level}] {msg}")

def fail(msg: str, code: int = 1):
    log("ERROR", msg)
    sys.exit(code)

def main():
    config_dir = Path(os.environ.get("CONFIG", "/config"))
    rclone_conf = config_dir / "rclone.conf"
    jobs_file = config_dir / "jobs.json"

    rclone_path = shutil.which("rclone")
    if not rclone_path:
        fail("rclone binary not found in PATH")

    try:
        subprocess.run([rclone_path, "version"], check=True)
    except subprocess.CalledProcessError as e:
        fail(f"Failed to execute rclone version: {e}")

    if not rclone_conf.is_file():
        fail(f"Missing file {rclone_conf}")
    if not jobs_file.is_file():
        fail(f"Missing file {jobs_file}")

    try:
        with jobs_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {jobs_file}: {e}")

    jobs = data.get("jobs")
    if jobs is None:
        fail("Missing 'jobs' array in jobs.json")
    if not isinstance(jobs, list):
        fail("'jobs' must be an array")

    total = len(jobs)
    log("INFO", f"Jobs count: {total}")

    dry_run = bool(data.get("dry-run", False))
    rclone_dry_flag = "--dry-run" if dry_run else ""
    if dry_run:
        log("INFO", "dry-run ACTIVE")

    for idx, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            log("WARN", f"Job {idx} skipped (not an object).")
            continue
        src = job.get("source")
        dst = job.get("destination")
        if not src or not dst:
            log("WARN", f"Job {idx} skipped (incorrect structure).")
            continue

        print(f"[JOB {idx}/{total}{rclone_dry_flag}] {src} -> {dst}")

        cmd = [
            rclone_path,
            "sync",
            src,
            dst,
            "--config", str(rclone_conf),
            "--transfers", "4",
            "--verbose",
        ]
        if dry_run:
            cmd.append("--dry-run")

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            fail(f"rclone sync failed for job {idx}: {e}")

    log("INFO", "Finished processing jobs.")

if __name__ == "__main__":
    main()
