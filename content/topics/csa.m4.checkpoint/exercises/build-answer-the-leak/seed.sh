#!/bin/bash
# The scenery for "The leak", built while the image is built. Every key,
# password and certificate is made here, so none of it is in the public
# repository this file lives in, and the provider-format keys are put
# together from pieces ("gk_""live_") so that no committed file matches a
# scanner's rule. The repository's history, the provider's trail and the
# CA's records are built by arithmetic, the same in every build apart from
# the random keys.
set -euo pipefail
home=/home/learner
planted=/usr/local/lib/lab/planted
install -d -m 700 "$planted"
useradd --system --no-create-home --shell /usr/sbin/nologin giftcards

# --- the gift-card company's stand-in: the shop's keys there ---------------
# Three keys: the first, revoked at the June rotation; the one the
# shop uses now (which the repository leaked); and the franchise store's.
prefix="gk_""live_"
old_key="$prefix$(openssl rand -hex 16)"
leaked_key="$prefix$(openssl rand -hex 16)"
franchise_key="$prefix$(openssl rand -hex 16)"
install -d -m 700 /etc/gift-provider /var/lib/gift-provider
(umask 077 && openssl rand -hex 24 > /etc/gift-provider/admin.key)
sha() { printf '%s' "$1" | sha256sum | cut -d' ' -f1; }
cat > /var/lib/gift-provider/keys.json << EOF
[
 {"id": "k-5531", "sha256": "$(sha "$old_key")", "state": "revoked", "made": "2026-04-08 16:30"},
 {"id": "k-7208", "sha256": "$(sha "$leaked_key")", "state": "active", "made": "2026-06-15 10:20"},
 {"id": "k-7311", "sha256": "$(sha "$franchise_key")", "state": "active", "made": "2026-05-04 14:05"}
]
EOF
chmod 600 /var/lib/gift-provider/keys.json
printf '%s\n' "$leaked_key" > "$planted/leaked.key"
printf '%s\n' "$old_key" > "$planted/old.key"
printf '%s\n' "$franchise_key" > "$planted/franchise.key"

# --- the shop's CA: an offline root, and the issuing CA on this server -----
ca=/srv/ca/issuing
install -d -m 755 /srv/ca /srv/ca/public "$ca" "$ca/newcerts"
install -d -m 700 "$ca/private"
work=$(mktemp -d)
openssl req -x509 -newkey rsa:2048 -nodes -keyout "$work/root.key" -out /srv/ca/public/root.pem \
  -days 3650 -subj "/O=The shop/CN=The shop's root CA" \
  -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" 2> /dev/null
openssl req -newkey rsa:2048 -nodes -keyout "$ca/private/issuing.key" -out "$work/issuing.csr" \
  -subj "/O=The shop/CN=The shop's issuing CA" 2> /dev/null
printf 'basicConstraints=critical,CA:TRUE,pathlen:0\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid\n' > "$work/ext"
openssl x509 -req -in "$work/issuing.csr" -CA /srv/ca/public/root.pem -CAkey "$work/root.key" \
  -CAcreateserial -days 3650 -extfile "$work/ext" -out "$ca/issuing.pem" 2> /dev/null
cp "$ca/issuing.pem" /srv/ca/public/issuing.pem
# The root's key leaves the server: an offline root is kept elsewhere.
rm -f "$work/root.key" /srv/ca/public/root.srl
cat > "$ca/ca.cnf" << 'EOF'
# The shop's issuing CA, for "openssl ca -config /srv/ca/issuing/ca.cnf".
[ ca ]
default_ca = issuing

[ issuing ]
dir              = /srv/ca/issuing
database         = $dir/index.txt
serial           = $dir/serial
crlnumber        = $dir/crlnumber
new_certs_dir    = $dir/newcerts
certificate      = $dir/issuing.pem
private_key      = $dir/private/issuing.key
default_md       = sha256
default_days     = 365
default_crl_days = 30
policy           = only_a_name
# A request's subjectAltName (the server's name) goes into its certificate.
copy_extensions  = copy
x509_extensions  = server_cert

[ only_a_name ]
commonName = supplied

