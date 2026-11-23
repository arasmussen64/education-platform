#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: the story so far, played out at the
# machine's first boot. The base runs it once, as root, with OpenBao's
# root token in BAO_TOKEN.
#
# Every key is made here, on this machine: the gateway's admin key and
# the shop's two payment keys. None is in the image or the repository.
set -euo pipefail
export HOME=/root

truth=/usr/local/lib/lab/debug
pay=/usr/local/bin/paygate

# The gateway's admin key, kept in OpenBao.
bao secrets enable -path=secret -version=2 kv > /dev/null
bao kv put secret/paygate/admin key="$($pay admin-key)" > /dev/null

# The shop's keys at the gateway. k1 is last year's; k2 was added at last
# month's rotation and is the one the export uses today.
read -r _ old < <($pay add-key)
read -r _ current < <($pay add-key)
printf '%s\n%s\n' "$old" "$current" > "$truth/keys"
chmod 600 "$truth/keys"

# The gateway's record: the shop used k1 every night until the rotation
# 30 days ago and k2 since; and on the last two nights k1 was used from
# an address that isn't the shop's.
day() { date -u -d "$1" +%Y-%m-%d; }
for ago in 33 32 31; do
  $pay note-use k1 charge ok 127.0.0.1 "$(day "$ago days ago")T02:00:03Z"
done
for ago in 30 29 28 3 2 1; do
  $pay note-use k2 charge ok 127.0.0.1 "$(day "$ago days ago")T02:00:04Z"
done
for ago in 2 1; do
  $pay note-use k1 charge ok 198.51.100.77 "$(day "$ago days ago")T03:41:19Z"
  $pay note-use k1 charge ok 198.51.100.77 "$(day "$ago days ago")T03:41:52Z"
done

# The export's key, as the unit reads it.
printf 'PAYGATE_KEY=%s\n' "$current" > /etc/shop/export.env
chmod 600 /etc/shop/export.env

# The shop's repository. The dates are fixed; the key isn't, so the
# commits' names differ from lab to lab.
git init -q --bare --shared=group /srv/git/shop.git
work=$(mktemp -d)
git clone -q /srv/git/shop.git "$work/shop" 2> /dev/null
(
  cd "$work/shop"
  git config user.name "Sam Okafor"
  git config user.email "sam@shop.test"
  commit() {
    git add -A
    GIT_AUTHOR_DATE="2026-0$1 10:15:00 +0000" GIT_COMMITTER_DATE="2026-0$1 10:15:00 +0000" \
      git commit -q -m "$2"
  }
  printf '# shop\n\nThe shop'"'"'s order service and its export.\n' > README.md
  commit 3-02 "Start the order service"
  mkdir -p deploy
  printf '[Service]\nUser=export\nExecStart=/usr/local/bin/shop-export --api-key %s\n' "$old" > deploy/shop-export.service
  commit 3-09 "Add the export's unit"
  printf '[Service]\nUser=export\nEnvironmentFile=/etc/shop/export.env\nExecStart=/usr/local/bin/shop-export --api-key ${PAYGATE_KEY}\n' > deploy/shop-export.service
  commit 3-10 "Read the key from a file on the server"
  printf '\nThe export charges the day'"'"'s orders every night.\n' >> README.md
  commit 4-21 "Say what the export does"
  git push -q origin main
)
rm -rf "$work"
chgrp -R git /srv/git/shop.git
chmod -R g+rwX /srv/git/shop.git
