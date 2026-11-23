# pkicheck.sh: what the checks of this topic's network labs share. A check
# starts with:   . /usr/local/lib/lab/pkicheck.sh
# Checks run as root on the lab machine, where a machine's own /etc/NAME is
# /etc/netns/MACHINE/NAME.
. /usr/local/lib/netlab/checklib.sh

ROOT_DIR=/etc/netns/root/shop-ca
CA_DIR=/etc/netns/ca/shop-ca
ROOT_PEM=$ROOT_DIR/root.pem
CA_PEM=$CA_DIR/partners.pem
API=https://api.shop.test/orders

# api_up: nginx on web answers HTTPS for the API (with any status).
api_up() { on office curl -sk --max-time 2 -o /dev/null https://api.shop.test/; }

# ca_web_up: nginx on ca answers at crl.shop.test (with any status).
ca_web_up() { on office curl -s --max-time 2 -o /dev/null http://crl.shop.test/; }

# ocsp_status CA-CERT CERT [URL]: what the CA's OCSP responder tells the
# office about CERT: good, revoked or unknown; nothing when no answer signed
# by the CA comes. It waits a few seconds for a responder that has just
# started, and throws the first answer away: openssl's responder re-reads
# the database after it has answered. Every question has a time limit, and
# the port is never probed with a bare connection (nc -z), which hangs
# openssl's responder for good.
ocsp_status() {
  local ca=$1 cert=$2 url=${3:-http://ocsp.shop.test:8888} said i
  for i in 1 2 3 4; do
    said=$(on office timeout 5 openssl ocsp -issuer "$ca" -CAfile "$ROOT_PEM" -cert "$cert" -url "$url" 2>&1)
    printf '%s\n' "$said" | grep '^Response verify OK' > /dev/null && break
    sleep 1
  done
  said=$(on office timeout 5 openssl ocsp -issuer "$ca" -CAfile "$ROOT_PEM" -cert "$cert" -url "$url" 2>&1)
  printf '%s\n' "$said" | grep '^Response verify OK' > /dev/null || return 0
  printf '%s\n' "$said" | sed -n 's/^.*: \(good\|revoked\|unknown\)$/\1/p' | head -n 1
}

# api_code MACHINE [CERT KEY]: the HTTP status the API gives a client on
# MACHINE that shows CERT (a file with its certificate, and any it sends
# after it) and holds KEY; with no CERT, a client that shows nothing.
api_code() {
  local m=$1
  shift
  if [ $# -ge 2 ]; then
    on "$m" curl -s --max-time 5 -o /dev/null -w '%{http_code}' --cert "$1" --key "$2" "$API" 2> /dev/null
  else
    on "$m" curl -s --max-time 5 -o /dev/null -w '%{http_code}' "$API" 2> /dev/null
  fi
}

# served NAME FILE: what crl.shop.test serves as NAME, fetched from the
# office into FILE. Fails when nothing comes.
served() { on office curl -fsS --max-time 5 "http://crl.shop.test/$1" > "$2" 2> /dev/null && [ -s "$2" ]; }

# serial_of CERT: a certificate's serial number, as the CA's database
# writes it.
serial_of() { openssl x509 -in "$1" -noout -serial 2> /dev/null | cut -d= -f2; }

# crl_lists CRL CERT: the CRL lists the certificate's serial number.
crl_lists() {
  local s
  s=$(serial_of "$2")
  [ -n "$s" ] && openssl crl -in "$1" -noout -text 2> /dev/null | grep -i "Serial Number: $s\$" > /dev/null
}

# crl_from CRL CA-CERT: the CRL is signed by that CA.
crl_from() { openssl crl -in "$1" -noout -CAfile "$2" 2>&1 | grep '^verify OK' > /dev/null; }

# seconds_left CRL: seconds from now until the CRL's nextUpdate (negative
# when it has passed). crl_life CRL: seconds from lastUpdate to nextUpdate.
crl_date() { date -u -d "$(openssl crl -in "$1" -noout "-$2" 2> /dev/null | cut -d= -f2)" +%s 2> /dev/null; }
seconds_left() { echo $(($(crl_date "$1" nextupdate) - $(date -u +%s))); }
crl_life() { echo $(($(crl_date "$1" nextupdate) - $(crl_date "$1" lastupdate))); }

# crl_number CRL: its number, in decimal.
crl_number() { echo $((16#$(openssl crl -in "$1" -noout -crlnumber 2> /dev/null | sed 's/^crlNumber=0x//;s/^crlNumber=//'))); }

# split_crls FILE DIR PREFIX: FILE's CRLs, one a file, as DIR/PREFIX1.crl,
# DIR/PREFIX2.crl and so on.
split_crls() { awk -v d="$2" -v p="$3" '/BEGIN X509 CRL/ {n++} n {print > (d "/" p n ".crl")}' "$1" 2> /dev/null; }

# db_status DATABASE CERT: the first letter of the certificate's line in a
# CA's database (V, R or E), or nothing.
db_status() {
  local s
  s=$(serial_of "$2")
  [ -n "$s" ] && awk -F'\t' -v s="$s" 'toupper($4) == toupper(s) {print $1}' "$1" | head -n 1
}

# same_key CERT KEY: the certificate is for that private key.
same_key() {
  [ -n "$(openssl x509 -in "$1" -noout -pubkey 2> /dev/null)" ] &&
    [ "$(openssl x509 -in "$1" -noout -pubkey 2> /dev/null)" = "$(openssl pkey -in "$2" -pubout 2> /dev/null)" ]
}

# timer_ok UNIT MAX-SECONDS: the timer is switched on now and at every boot,
# from a unit file that lasts, runs its service after a boot (a timer with
# only OnUnitActiveSec never runs again once the machine has restarted), and
# never waits longer than MAX-SECONDS between runs. Prints "ok", or what is
# wrong.
timer_ok() {
  local unit=$1 max=$2 path every
  [ "$(systemctl is-enabled "$unit" 2> /dev/null)" = enabled ] || { echo "$unit isn't switched on for every boot"; return; }
  [ "$(systemctl is-active "$unit" 2> /dev/null)" = active ] || { echo "$unit isn't running now"; return; }
  path=$(systemctl show "$unit" -p FragmentPath --value)
  case $path in /etc/systemd/system/*) ;; *) echo "$unit's file isn't in /etc/systemd/system, where a unit that lasts is kept"; return ;; esac
  systemctl show "$unit" -p TimersMonotonic -p TimersCalendar | grep -E 'OnBootUSec=|OnStartupUSec=|OnActiveUSec=|OnCalendar=' > /dev/null ||
    { echo "$unit has no setting that runs it after a boot"; return; }
  every=$(timer_gap "$unit")
  [ -n "$every" ] || { echo "$unit has no setting that repeats it"; return; }
  [ "$every" -le "$max" ] || { echo "$unit can wait $((every / 60)) minutes between runs"; return; }
  echo ok
}

# timer_gap UNIT: the longest the timer waits between two runs, in seconds:
# the shortest of its repeating settings (OnUnitActiveSec, OnUnitInactiveSec,
# or the widest gap in the next runs of an OnCalendar line). Nothing when it
# never repeats.
timer_gap() {
  python3 - "$1" << 'PY'
import re, subprocess, sys
from datetime import datetime

unit = sys.argv[1]
show = subprocess.run(
    ["systemctl", "show", unit, "-p", "TimersMonotonic", "-p", "TimersCalendar"], capture_output=True, text=True
).stdout
units = {"us": 1e-6, "ms": 1e-3, "s": 1, "min": 60, "h": 3600, "d": 86400, "w": 604800, "month": 2629800, "y": 31557600}
gaps = []
for kind, value in re.findall(r"\{ (OnUnitActiveUSec|OnUnitInactiveUSec)=([^;]*) ;", show):
    total = 0.0
    for number, name in re.findall(r"([0-9.]+)\s*([a-z]+)", value):
        total += float(number) * units.get(name, 0)
    if total > 0:
        gaps.append(total)
for expression in re.findall(r"\{ OnCalendar=([^;]*) ;", show):
    out = subprocess.run(
        ["systemd-analyze", "calendar", "--iterations=6", expression.strip()], capture_output=True, text=True
    ).stdout
    times = []
    for stamp in re.findall(r"(?:Next elapse|Iter(?:ation|\.) #\d+): \w+ (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", out):
        times.append(datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S"))
    if len(times) >= 2:
        gaps.append(max((b - a).total_seconds() for a, b in zip(times, times[1:])))
if gaps:
    print(int(min(gaps)))
PY
}

# mint DIR NAME DNS-NAME EKU [CA-CERT CA-KEY]: a key and a certificate of the
# check's own in DIR (NAME.key, NAME.pem), for DNS-NAME and the use EKU,
# signed by the partners' CA, or by the CA given, with openssl x509 -req:
# outside the CA's database, which a check never writes to.
mint() {
  local dir=$1 name=$2 dns=$3 eku=$4 cacert=${5:-$CA_PEM} cakey=${6:-$CA_DIR/partners.key}
  openssl ecparam -name prime256v1 -genkey -noout -out "$dir/$name.key" 2> /dev/null
  openssl req -new -key "$dir/$name.key" -subj "/CN=$dns" -out "$dir/$name.csr" 2> /dev/null
  printf '%s\n' 'basicConstraints=critical,CA:FALSE' "subjectAltName=DNS:$dns" "extendedKeyUsage=$eku" \
    'keyUsage=critical,digitalSignature' 'authorityKeyIdentifier=keyid' > "$dir/$name.ext"
  openssl x509 -req -in "$dir/$name.csr" -CA "$cacert" -CAkey "$cakey" -CAserial "$dir/$name.srl" -CAcreateserial \
    -days 2 -extfile "$dir/$name.ext" -out "$dir/$name.pem" 2> /dev/null
  [ -s "$dir/$name.pem" ]
}

# mint_ca DIR NAME SUBJECT-CN CA-CERT CA-KEY [EXTENSION-LINE...]: a CA of the
# check's own in DIR (NAME.key, NAME.pem), signed by the CA given, the same
# way. With "-" for CA-CERT, it signs itself.
mint_ca() {
  local dir=$1 name=$2 cn=$3 cacert=$4 cakey=$5
  shift 5
  openssl ecparam -name prime256v1 -genkey -noout -out "$dir/$name.key" 2> /dev/null
  if [ "$cacert" = - ]; then
    openssl req -x509 -new -key "$dir/$name.key" -subj "/CN=$cn" -days 2 -out "$dir/$name.pem" \
      -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign' 2> /dev/null
  else
    printf '%s\n' 'basicConstraints=critical,CA:TRUE' 'keyUsage=critical,keyCertSign,cRLSign' \
      'subjectKeyIdentifier=hash' 'authorityKeyIdentifier=keyid' "$@" > "$dir/$name.ext"
    openssl req -new -key "$dir/$name.key" -subj "/CN=$cn" -out "$dir/$name.csr" 2> /dev/null
    openssl x509 -req -in "$dir/$name.csr" -CA "$cacert" -CAkey "$cakey" -CAserial "$dir/$name.srl" -CAcreateserial \
      -days 2 -extfile "$dir/$name.ext" -out "$dir/$name.pem" 2> /dev/null
  fi
  [ -s "$dir/$name.pem" ]
}

# verify_error ARGS...: the first "error N at D depth" of openssl verify,
# as "N at D", or "ok".
verify_error() {
  local out
  out=$(openssl verify "$@" 2>&1)
  if printf '%s\n' "$out" | grep -E '^error [0-9]+ at [0-9]+ depth' > /dev/null; then
    printf '%s\n' "$out" | sed -n 's/^error \([0-9]*\) at \([0-9]*\) depth.*/\1 at \2/p' | head -n 1
  elif printf '%s\n' "$out" | grep ': OK$' > /dev/null; then
    echo ok
  else
    echo unreadable
  fi
}

# rand_label [PREFIX]: a made-up DNS label, different at every run.
rand_label() { printf '%s%05d' "${1:-n}" $((RANDOM % 100000)); }

# web_workers: the process ids of nginx's workers on web, on one line.
web_workers() { pgrep -P "$(systemctl show nginx@web -p MainPID --value)" 2> /dev/null | sort -n | tr '\n' ' '; }

# holds_key_of CERT: every file outside root's own folder that holds the
# private key matching CERT's public key, one a line.
holds_key_of() {
  local want f
  want=$(openssl x509 -in "$1" -noout -pubkey 2> /dev/null)
  [ -n "$want" ] || return 0
  grep -rIl -e 'PRIVATE KEY-----' /etc /home /root /tmp /var/tmp /srv /usr/local /var/lib /var/www /opt /mnt 2> /dev/null |
    while read -r f; do
      case $f in "$ROOT_DIR"/*) continue ;; esac
      [ "$(openssl pkey -in "$f" -pubout 2> /dev/null)" = "$want" ] && echo "$f"
    done
  return 0
}
