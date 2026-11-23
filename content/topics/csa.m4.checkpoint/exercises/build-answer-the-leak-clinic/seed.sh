#!/bin/bash
# The scenery for "The leak at the clinic", built while the image is built. Every key,
# password and certificate is made here, so none of it is in the public
# repository this file lives in, and the provider-format keys are put
# together from pieces ("ml_""live_") so that no committed file matches a
# scanner's rule. The repository's history, the provider's trail and the
# CA's records are built by arithmetic, the same in every build apart from
# the random keys.
set -euo pipefail
home=/home/learner
planted=/usr/local/lib/lab/planted
install -d -m 700 "$planted"
useradd --system --no-create-home --shell /usr/sbin/nologin results

# --- the laboratory's stand-in: the clinic's keys there --------------------
# Two keys: the one the clinic's results service uses (which the
# repository leaked), and the one Northgate Surgery, a partner practice,
# uses from its own address.
prefix="ml_""live_"
leaked_key="$prefix$(openssl rand -hex 16)"
franchise_key="$prefix$(openssl rand -hex 16)"
install -d -m 700 /etc/medilab /var/lib/medilab
(umask 077 && openssl rand -hex 24 > /etc/medilab/admin.key)
sha() { printf '%s' "$1" | sha256sum | cut -d' ' -f1; }
cat > /var/lib/medilab/keys.json << EOF
[
 {"id": "k-4410", "sha256": "$(sha "$leaked_key")", "state": "active", "made": "2026-02-11 08:55"},
 {"id": "k-4502", "sha256": "$(sha "$franchise_key")", "state": "active", "made": "2026-07-01 12:30"}
]
EOF
chmod 600 /var/lib/medilab/keys.json
printf '%s\n' "$leaked_key" > "$planted/leaked.key"
printf '%s\n' "$franchise_key" > "$planted/franchise.key"

# --- the clinic's CA: an offline root, and the issuing CA on this server -----
ca=/srv/ca/issuing
install -d -m 755 /srv/ca /srv/ca/public "$ca" "$ca/newcerts"
install -d -m 700 "$ca/private"
work=$(mktemp -d)
openssl req -x509 -newkey rsa:2048 -nodes -keyout "$work/root.key" -out /srv/ca/public/root.pem \
  -days 3650 -subj "/O=Westbrook Clinic/CN=The clinic's root CA" \
  -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" 2> /dev/null
openssl req -newkey rsa:2048 -nodes -keyout "$ca/private/issuing.key" -out "$work/issuing.csr" \
  -subj "/O=Westbrook Clinic/CN=The clinic's issuing CA" 2> /dev/null
printf 'basicConstraints=critical,CA:TRUE,pathlen:0\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid\n' > "$work/ext"
openssl x509 -req -in "$work/issuing.csr" -CA /srv/ca/public/root.pem -CAkey "$work/root.key" \
  -CAcreateserial -days 3650 -extfile "$work/ext" -out "$ca/issuing.pem" 2> /dev/null
cp "$ca/issuing.pem" /srv/ca/public/issuing.pem
# The root's key leaves the server: an offline root is kept elsewhere.
rm -f "$work/root.key" /srv/ca/public/root.srl
cat > "$ca/ca.cnf" << 'EOF'
# The clinic's issuing CA, for "openssl ca -config /srv/ca/issuing/ca.cnf".
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
# published CRL isn't empty; then the results service's own.
issue wards-old.clinic.test 365 "$work/old.key" "$work/old.pem"
openssl ca -config "$ca/ca.cnf" -revoke "$work/old.pem" -crl_reason superseded 2> /dev/null
install -d -m 755 /etc/results /etc/results/tls
issue results.clinic.test 1095 "$work/results.key" "$work/results.crt"
openssl ca -config "$ca/ca.cnf" -gencrl -crldays 3650 -out /srv/ca/public/issuing.crl 2> /dev/null
cat "$work/results.crt" "$ca/issuing.pem" > /etc/results/tls/results.pem
install -m 640 -o root -g results "$work/results.key" /etc/results/tls/results.key
chmod 644 /etc/results/tls/results.pem
cp "$work/results.crt" "$planted/leaked-cert.pem"
cp "$work/results.key" "$planted/leaked-tls.key"
openssl x509 -in "$work/results.crt" -noout -serial | cut -d= -f2 > "$planted/leaked-serial"
openssl pkey -in "$work/results.key" -pubout | sha256sum | cut -d' ' -f1 > "$planted/leaked-tls.pub"
cat "$ca/crlnumber" > "$planted/crlnumber-start"

# --- the lab-results service -----------------------------------------------
cat > /etc/results/results.conf << 'EOF'
# The lab-results service's settings (read by /usr/local/lib/results/results).
# The file holding the clinic's key for the laboratory, as a line
# MEDILAB_KEY=...; read again for every request.
provider_key_file = /etc/results/lab.env
# What it serves HTTPS with: the certificate followed by its chain, and the
# private key. Read when the service starts.
tls_cert = /etc/results/tls/results.pem
tls_key = /etc/results/tls/results.key
EOF
printf 'MEDILAB_KEY=%s\n' "$leaked_key" > /etc/results/lab.env
chmod 644 /etc/results/results.conf /etc/results/lab.env