# Every certificate this CA issues is a server's.
[ server_cert ]
basicConstraints       = critical, CA:FALSE
keyUsage               = critical, digitalSignature, keyEncipherment
extendedKeyUsage       = serverAuth
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid, issuer
EOF
: > "$ca/index.txt"
echo 'unique_subject = no' > "$ca/index.txt.attr"
echo 1000 > "$ca/serial"
echo 2000 > "$ca/crlnumber"
issue() { # issue NAME DAYS KEYFILE CERTFILE
  openssl req -newkey rsa:2048 -nodes -keyout "$3" -out "$work/req.csr" -subj "/CN=$1" \
    -addext "subjectAltName=DNS:$1" 2> /dev/null
  openssl ca -batch -config "$ca/ca.cnf" -days "$2" -in "$work/req.csr" -out "$4" 2> /dev/null
}
# An old certificate, revoked when its server was replaced, so the
# published CRL isn't empty; then the gift-card service's own.
issue tills-old.shop.test 365 "$work/old.key" "$work/old.pem"
openssl ca -config "$ca/ca.cnf" -revoke "$work/old.pem" -crl_reason superseded 2> /dev/null
install -d -m 755 /etc/giftcards /etc/giftcards/tls
issue gifts.shop.test 1095 "$work/gifts.key" "$work/gifts.crt"
openssl ca -config "$ca/ca.cnf" -gencrl -crldays 3650 -out /srv/ca/public/issuing.crl 2> /dev/null
cat "$work/gifts.crt" "$ca/issuing.pem" > /etc/giftcards/tls/gifts.pem
install -m 640 -o root -g giftcards "$work/gifts.key" /etc/giftcards/tls/gifts.key
chmod 644 /etc/giftcards/tls/gifts.pem
cp "$work/gifts.crt" "$planted/leaked-cert.pem"
cp "$work/gifts.key" "$planted/leaked-tls.key"
openssl x509 -in "$work/gifts.crt" -noout -serial | cut -d= -f2 > "$planted/leaked-serial"
openssl pkey -in "$work/gifts.key" -pubout | sha256sum | cut -d' ' -f1 > "$planted/leaked-tls.pub"
cat "$ca/crlnumber" > "$planted/crlnumber-start"

# --- the gift-card service -------------------------------------------------
cat > /etc/giftcards/giftcards.conf << 'EOF'
# The gift-card service's settings (read by /usr/local/lib/giftcards/giftcards).
# The file holding the shop's key for the gift-card company, as a line
# GIFT_PROVIDER_KEY=...; read again for every card.
provider_key_file = /etc/giftcards/prod.env
# What it serves HTTPS with: the certificate followed by its chain, and the
# private key. Read when the service starts.
tls_cert = /etc/giftcards/tls/gifts.pem
tls_key = /etc/giftcards/tls/gifts.key
EOF
printf 'GIFT_PROVIDER_KEY=%s\n' "$leaked_key" > /etc/giftcards/prod.env
chmod 644 /etc/giftcards/giftcards.conf /etc/giftcards/prod.env

# --- the repository, its history built commit by commit -------------------
repo=/srv/git/giftcards.git
src=$(mktemp -d)
git init -q -b main "$src"
n=0
commit() { # commit "MESSAGE": everything in the work tree, on a fixed day
  n=$((n + 1))
  local when
  when="2026-$(printf '%02d' $((3 + n / 2)))-$(printf '%02d' $((3 + n * 2))) 10:$(printf '%02d' $((n * 4))):00 +0000"
  git -C "$src" add -A
  GIT_AUTHOR_DATE=$when GIT_COMMITTER_DATE=$when git -C "$src" -c user.name="Sam Okafor" \
    -c user.email=sam@shop.test commit -q -m "$1"
}
mkdir -p "$src/app" "$src/config" "$src/docs"
printf '# Gift cards\n\nThe shop'"'"'s gift-card service: the tills ask it for cards, and it\nissues them at the gift-card company.\n' > "$src/README.md"
printf 'import http.server\n\n# The service itself is deployed from here.\n' > "$src/app/giftcards.py"
printf 'GIFT_PROVIDER_KEY=put-the-key-here\n' > "$src/config/example.env"
commit "Start the gift-card service"
printf 'def issue(amount):\n    """Ask the gift-card company for a card worth amount."""\n' > "$src/app/tills.py"
commit "Add the tills' API"
printf 'GIFT_PROVIDER_KEY=%s\n' "$old_key" > "$src/config/prod.env"
commit "Production settings"
printf '\nRETRIES = 2  # the company sometimes takes a second to answer\n' >> "$src/app/giftcards.py"
commit "Retry the gift-card company twice"
printf '# The tills\n\nEach till asks /issue?amount=N and prints the card.\n' > "$src/docs/tills.md"
commit "Docs for the tills"
printf 'GIFT_PROVIDER_KEY=%s\n' "$leaked_key" > "$src/config/prod.env"
commit "New key after the rotation"
printf '\nLOG_EVERY_CARD = True\n' >> "$src/app/giftcards.py"
commit "Log every card issued"
mkdir -p "$src/deploy/tls"
cp "$work/gifts.crt" "$src/deploy/tls/gifts.crt"
cp "$work/gifts.key" "$src/deploy/tls/gifts.key"
commit "TLS for gifts.shop.test"
printf '\nHEALTH_PAGE = "/health"\n' >> "$src/app/giftcards.py"
commit "Health page"
git -C "$src" rm -q -r deploy
commit "Take the TLS files out of the repository"
printf '\nAsk the platform team for the settings.\n' >> "$src/README.md"
commit "Tidy the README"
printf '\nAMOUNTS_IN_WHOLE_DOLLARS = True\n' >> "$src/app/tills.py"
commit "Amounts in whole dollars"
git clone -q --bare "$src" "$repo"
rm -rf "$src"
git clone -q "$repo" "$home/giftcards"
git -C "$home/giftcards" config user.name "Learner"
git -C "$home/giftcards" config user.email learner@shop.test
chown -R learner:learner "$repo" "$home/giftcards"

