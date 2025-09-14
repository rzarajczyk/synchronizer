# synchronizer

A minimal container for running rclone tasks defined in the /config/jobs.json file.

## Configuration (only one allowed method)
Mount the *entire directory* with configuration files to the container under the /config path.
The directory must contain at least:
- rclone.conf
- jobs.json

Example local structure:
```
config/
  rclone.conf
  jobs.json
```

## jobs.json file
Structure:
```
{
  "dry-run": false,           // optional, default false; when true rclone runs with --dry-run
  "jobs": [
    { "source": "remote1:/path", "destination": "remote2:/other_path" },
    { "source": "remote3:/", "destination": "remote4:/backup" }
  ]
}
```
Each object must have `source` and `destination` fields in a format accepted by rclone (REMOTE:path).

To test without making changes set:
```
{
  "dry-run": true,
  "jobs": [ { "source": "remote1:/", "destination": "remote2:/backup" } ]
}
```
This will display planned operations only.
