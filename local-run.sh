#!/bin/bash
set -euo pipefail

docker build -t synchronizer:local .

docker run --rm -it \
  --network host \
  -e ACTION=config \
  synchronizer:local
