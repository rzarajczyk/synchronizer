# synchronizer

Minimal container for running rclone tasks defined in /config/jobs.json.

## Configuration (the only way)
Mount the directory with configuration files at /config in the container.
Required files:
- rclone.conf
- jobs.json

Example local structure:
```
config/
  rclone.conf
  jobs.json
```

## jobs.json file
Basic structure:
```
{
  "dry-run": false,            // optional; if true adds --dry-run to rclone
  "schedule": "0 2 * * *",    // optional; 5-field cron (min hour day month day_of_week) or shortcut @hourly/@daily/@weekly/@monthly
  "jobs": [
    { "source": "remote1:/path", "destination": "remote2:/other_path" },
    { "source": "remote3:/", "destination": "remote4:/backup" }
  ]
}
```
Each object in `jobs` must have `source` and `destination` fields in a format accepted by rclone (REMOTE:path).

### Schedule
If the `schedule` field is omitted – tasks are run once and the container exits.
If `schedule` is set – APScheduler (CronTrigger) is used and the container remains active.

Example: every day at 02:00
```
{
  "schedule": "0 2 * * *",
  "jobs": [ { "source": "r1:/", "destination": "r2:/backup" } ]
}
```

### Test mode (dry-run)
To see planned operations without making changes:
```
{
  "dry-run": true,
  "jobs": [ { "source": "remote1:/", "destination": "remote2:/backup" } ]
}
```