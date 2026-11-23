#!/bin/bash
# Builds the lab's scenery while the image is built: the API's settings,
# the platform's list of workloads, and a second workload's user. Every
# password and key is made later, on the machine, at its first boot
# (bao-seed.sh and platform-token): none is in this file or the image.
set -euo pipefail

# What only the checks may read.
install -d -m 700 /usr/local/lib/lab/build

# The order API runs as "shop" (the base made that user). Another job on
# this machine, the nightly report, runs as "report": a second workload,
# with a platform token of its own.
useradd -r -s /usr/sbin/nologin report

install -d -m 755 /etc/shop
cat > /etc/shop/shop-api.conf << 'EOF'
# /etc/shop/shop-api.conf: the order API's settings, read at each request.

# The file the API reads its database account from (a PostgreSQL service
# file with a [shop] section).
credentials = /etc/shop/db.conf
EOF
chmod 644 /etc/shop/shop-api.conf

# The platform's list: which workloads run here, and as which user.
install -d -m 755 /etc/lab-platform
cat > /etc/lab-platform/workloads << 'EOF'
# WORKLOAD USER: the platform signs a token for each workload, readable
# by that user alone, in /run/platform/WORKLOAD/token.
shop-api shop
report-job report
EOF
chmod 644 /etc/lab-platform/workloads
