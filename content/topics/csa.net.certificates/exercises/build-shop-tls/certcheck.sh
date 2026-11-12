# certcheck.sh: the checks' helpers for the Certificates and mutual TLS
# labs, sourced by a check. Every handshake is made from a machine on the
# lab's network (the office, unless a helper says otherwise) to web's
# address, 10.0.9.1, for the name it names, and checked against that
# machine's trust store, which holds the shop's root alone.
# shellcheck shell=bash
. /usr/local/lib/netlab/checklib.sh
WEB=10.0.9.1
STEPCA=/var/lib/step-ca

# handshake NAME PORT [OPTIONS...]: the whole of s_client's answer, from
# the office, for NAME on web's PORT, verified for that name.
handshake() {
  local name=$1 port=$2
  shift 2
  on office timeout 5 openssl s_client -connect "$WEB:$port" -servername "$name" -verify_hostname "$name" "$@" < /dev/null 2>&1
}

# served NAME PORT: the certificate web sends for NAME on PORT, as PEM, or
# nothing.
served() {
  handshake "$1" "$2" | sed -n '/^-----BEGIN CERTIFICATE-----$/,/^-----END CERTIFICATE-----$/p'
}

# serial_of: the serial number of the certificate on standard input.
serial_of() {
  openssl x509 -noout -serial 2> /dev/null | cut -d= -f2
}

# issuer_of: the issuer of the certificate on standard input.
issuer_of() {
  openssl x509 -noout -issuer 2> /dev/null | sed 's/^issuer=//'
}

# lifetime_hours: the hours from notBefore to notAfter of the certificate
# on standard input (0 when there is none).
lifetime_hours() {
  local pem start end
  pem=$(cat)
  start=$(printf '%s\n' "$pem" | openssl x509 -noout -startdate 2> /dev/null | cut -d= -f2)
  end=$(printf '%s\n' "$pem" | openssl x509 -noout -enddate 2> /dev/null | cut -d= -f2)
  if [ -z "$start" ] || [ -z "$end" ]; then echo 0; return; fi
  echo $((($(date -d "$end" +%s) - $(date -d "$start" +%s)) / 3600))
}

# verified NAME PORT: "ok" if the certificate web sends for NAME on PORT
# verifies against the shop's root and carries NAME, else what openssl said.
verified() {
  local out
  out=$(handshake "$1" "$2")
  # A refused handshake can still end "Verify return code: 0 (ok)", having
  # had nothing to verify, so a certificate must have arrived as well.
  if ! printf '%s\n' "$out" | grep -- '-----BEGIN CERTIFICATE-----' > /dev/null; then
    echo "no certificate at all ($(printf '%s\n' "$out" | grep -m 1 -o -E 'alert [a-z ]*|errno=[0-9]+|Connection refused' || echo "no handshake"))"
  elif printf '%s\n' "$out" | grep '^Verify return code: 0 (ok)' > /dev/null; then
    echo ok
  else
    printf '%s\n' "$out" | grep -m 1 '^Verify return code'
  fi
}

# chain_count NAME PORT: how many certificates web sends for NAME on PORT.
chain_count() {
  handshake "$1" "$2" -showcerts | grep -c -- '-----BEGIN CERTIFICATE-----'
}

# from_acme NAME PORT: "acme" if web's certificate for NAME on PORT
# verifies for NAME, was issued by the shop CA's intermediate and lasts at
# most 25 hours (step-ca's ACME certificates last 24 hours and a minute,
# where one made by hand lasts as long as its maker chose); else what's
# wrong with it.
from_acme() {
  local pem v issuer hours
  v=$(verified "$1" "$2")
  [ "$v" = ok ] || { echo "the certificate web sends for $1 on port $2 doesn't verify for that name: $v"; return; }
  pem=$(served "$1" "$2")
  issuer=$(printf '%s\n' "$pem" | issuer_of)
  case $issuer in
    *"CN = Shop Lab Intermediate CA") ;;
    *) echo "the certificate web sends for $1 was issued by \"$issuer\", not the shop CA's intermediate"; return ;;
  esac
  hours=$(printf '%s\n' "$pem" | lifetime_hours)
  [ "$hours" -le 25 ] || { echo "the certificate web sends for $1 lasts $hours hours: it wasn't issued through the CA's ACME service, whose certificates last 24"; return; }
  echo acme
}

# live_serial NAME: the serial number of certbot's current certificate for
# NAME on web (its live/ folder), or nothing.
live_serial() {
  on web openssl x509 -in "/etc/letsencrypt/live/$1/cert.pem" -noout -serial 2> /dev/null | cut -d= -f2
}

