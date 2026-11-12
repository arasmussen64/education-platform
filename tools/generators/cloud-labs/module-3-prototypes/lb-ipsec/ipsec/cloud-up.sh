#!/bin/bash
# FRR for the cloud side, in the cloud namespace (pathspace "cloud").
set -euo pipefail
exec /usr/lib/frr/frrinit.sh start cloud
