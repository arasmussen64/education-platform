#!/bin/bash
# Builds the lab's scenery while the image is built: the job's user and an
# ordinary account, the folders, the job's settings and the day's orders.
# Every key is made later, on the machine, at its first boot (bao-seed.sh):
# nothing key-shaped is in this file or the image.
set -euo pipefail

# The export runs as "export". "audit" is an ordinary account as every
# operator of the server has: no sudo, and in the groups that may read
# the journal.
useradd -r -s /usr/sbin/nologin export
useradd -m -s /bin/bash -G adm,systemd-journal audit

# What only the checks may read.
install -d -m 700 /usr/local/lib/lab/debug

install -d -m 755 /etc/shop /srv/shop
cat > /etc/shop/export.conf << 'EOF'
# /etc/shop/export.conf: the export's settings, read at each run.

# How much the job logs: info or debug.
log_level = debug

# The day's orders.
orders = /srv/shop/orders-today.csv
EOF
chmod 644 /etc/shop/export.conf

{
  echo "order,amount"
  for i in 1 2 3; do
    echo "$((8100 + i)),$((i * 17 % 60 + 20)).00"
  done
} > /srv/shop/orders-today.csv
chmod 644 /srv/shop/orders-today.csv

# The shop's scanner settings: gitleaks' built-in rules, and a rule for
# the payment gateway's key format.
install -d /etc/gitleaks
cat > /etc/gitleaks/shop.toml << 'TOML'
title = "The shop's scanner settings"

[extend]
useDefault = true

[[rules]]
id = "paygate-key"
description = "A payment gateway API key"
regex = '''pg_live_[A-Za-z0-9]{32}'''
TOML
chmod 644 /etc/gitleaks/shop.toml

# The git server's folder; the repository is made at first boot.
groupadd git
usermod -aG git learner
install -d -o root -g git -m 2775 /srv/git
git config --system --add safe.directory /srv/git/shop.git
git config --system init.defaultBranch main
