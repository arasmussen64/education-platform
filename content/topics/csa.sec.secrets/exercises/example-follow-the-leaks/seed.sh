#!/bin/bash
# Builds the walkthrough's scenery while the image is built: the job's
# user, the folders, the shop's scanner settings and the recipe of the
# leaky image. Everything secret is made later, on the machine, at its
# first boot (bao-seed.sh): nothing key-shaped is in this file or the
# image.
set -euo pipefail

# The demo job runs as "export"; "audit" stands for any other ordinary
# user of the server.
useradd -r -s /usr/sbin/nologin export
useradd -m -s /bin/bash audit

# What only the checks may read.
install -d -m 700 /usr/local/lib/lab/example

# The shop's own scanner settings: gitleaks' built-in rules, and a rule for
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

# The recipe of the image the export job was shipped in last year. The
# image itself is built at first boot, with that boot's key.
install -d /srv/shop/export-image
cat > /srv/shop/export-image/Containerfile << 'RECIPE'
FROM busybox
ARG PAYGATE_KEY
ENV GREETING=hello
COPY deploy.token /tmp/deploy.token
RUN echo "checked the gateway with $PAYGATE_KEY" > /opt/checked.txt && rm /tmp/deploy.token
CMD ["/bin/sh", "-c", "echo $GREETING from the export image"]
RECIPE
chmod -R a+rX /srv/shop

# The git server's folder; the repository is made at first boot.
groupadd git
usermod -aG git learner
install -d -o root -g git -m 2775 /srv/git
git config --system --add safe.directory /srv/git/shop.git
git config --system init.defaultBranch main
