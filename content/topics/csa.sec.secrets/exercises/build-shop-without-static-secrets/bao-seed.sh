#!/bin/bash
# /etc/lab/bao-seed.d/10-shop.sh: what the database, OpenBao and the API's
# credentials file hold when the lab starts. The base runs it once, at the
# machine's first boot, as root with OpenBao's root token in BAO_TOKEN,
# after PostgreSQL is up.
#
# Both passwords are made here, on this machine: the API's static
# password and the database admin's. Neither is in the image or the
# repository.
set -euo pipefail

truth=/usr/local/lib/lab/build
# sql DATABASE STATEMENT: the statement goes to psql on its standard input,
# never as an argument: a command that changes user is noted in the journal
# with its whole command line, and a password in a statement would be
# there for every operator to read.
sql() { runuser -u postgres -- psql -X -q -v ON_ERROR_STOP=1 -d "$1" <<< "$2"; }

app=$(openssl rand -hex 16)
admin=$(openssl rand -hex 16)
echo "$app" > "$truth/app-password"
echo "$admin" > "$truth/admin-password"
chmod 600 "$truth/app-password" "$truth/admin-password"

# The shop database: 25 orders and 8 customers; an admin account that may
# make other accounts (for OpenBao, once it is connected); and the API's
# own account, shop_app, with the password it has had for years.
sql postgres "CREATE ROLE bao_admin WITH LOGIN CREATEROLE PASSWORD '$admin'"
sql postgres "CREATE ROLE shop_app WITH LOGIN PASSWORD '$app'"
sql postgres "CREATE DATABASE shop"
sql shop "CREATE TABLE orders (id integer PRIMARY KEY, total numeric NOT NULL)"
sql shop "INSERT INTO orders SELECT n, n * 7 % 90 + 10 FROM generate_series(1, 25) AS n"
sql shop "CREATE TABLE customers (id integer PRIMARY KEY, email text NOT NULL)"
sql shop "INSERT INTO customers SELECT n, 'customer' || n || '@example.test' FROM generate_series(1, 8) AS n"
sql shop "ALTER TABLE orders OWNER TO bao_admin"
sql shop "ALTER TABLE customers OWNER TO bao_admin"
sql shop "GRANT SELECT, INSERT ON orders TO shop_app"

# The API's credentials file, as it has been for years.
cat > /etc/shop/db.conf << EOF
# The order API's database account.
[shop]
host=127.0.0.1
dbname=shop
user=shop_app
password=$app
EOF
chown shop:shop /etc/shop/db.conf
chmod 400 /etc/shop/db.conf

# OpenBao's key-value store, where the database's admin left the admin
# account for whoever sets up dynamic credentials.
bao secrets enable -path=secret -version=2 kv > /dev/null
printf "%s" "$admin" | bao kv put secret/db/admin username=bao_admin password=- > /dev/null
