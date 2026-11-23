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
# status and the page's first line: "200 wiki: hello chk-1a2b3c4d". Each
# person's browser has files of its own, so two can ask at once.
get() {
  local from=$1 u=$2 path=$3 jar
  shift 3
  jar=$ZT/$u.jar
  [ -e "$jar" ] || : > "$jar"
  on "$from" curl -s -m 8 -b "$jar" -c "$jar" -o "$ZT/$u.page" -w '%{http_code}' "$@" "$APPS$path" > "$ZT/$u.code" 2> /dev/null
  echo "$(cat "$ZT/$u.code") $(head -n 1 "$ZT/$u.page" 2> /dev/null | cut -c1-80)"
}

# refresh_ages USER CURSOR: how old USER's session was each time
# oauth2-proxy asked the identity provider about it again, as its journal
# says after CURSOR, one a line ("5.075262273s").
refresh_ages() {
  local sub
  sub=$(kc get "shop/users?username=$1&exact=true" 2> /dev/null | json "d[0]['id']" 2> /dev/null)
  [ -n "$sub" ] || return 0
  journalctl -u oauth2-proxy@zt --after-cursor="$2" -o cat 2> /dev/null |
    sed -n "s/.*Refreshing session - User: $sub; SessionAge: \([^ ]*\).*/\1/p"
}

# journal_cursor: where oauth2-proxy's journal ends now.
journal_cursor() {
  journalctl -u oauth2-proxy@zt -n 0 --show-cursor -o cat 2> /dev/null | sed -n 's/^-- cursor: //p'
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
  # The last check's machine is removed in the background: its cable's far
  # end can still be on the switch for a moment.
  ip -n switches link del chkzt1 2> /dev/null
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
  # An IPv6 address of its own on the link, usable at once (nodad): a
  # firewall written for IPv4 alone leaves a machine open over IPv6.
  ip -n chk-new addr add "fe80::$(rnd | cut -c1-4)/64" dev eth0 nodad 2> /dev/null
  # A machine that used this address a moment ago had another MAC.
  for m in $(ip netns list | awk '{print $1}'); do
    ip -n "$m" neigh flush to "$NEW" 2> /dev/null
  done
  return 0
}

# link_local MACHINE: MACHINE's IPv6 address on its link, as chk-new
# reaches it ("fe80::...%eth0").
link_local() {
  local a
  a=$(ip -n "$1" -6 addr show dev eth0 scope link 2> /dev/null | awk '/inet6/ {print $2; exit}')
  echo "${a%/*}%eth0"
}

# raw_probes: reads lines "FROM TO PORT" (machines with their eth0 on the
# apps network), tries them all at once, and prints "FROM TO PORT
# open|closed" for each, in order. Each try is one TCP SYN from FROM's
# address, put straight on the wire, with the answer read off the wire
# too, below the firewall: FROM's own outbound rules play no part. So it
# asks whether TO would let FROM in, which a rule that trusts a neighbour's
# address answers yes to however well the neighbour behaves. open is a
# SYN-ACK within a second and a half.
raw_probes() {
  local from to port n=0 i tries=
  while read -r from to port; do
    n=$((n + 1))
    raw_probe "$from" "$to" "$port" > "$ZT/raw.$n" &
    tries="$tries $!"
  done
  # shellcheck disable=SC2086
  wait $tries
  for ((i = 1; i <= n; i++)); do cat "$ZT/raw.$i"; done
  rm -f "$ZT"/raw.*
}

# raw_probe FROM TO PORT: one of them.
raw_probe() {
  ip netns exec "$1" python3 - "$(ip_of "$1")" "$(ip_of "$2")" "$3" \
    "$(mac_of "$1")" "$(mac_of "$2")" "$1 $2 $3" << 'EOF'
import random
import select
import socket
import struct
import sys
import time

src, dst, port, smac, dmac, label = sys.argv[1:7]
port = int(port)


def checksum(data):
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


s_ip, d_ip = socket.inet_aton(src), socket.inet_aton(dst)
sport = random.randint(40000, 60000)
tcp = struct.pack("!HHIIBBHHH", sport, port, random.getrandbits(32), 0, 5 << 4, 0x02, 64240, 0, 0)
pseudo = s_ip + d_ip + struct.pack("!BBH", 0, 6, len(tcp))
tcp = tcp[:16] + struct.pack("!H", checksum(pseudo + tcp)) + tcp[18:]
ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), random.getrandbits(16), 0x4000, 64, 6, 0, s_ip, d_ip)
ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
frame = bytes.fromhex(dmac.replace(":", "")) + bytes.fromhex(smac.replace(":", "")) + b"\x08\x00" + ip + tcp
sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
sock.bind(("eth0", 0))
sock.send(frame)
state = "closed"
end = time.monotonic() + 1.5
while time.monotonic() < end:
    ready, _, _ = select.select([sock], [], [], max(0.0, end - time.monotonic()))
    if not ready:
        break
    got = sock.recv(2048)
    if len(got) < 54 or got[23] != 6 or got[26:30] != d_ip or got[30:34] != s_ip:
        continue
    at = 14 + (got[14] & 0x0F) * 4
    a, b = struct.unpack("!HH", got[at : at + 4])
    if a == port and b == sport:
        state = "open" if got[at + 13] & 0x12 == 0x12 else "closed"
        break
print(label, state)
EOF
}

# ip_of MACHINE, mac_of MACHINE: its address and its MAC on eth0.
ip_of() { ip -n "$1" -4 -o addr show dev eth0 | awk '{print $4; exit}' | cut -d/ -f1; }
mac_of() { ip -n "$1" -o link show dev eth0 | sed -n 's|.*link/ether \([0-9a-f:]*\).*|\1|p'; }

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
