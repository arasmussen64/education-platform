#!/bin/bash
# The story of "Gaps in the trail", told once, at the lab's first boot (a
# container has no systemd while its image is built, and sealing keys
# belong to one machine). It leaves the payments server as it was a year
# after its audit trail was set up: sealed, with the auditors holding the
# key, some weeks of history on disk, and then last week's changes.
set -euo pipefail
stock=/usr/local/lib/lab/story
state=/var/lib/lab
mkdir -p "$state"

# The sealing keys, and the auditors' copy of the verification key. The
# image's journald@audit.conf already says Seal=yes; journald loads the
# keys when it starts.
journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 > /srv/auditors/verify-key
chmod 644 /srv/auditors/verify-key
systemctl restart systemd-journald@audit

# The shop answers once its audit writer has its socket.
for try in $(seq 1 150); do
  shop-cli login.ok user=ana src=203.0.113.9 > /dev/null 2>&1 && break
  sleep 0.2
done

# Some weeks of history, written while the policy and the journal were
# still as the build left them.
shop-cli refund actor=ana order=6101 amount=19.99 src=203.0.113.9
shop-cli login.failed user=ben src=198.51.100.7
shop-cli login.ok user=ben src=198.51.100.7
shop-cli role.change actor=root user=ben old=staff new=admin src=127.0.0.1
shop-cli refund actor=ben order=6102 amount=250.00 src=198.51.100.7
shop-cli config.change actor=ben setting=refund.limit old=100 new=5000 src=198.51.100.7
shop-cli card.update user=cy card=4242424242424242 src=192.0.2.44
shop-cli export actor=ben table=orders rows=1200 src=198.51.100.7
shop-cli role.change actor=ben user=dee old=staff new=admin src=198.51.100.7
shop-cli refund actor=dee order=6103 amount=4999.00 src=192.0.2.80
shop-cli role.change actor=root user=dee old=admin new=staff src=127.0.0.1
shop-cli login.ok user=zed-end-of-history src=203.0.113.9
for try in $(seq 1 150); do
  journalctl --namespace=audit -t shop-audit -o cat | grep -F 'user=zed-end-of-history ' > /dev/null && break
  sleep 0.2
done
# What the trail held before last week, for the check that nothing was
# taken out of it.
journalctl --namespace=audit -t shop-audit -o cat | grep '^time=' > "$state/history"
chmod 600 "$state/history"

# Last week's changes.
mkdir -p /etc/systemd/journald@audit.conf.d
install -m 644 "$stock/40-quiet.conf" "$stock/60-disk.conf" /etc/systemd/journald@audit.conf.d/
sed -i 's/^audit role\.change /audit role.chnage /' /etc/shop/audit.conf
systemctl reload shop-audit
systemctl restart systemd-journald@audit

# The audit writer's unit as the shop ships it, drop-ins and all.
systemctl cat shop-audit 2> /dev/null | sha256sum | cut -d' ' -f1 > "$state/unit.sum"
rm -rf "$stock"
touch "$state/story-told"