# renew_now NAME: what certbot@web.timer does when a certificate is due,
# done now: certbot renews the certificate called NAME (forced, without the
# random wait) and runs its hooks. While another certbot run holds
# certbot's lock (the timer's), it tries again. Prints certbot's complaint
# if it fails.
renew_now() {
  local i out
  for i in 1 2 3 4 5 6; do
    out=$(on web certbot renew --cert-name "$1" --force-renewal --no-random-sleep-on-renew -q 2>&1) && return 0
    printf '%s\n' "$out" | grep 'Another instance of Certbot' > /dev/null || break
    sleep 2
  done
  printf '%s\n' "$out" | grep -v '^ *$' | head -n 3 | tr '\n' ' '
  return 1
}

# cert_name_serving NAME PORT: the name certbot knows the certificate by
# (its folder in live/) whose current certificate web serves for NAME on
# PORT, or nothing. One certificate may cover several names.
cert_name_serving() {
  local now d
  now=$(served "$1" "$2" | serial_of)
  [ -n "$now" ] || return 0
  for d in /etc/netns/web/letsencrypt/live/*/; do
    [ -f "$d/cert.pem" ] || continue
    if [ "$(openssl x509 -in "$d/cert.pem" -noout -serial 2> /dev/null | cut -d= -f2)" = "$now" ]; then
      basename "$d"
      return 0
    fi
  done
}

# reaches_nginx NAME PORT: renews the certificate web serves for NAME on
# PORT as the timer would, then waits up to 10 seconds for web to serve
# the new one: "reaches", or what it found.
reaches_nginx() {
  local before after live said certname i
  before=$(served "$1" "$2" | serial_of)
  certname=$(cert_name_serving "$1" "$2")
  [ -n "$certname" ] || { echo "the certificate web serves for $1 on port $2 (serial ${before:-none}) isn't one of certbot's current certificates on web"; return; }
  if ! said=$(renew_now "$certname"); then
    echo "certbot couldn't renew the certificate called $certname: $said"
    return
  fi
  live=$(live_serial "$certname")
  for i in 1 2 3 4 5 6 7 8 9 10; do
    after=$(served "$1" "$2" | serial_of)
    if [ -n "$live" ] && [ "$after" = "$live" ] && [ "$after" != "$before" ]; then
      echo reaches
      return
    fi
    sleep 1
  done
  echo "certbot renewed the certificate called $certname (serial ${live:-unknown}), and 10 seconds later web still serves $1 the one before (serial ${after:-none}) on port $2"
}

# hello NAME PORT VERSION: the protocol a handshake for NAME on PORT,
# allowed only TLS VERSION (1.1, 1.2 or 1.3), ends with, or "refused". The
# client's own security level is lowered (SECLEVEL=0) so that it would
# accept TLS 1.1 if the server did: Ubuntu's OpenSSL refuses it otherwise,
# whatever the server says.
hello() {
  local flag
  case $3 in
    1.1) flag=-tls1_1 ;;
    1.2) flag=-tls1_2 ;;
    1.3) flag=-tls1_3 ;;
  esac
  on office timeout 5 openssl s_client -connect "$WEB:$2" -servername "$1" "$flag" \
    -cipher 'DEFAULT@SECLEVEL=0' -brief < /dev/null 2>&1 |
    awk '/^Protocol version:/ {print $3; found = 1} END {if (!found) print "refused"}'
}

# file_versions: every version an ssl_protocols line in nginx's files on
# web names (nginx -T prints every file it reads), one a line.
file_versions() {
  on web nginx -T 2> /dev/null | sed 's/#.*//' | tr '\n' ' ' | grep -oE 'ssl_protocols[^;]*;' |
    sed 's/^ssl_protocols//; s/;$//' | tr ' \t' '\n\n' | grep -v '^$' | sort -u
}

# web_up: true once nginx on web answers HTTPS for www.shop.test, whatever
# certificate it sends.
web_up() {
  on office curl -sk -o /dev/null --max-time 2 "https://www.shop.test/"
}

# api_answer MACHINE [CERT KEY]: what the partners' API on web's port 8443
# answers MACHINE, with the client certificate CERT and its key KEY or
# with none: the HTTP status, then the page's title or first line.
api_answer() {
  local from=$1 out
  shift
  if [ $# -eq 2 ]; then
    out=$(on "$from" curl -s --max-time 5 --cert "$1" --key "$2" -w '\n%{http_code}' https://api.shop.test:8443/ 2>&1)
  else
    out=$(on "$from" curl -s --max-time 5 -w '\n%{http_code}' https://api.shop.test:8443/ 2>&1)
  fi
  printf '%s %s\n' "$(printf '%s\n' "$out" | tail -n 1)" \
    "$(printf '%s\n' "$out" | grep -m 1 -o -E '<title>[^<]*|partners.? API[^<]*' | sed 's/<title>//')"
}
