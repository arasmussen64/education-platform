#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: the story so far, played out at the
# machine's first boot. The base runs it once, as root, with OpenBao's
# root token in BAO_TOKEN, after PostgreSQL is up.
#
# Every key and password is made here, on this machine: the gateway's
# admin key, the shop's payment key, the database password, the deploy
# token. None is in the image or the repository. The payment key is then
# leaked the four ways the walkthrough follows: into the git history,
# into an image, into a unit file and a command line, and into the
# journal.
set -euo pipefail
export HOME=/root

truth=/usr/local/lib/lab/example
# sql DATABASE STATEMENT: the statement goes to psql on its standard input,
# never as an argument: a command that changes user is noted in the journal
# with its whole command line, and a password in a statement would be
# there for every operator to read.
sql() { runuser -u postgres -- psql -X -q -v ON_ERROR_STOP=1 -d "$1" <<< "$2"; }

# --- The payment gateway: its admin key, kept in OpenBao, and the shop's
# key, k1.
bao secrets enable -path=secret -version=2 kv > /dev/null
# (The admin key goes to bao down a pipe, "key=-", never as an argument.)
/usr/local/bin/paygate admin-key | tr -d '\n' | bao kv put secret/paygate/admin key=- > /dev/null
read -r _ key < <(/usr/local/bin/paygate add-key)
echo "$key" > "$truth/leaked-key"
chmod 600 "$truth/leaked-key"

# The gateway's record already holds two days of the key's use: the
# shop's own, and three charges last night from an address that isn't the
# shop's.
day() { date -u -d "$1" +%Y-%m-%d; }
for hour in 09 13 17; do
  /usr/local/bin/paygate note-use k1 charge ok 127.0.0.1 "$(day '2 days ago')T$hour:00:04Z"
  /usr/local/bin/paygate note-use k1 charge ok 127.0.0.1 "$(day '1 day ago')T$hour:00:05Z"
done
for minute in 12 13 15; do
  /usr/local/bin/paygate note-use k1 charge ok 203.0.113.50 "$(day '1 day ago')T23:$minute:41Z"
done

# The gateway's own date for the key, to match that record and the
# repository: it was made the day its settings file was committed.
# (add-key stamps a key with the moment it runs.)
python3 - "2026-05-12T09:58:21Z" << 'PY'
import json
import sys

path = "/var/lib/paygate/keys.json"
with open(path, encoding="utf-8") as file:
    keys = json.load(file)
for key, created in zip(keys, sys.argv[1:]):
    key["created"] = created
with open(path, "w", encoding="utf-8") as file:
    json.dump(keys, file, indent=1)
PY

# --- Leak 1: the repository. Five commits; the third adds a settings file
# with the key in it, and the fourth deletes the file again. The dates
# are fixed; the key isn't, so the commits' names differ from lab to lab.
git init -q --bare --shared=group /srv/git/shop.git
work=$(mktemp -d)
git clone -q /srv/git/shop.git "$work/shop" 2> /dev/null
(
  cd "$work/shop"
  git config user.name "Sam Okafor"
  git config user.email "sam@shop.test"
  commit() {
    git add -A
    GIT_AUTHOR_DATE="2026-05-$1 10:15:00 +0000" GIT_COMMITTER_DATE="2026-05-$1 10:15:00 +0000" \
      git commit -q -m "$2"
  }
  printf '# shop\n\nThe shop'"'"'s order service and its nightly export.\n' > README.md
  commit 04 "Start the order service"
  mkdir -p app
  printf '#!/bin/bash\n# Charges the day'"'"'s orders at the payment gateway.\n. config/paygate.env\n' > app/export.sh
  commit 11 "Add the nightly export"
  mkdir -p config
  printf '# Settings for the nightly export.\nGATEWAY=http://127.0.0.1:9440\nPAYGATE_KEY=%s\n' "$key" > config/paygate.env
  commit 12 "Add the gateway settings"
  git rm -q config/paygate.env
  printf '#!/bin/bash\n# Charges the day'"'"'s orders at the payment gateway.\n# The key comes from the server, not from this repository.\n' > app/export.sh
  commit 13 "Move the key out of the repository"
  printf '\nOrders are exported every night.\n' >> README.md
  commit 20 "Say when the export runs"
  git push -q origin main
)
rm -rf "$work"
chgrp -R git /srv/git/shop.git
chmod -R g+rwX /srv/git/shop.git

# --- Leak 2: the image the export job was shipped in. Its recipe takes
# the key as a build argument, and copies in a deploy token that a later
# step deletes. (The busybox image it starts from is made by a unit of the
# base; starting it here waits until it is there.)
systemctl start lab-busybox-image.service
build=$(mktemp -d)
cp /srv/shop/export-image/Containerfile "$build/"
echo "deploy-$(openssl rand -hex 12)" > "$build/deploy.token"
podman build -q --build-arg PAYGATE_KEY="$key" -t shop-export:1 "$build" > /dev/null
rm -rf "$build"

# --- Leaks 3 and 4: the demo job. Its key is in a unit file every user
# can read and on its command line, and it logs each request, header and
# all, into the journal.
install -d -m 755 /etc/systemd/system/shop-demo.service.d
printf '# The demo job'"'"'s key.\n[Service]\nEnvironment=PAYGATE_KEY=%s\n' "$key" \
  > /etc/systemd/system/shop-demo.service.d/key.conf
chmod 644 /etc/systemd/system/shop-demo.service.d/key.conf
systemctl daemon-reload

# --- The database for the walkthrough's last part: 25 orders, and an
# account for OpenBao to manage other accounts with. Its password is in
# OpenBao's key-value store, where the database's admin left it.
password=$(openssl rand -hex 16)
echo "$password" > "$truth/db-admin-password"
chmod 600 "$truth/db-admin-password"
sql postgres "CREATE ROLE bao_admin WITH LOGIN CREATEROLE PASSWORD '$password'"
sql postgres "CREATE DATABASE shop"
sql shop "CREATE TABLE orders (id integer PRIMARY KEY, total numeric NOT NULL)"
sql shop "INSERT INTO orders SELECT n, n * 7 % 90 + 10 FROM generate_series(1, 25) AS n"
sql shop "CREATE TABLE customers (id integer PRIMARY KEY, email text NOT NULL)"
sql shop "INSERT INTO customers SELECT n, 'customer' || n || '@example.test' FROM generate_series(1, 8) AS n"
sql shop "ALTER TABLE orders OWNER TO bao_admin"
sql shop "ALTER TABLE customers OWNER TO bao_admin"
printf "%s" "$password" | bao kv put secret/db/admin username=bao_admin password=- > /dev/null
