#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what OpenBao and the database hold when
# the lab starts. The base runs it once, at the machine's first boot, as
# root with OpenBao's root token in BAO_TOKEN, after PostgreSQL is up.
set -euo pipefail

sql() { runuser -u postgres -- psql -X -q -v ON_ERROR_STOP=1 -d "$1" -c "$2"; }

# The transit engine and the key the export's data keys are wrapped under.
bao secrets enable transit > /dev/null
bao write -f transit/keys/orders > /dev/null

# The shop's database: 25 orders, and an account for OpenBao to manage
# other accounts with. Its password is made here, on this machine, and
# OpenBao changes it at once to one only OpenBao knows (rotate-root).
password=$(openssl rand -hex 16)
sql postgres "CREATE ROLE bao_admin WITH LOGIN CREATEROLE PASSWORD '$password'"
sql postgres "CREATE DATABASE shop"
sql shop "CREATE TABLE orders (id integer PRIMARY KEY, total numeric NOT NULL)"
sql shop "INSERT INTO orders SELECT n, n * 7 % 90 + 10 FROM generate_series(1, 25) AS n"
sql shop "ALTER TABLE orders OWNER TO bao_admin"

bao secrets enable database > /dev/null
bao write database/config/shop \
  plugin_name=postgresql-database-plugin \
  allowed_roles=report \
  connection_url='postgresql://{{username}}:{{password}}@127.0.0.1:5432/shop' \
  username=bao_admin \
  password="$password" > /dev/null
bao write -f database/rotate-root/shop > /dev/null
