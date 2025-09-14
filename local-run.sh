#!/bin/bash
set -euo pipefail

docker build -t synchronizer:local .

docker run --rm -it \
  --network host \
  -v ./config:/config \
  synchronizer:local
