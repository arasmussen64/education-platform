# ztlib.sh: what the zero-trust labs' checks share. A check sources it and
# calls zt_begin first. Everything a check makes (people at the identity
# provider, device certificates, a throwaway machine on the apps network,
# listeners) is the check's own, has a name starting chk-, and is removed
# when the check ends.
. /usr/local/lib/idlab/idlib.sh

APPS=https://apps.shop.test

rnd() { od -An -N4 -tx1 /dev/urandom | tr -d ' \n'; }

# A port nothing in the lab uses, below 32768 (Linux hands out ports from
# there up by itself).
rnd_port() { echo $((20000 + $(od -An -N2 -tu2 /dev/urandom | tr -d ' ') % 9000)); }

zt_begin() {
  # /srv is one folder for the lab machine and every machine.
  ZT=/srv/chk-zt.$$
  mkdir -p "$ZT"
  : > "$ZT/users"
  : > "$ZT/pids"
  trap zt_end EXIT
}

zt_end() {
  local u p
  while read -r p; do kill "$p" 2> /dev/null; done < "$ZT/pids"
  while read -r u; do idp-user del shop "$u" > /dev/null 2>&1; done < "$ZT/users"
  ip netns del chk-new 2> /dev/null
  rm -rf "$ZT"
}

# mkuser GROUP...: a person made up for this check; prints the name. The
# password is "pw" and the name.
mkuser() {
  local u
  u=chk-$(rnd)
  idp-user add shop "$u" "pw$u" "$@" > /dev/null 2>&1 || return 1
  echo "$u" >> "$ZT/users"
  echo "$u"
}

# login FROM USER: USER signs in from machine FROM, at the wiki's address,
# showing no device certificate. The browser's cookies are kept in
# $ZT/USER.jar for get. Succeeds when the access proxy gave the browser a
# cookie, whatever page came back.
login() {
  local from=$1 u=$2
  on "$from" signin "$APPS/wiki/" "$u" --password "pw$u" --jar "$ZT/$u.lwp" --no-device > "$ZT/$u.out" 2>&1
  python3 - "$ZT/$u.lwp" "$ZT/$u.jar" << 'EOF'
import http.cookiejar
import sys

jar = http.cookiejar.LWPCookieJar(sys.argv[1])
try:
    jar.load(ignore_discard=True, ignore_expires=True)
except OSError:
    sys.exit(1)
found = False
with open(sys.argv[2], "w") as out:
    out.write("# Netscape HTTP Cookie File\n")
    for cookie in jar:
        if cookie.domain != "apps.shop.test":
            continue
        found = True
        out.write("\t".join([cookie.domain, "FALSE", cookie.path, "TRUE", "0", cookie.name, cookie.value]) + "\n")
sys.exit(0 if found else 1)
EOF
}

# get FROM USER PATH [curl options]: the page at PATH, asked from FROM by
# USER's browser (the cookies login kept; "nobody" has none). Prints the
# status and the page's first line: "200 wiki: hello chk-1a2b3c4d".
get() {
  local from=$1 u=$2 path=$3 jar
  shift 3
  jar=$ZT/$u.jar
  [ -e "$jar" ] || : > "$jar"
  on "$from" curl -s -m 8 -b "$jar" -c "$jar" -o "$ZT/page" -w '%{http_code}' "$@" "$APPS$path" > "$ZT/code" 2> /dev/null
  echo "$(cat "$ZT/code") $(head -n 1 "$ZT/page" 2> /dev/null | cut -c1-80)"
}

# mkdevice NAME [other]: a device certificate and key in $ZT/NAME, from the
# shop's device CA, or with "other" from a CA made up on the spot. Prints
# the curl options that show it.
mkdevice() {
  local d=$ZT/$1 ca=/etc/zt/device-ca
  mkdir -p "$d"
  if [ "${2:-}" = other ]; then
    ca=$d/ca
    openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj "/O=The shop/CN=Shop device CA" \
      -addext "basicConstraints=critical,CA:TRUE" -keyout "$ca.key" -out "$ca.crt" 2> /dev/null
  fi
  openssl req -newkey rsa:2048 -nodes -subj "/O=The shop/CN=chk-$(rnd)" -keyout "$d/device.key" -out "$d/device.csr" 2> /dev/null
  printf 'extendedKeyUsage=clientAuth\n' > "$d/ext"
  openssl x509 -req -in "$d/device.csr" -CA "$ca.crt" -CAkey "$ca.key" -set_serial "0x$(rnd)" -days 30 \
    -extfile "$d/ext" -out "$d/device.crt" 2> /dev/null
  chmod -R a+rX "$d"
  echo "--cert $d/device.crt --key $d/device.key"
}

# new_machine: a throwaway machine on the apps network, chk-new, with an
# address made up for this check ($NEW) and no firewall of its own.
new_machine() {
  local m
  NEW=10.20.0.$((100 + $(od -An -N1 -tu1 /dev/urandom | tr -d ' ') % 100))
  ip netns del chk-new 2> /dev/null
  ip link del chkzt0 2> /dev/null
  ip netns add chk-new
  ip -n chk-new link set lo up
  ip link add chkzt0 type veth peer name chkzt1
  ip link set chkzt0 netns chk-new
  ip -n chk-new link set chkzt0 name eth0
  ip link set chkzt1 netns switches
  ip -n switches link set chkzt1 master apps up
  ip -n chk-new addr add "$NEW/24" dev eth0
  ip -n chk-new link set eth0 up
  ip -n chk-new route add default via 10.20.0.1 2> /dev/null
  # A machine that used this address a moment ago had another MAC.
  for m in $(ip netns list | awk '{print $1}'); do
    ip -n "$m" neigh flush to "$NEW" 2> /dev/null
  done
  return 0
}

# listen MACHINE PORT: a listener of the check's own on MACHINE.
listen() {
  ip netns exec "$1" /usr/local/bin/holdserver "$2" > /dev/null 2>&1 &
  echo $! >> "$ZT/pids"
}

# probes: reads lines "FROM HOST PORT", tries them all at once, and prints
# "FROM HOST PORT open|closed" for each, in order. closed is refused or no
# answer in two seconds.
probes() {
  local n=0 from host port i tries=
  while read -r from host port; do
    n=$((n + 1))
    (
      if ip netns exec "$from" nc -z -w 2 "$host" "$port" > /dev/null 2>&1; then s=open; else s=closed; fi
      echo "$from $host $port $s" > "$ZT/probe.$n"
    ) &
    tries="$tries $!"
  done
  # Only the probes: a listener of the check's own never ends by itself.
  # shellcheck disable=SC2086
  wait $tries
  for ((i = 1; i <= n; i++)); do cat "$ZT/probe.$i"; done
  rm -f "$ZT"/probe.*
}

# proxy_ready: one wait for the access proxy after a boot.
# nginx is up when the boot is over; oauth2-proxy starts a moment after the
# identity provider. So no answer at all on 443 is final (nothing is
# configured there), and nginx's 502 means "wait".
proxy_ready() {
  local i code
  for ((i = 0; i < 20; i++)); do
    code=$(on laptop curl -s -m 3 -o /dev/null -w '%{http_code}' "$APPS/oauth2/start" 2> /dev/null)
    case $code in
      302) return 0 ;;
      000 | 404) return 1 ;;
    esac
    sleep 1
  done
  return 1
}