# --- the shop's scanner settings, on the server ---------------------------
install -d -m 755 /etc/gitleaks
cat > /etc/gitleaks/server.toml << 'EOF'
# The shop's scanner settings: gitleaks' built-in rules, and the gift-card
# company's key format, which the built-in rules don't know.
[extend]
useDefault = true

[[rules]]
id = "giftcard-key"
description = "A key for the gift-card company's API"
regex = '''gk_live_[a-z0-9]{32}'''
EOF
chmod 644 /etc/gitleaks/server.toml
# What the scanner finds in the history: the truth the list is held to.
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='*' \
  gitleaks detect --source "$repo" --config /etc/gitleaks/server.toml --no-banner \
  --report-format json --report-path "$work/found.json" > /dev/null 2>&1 || true
python3 -c '
import json, sys
for f in json.load(open(sys.argv[1])):
    print(f["Commit"], f["File"], f["RuleID"])
' "$work/found.json" | sort > "$planted/leaks.tsv"
[ "$(wc -l < "$planted/leaks.tsv")" = 3 ] || {
  echo "seed: the scanner found $(wc -l < "$planted/leaks.tsv") secrets, not 3" >&2
  exit 1
}

# --- the gift-card company's trail of the shop's keys, and the sheet --------
install -d -m 755 /srv/incident
install -d -o learner -g learner -m 755 "$home/incident"
python3 - << 'EOF'
import hashlib

shop = []
# The service, from the shop's cloud address, all day with its key.
for i, minute in enumerate(range(6 * 60 + 3, 16 * 60, 17)):
    amount = [10, 20, 25, 50][i % 4]
    action = "balance" if i % 5 == 4 else "issue"
    shop.append((minute * 60 + 11 + i % 40, "k-7208", "192.0.2.35", action, 0 if action == "balance" else amount, "ok"))
# The support desk, from the office, looking balances up with the same key.
for i, minute in enumerate(range(9 * 60 + 20, 15 * 60, 95)):
    shop.append((minute * 60 + 7, "k-7208", "198.51.100.21", "balance", 0, "ok"))
# The franchise store, with a key of its own, from its own address.
for i, minute in enumerate(range(7 * 60 + 15, 16 * 60, 41)):
    shop.append((minute * 60 + 30, "k-7311", "203.0.113.10", "issue", [25, 50][i % 2], "ok"))
# Someone else, with the leaked key.
for hms, address, action, amount, result in [
    ("11:42:09", "203.0.113.47", "balance", 0, "ok"),
    ("11:44:51", "203.0.113.47", "issue", 100, "ok"),
    ("11:47:30", "203.0.113.47", "issue", 250, "ok"),
    ("11:52:02", "203.0.113.47", "issue", 500, "refused"),
    ("12:05:17", "198.18.7.21", "issue", 250, "ok"),
    ("12:31:40", "198.18.7.21", "balance", 0, "ok"),
    ("13:02:11", "203.0.113.47", "issue", 250, "ok"),
    ("13:40:55", "198.18.7.21", "issue", 500, "refused"),
    ("14:12:08", "203.0.113.47", "issue", 100, "ok"),
    ("14:58:33", "198.18.7.21", "issue", 250, "ok"),
    ("15:21:47", "203.0.113.47", "issue", 250, "ok"),
    ("15:44:02", "198.18.7.21", "issue", 100, "ok"),
]:
    h, m, s = map(int, hms.split(":"))
    shop.append((h * 3600 + m * 60 + s, "k-7208", address, action, amount, result))
prev = "0" * 64
with open("/srv/incident/provider-trail.log", "w", encoding="utf-8", newline="\n") as log:
    for t, key, address, action, amount, result in sorted(shop):
        stamp = f"2026-11-22T{t // 3600:02d}:{t // 60 % 60:02d}:{t % 60:02d}Z"
        record = f"{stamp} key={key} from={address} action={action} amount={amount} result={result}"
        prev = hashlib.sha256(f"{prev} {record}".encode()).hexdigest()
        log.write(f"{prev} {record}\n")
with open("/srv/incident/provider-trail.anchor", "w", encoding="utf-8", newline="\n") as anchor:
    anchor.write(prev + "\n")
EOF
chmod 644 /srv/incident/provider-trail.log /srv/incident/provider-trail.anchor
rm -rf "$work"
