#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import logging
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# ----------------- Logging setup -----------------
logging.basicConfig(
    level="INFO",
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("synchronizer")

# ----------------- Errors -----------------

def fail(msg: str, code: int = 1):
    logger.error(msg)
    sys.exit(code)

# ----------------- Config loading -----------------

def load_config():
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

    return {
        "rclone_path": rclone_path,
        "rclone_conf": rclone_conf,
        "jobs": jobs,
        "raw": data,
    }

# ----------------- Job execution -----------------

def run_jobs(rclone_path: str, rclone_conf: Path, jobs, dry_run: bool):
    total = len(jobs)
    logger.info(f"Jobs count: {total}")
    if dry_run:
        logger.info("dry-run ACTIVE")
    rclone_dry_flag = " --dry-run" if dry_run else ""

    for idx, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            logger.warning(f"Job {idx} skipped (not an object).")
            continue
        src = job.get("source")
        dst = job.get("destination")
        if not src or not dst:
            logger.warning(f"Job {idx} skipped (incorrect structure).")
            continue

        logger.info(f"[JOB {idx}/{total}{rclone_dry_flag}] {src} -> {dst}")

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
    logger.info("Finished processing jobs.")

# ----------------- Scheduler orchestration -----------------

def scheduler_loop(cfg):
    data = cfg["raw"]
    schedule_expr = data.get("schedule")
    dry_run = bool(data.get("dry-run", False))

    if not schedule_expr:
        logger.info("No schedule field - single run.")
        run_jobs(cfg["rclone_path"], cfg["rclone_conf"], cfg["jobs"], dry_run)
        return

    logger.info(f"Scheduler active (cron): {schedule_expr}")

    scheduler = BlockingScheduler()

    def job_wrapper():
        logger.info("Scheduled execution started")
        run_jobs(cfg["rclone_path"], cfg["rclone_conf"], cfg["jobs"], dry_run)

    try:
        trigger = CronTrigger.from_crontab(schedule_expr)
    except ValueError as e:  # invalid cron format
        fail(f"Invalid cron expression: {e}")

    scheduler.add_job(
        job_wrapper,
        trigger=trigger,
        id="sync-jobs",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    logger.info("Entering blocking scheduler loop (Ctrl+C to exit)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown signal received.")
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")

# ----------------- Entry -----------------

if __name__ == "__main__":
    cfg = load_config()
    scheduler_loop(cfg)