# --- the repository, its history built commit by commit -------------------
repo=/srv/git/results.git
src=$(mktemp -d)
git init -q -b main "$src"
n=0
commit() { # commit "MESSAGE": everything in the work tree, on a fixed day
  n=$((n + 1))
  local when
  when="2026-$(printf '%02d' $((2 + n)))-$(printf '%02d' $((20 - n * 2))) 14:$(printf '%02d' $((n * 5))):00 +0000"
  git -C "$src" add -A
  GIT_AUTHOR_DATE=$when GIT_COMMITTER_DATE=$when git -C "$src" -c user.name="Priya Raman" \
    -c user.email=priya@clinic.test commit -q -m "$1"
}
mkdir -p "$src/service" "$src/config" "$src/docs"
printf '# Lab results\n\nThe clinic'"'"'s lab-results service: the ward tablets ask it for a\npatient'"'"'s results, and it fetches them from the laboratory.\n' > "$src/README.md"
printf 'import http.server\n\n# The service itself is deployed from here.\n' > "$src/service/results.py"
commit "First version of the results service"
printf 'MEDILAB_KEY=%s\n' "$leaked_key" > "$src/config/lab.env"
commit "Settings for the laboratory"
printf '\nTIMEOUT = 5  # seconds to wait for the laboratory\n' >> "$src/service/results.py"
commit "Wait at most five seconds for the laboratory"
mkdir -p "$src/certs"
cp "$work/results.crt" "$src/certs/results.crt"
cp "$work/results.key" "$src/certs/results.key"
commit "Certificate for results.clinic.test"
printf '# Setting up a new server\n\nCopy config/lab.env, or set the key by hand:\n\n    export MEDILAB_KEY=%s\n' "$leaked_key" > "$src/docs/setup.md"
commit "How to set up a new server"
git -C "$src" rm -q -r certs
commit "The certificate belongs on the server, not here"
printf '\nWARDS = ["A", "B", "C"]\n' >> "$src/service/results.py"
commit "Three wards"
printf '\nAsk the infrastructure team for the settings.\n' >> "$src/README.md"
commit "Tidy the README"
git clone -q --bare "$src" "$repo"
rm -rf "$src"
git clone -q "$repo" "$home/results"
git -C "$home/results" config user.name "Learner"
git -C "$home/results" config user.email learner@clinic.test
chown -R learner:learner "$repo" "$home/results"

# --- the clinic's scanner settings, on the server -------------------------
install -d -m 755 /etc/gitleaks
cat > /etc/gitleaks/server.toml << 'EOF'
# The clinic's scanner settings: gitleaks' built-in rules, and the
# laboratory's key format, which the built-in rules don't know.
[extend]
useDefault = true

[[rules]]
id = "medilab-key"
description = "A key for the laboratory's API"
regex = '''ml_live_[a-z0-9]{32}'''
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

# --- the laboratory's trail of the clinic's keys, and the sheet -------------
install -d -m 755 /srv/incident
install -d -o learner -g learner -m 755 "$home/incident"
python3 - << 'EOF'
import hashlib

calls = []
# The results service, from the clinic's cloud address, all afternoon.
for i, minute in enumerate(range(12 * 60 + 5, 21 * 60, 13)):
    action = "order" if i % 6 == 5 else "fetch"
    calls.append((minute * 60 + 3 + i % 50, "k-4410", "192.0.2.70", action, [3, 1, 6, 2, 4][i % 5], "ok"))
# The wards' admin desk, from the clinic's sites, checking a few by hand.
for i, minute in enumerate(range(13 * 60 + 2, 20 * 60, 70)):
    calls.append((minute * 60 + 41, "k-4410", "198.51.100.140", "fetch", 1, "ok"))
# Northgate Surgery, with its own key, from its own address.
for i, minute in enumerate(range(12 * 60 + 30, 21 * 60, 37)):
    calls.append((minute * 60 + 12, "k-4502", "203.0.113.30", "fetch", [2, 5][i % 2], "ok"))
# Someone else, with the leaked key.
for hms, address, action, amount, result in [
    ("15:03:27", "198.18.40.9", "fetch", 1, "ok"),
    ("15:09:44", "198.18.40.9", "fetch", 25, "ok"),
    ("15:31:02", "203.0.113.166", "fetch", 50, "refused"),
    ("15:58:19", "203.0.113.166", "fetch", 40, "ok"),
    ("16:47:55", "198.18.40.9", "order", 2, "ok"),
    ("17:20:30", "203.0.113.166", "fetch", 60, "ok"),
    ("18:12:06", "198.18.40.9", "fetch", 50, "refused"),
    ("19:44:51", "203.0.113.166", "fetch", 35, "ok"),
    ("20:31:13", "198.18.40.9", "fetch", 20, "ok"),
]:
    h, m, s = map(int, hms.split(":"))
    calls.append((h * 3600 + m * 60 + s, "k-4410", address, action, amount, result))
prev = "0" * 64
with open("/srv/incident/medilab-trail.log", "w", encoding="utf-8", newline="\n") as log:
    for t, key, address, action, amount, result in sorted(calls):
        stamp = f"2026-11-09T{t // 3600:02d}:{t // 60 % 60:02d}:{t % 60:02d}Z"
        record = f"{stamp} key={key} from={address} action={action} count={amount} result={result}"
        prev = hashlib.sha256(f"{prev} {record}".encode()).hexdigest()
        log.write(f"{prev} {record}\n")
with open("/srv/incident/medilab-trail.anchor", "w", encoding="utf-8", newline="\n") as anchor:
    anchor.write(prev + "\n")
EOF
chmod 644 /srv/incident/medilab-trail.log /srv/incident/medilab-trail.anchor
rm -rf "$work"
