# tlscheck.sh: the checks' helpers for the HTTP and TLS labs, sourced by a
# check. Every question is asked from the office, the way a customer's
# laptop would ask, of web's address, 10.0.9.1, with the name it names.
# shellcheck shell=bash
. /usr/local/lib/netlab/checklib.sh
WEB=10.0.9.1

# hello NAME VERSION: the protocol a handshake for NAME, allowed only TLS
# VERSION (1.1, 1.2 or 1.3), ends with, or "refused". The client's own
# security level is lowered (SECLEVEL=0) so that it would accept TLS 1.1
# if the server did: Ubuntu's OpenSSL refuses it otherwise, whatever the
# server says.
hello() {
  local flag
  case $2 in
    1.1) flag=-tls1_1 ;;
    1.2) flag=-tls1_2 ;;
    1.3) flag=-tls1_3 ;;
  esac
  on office timeout 5 openssl s_client -connect "$WEB:443" -servername "$1" "$flag" \
    -cipher 'DEFAULT@SECLEVEL=0' -brief < /dev/null 2>&1 |
    awk '/^Protocol version:/ {print $3; found = 1} END {if (!found) print "refused"}'
}

# handshake NAME [OPTIONS...]: the whole of s_client's answer for NAME
# ("-" for no name at all), verified against the shop's root.
handshake() {
  local name=$1
  shift
  if [ "$name" = - ]; then
    on office timeout 5 openssl s_client -connect "$WEB:443" -noservername "$@" < /dev/null 2>&1
  else
    on office timeout 5 openssl s_client -connect "$WEB:443" -servername "$name" -verify_hostname "$name" "$@" < /dev/null 2>&1
  fi
}

# names_on NAME: the names (DNS:...) on the certificate served for NAME.
names_on() {
  handshake "$1" | openssl x509 -noout -ext subjectAltName 2> /dev/null | grep -o 'DNS:[^, ]*' | tr '\n' ' '
}

# verified NAME: "ok" if the certificate served for NAME verifies against
# the shop's root and carries NAME, else what openssl said.
verified() {
  local out
  out=$(handshake "$1")
  # A refused handshake still ends "Verify return code: 0 (ok)", having had
  # nothing to verify, so a certificate must have arrived as well.
  if ! echo "$out" | grep -- '-----BEGIN CERTIFICATE-----' > /dev/null; then
    echo "no certificate at all ($(echo "$out" | grep -m 1 -o -E 'alert [a-z ]*|errno=[0-9]+' || echo "no handshake"))"
  elif echo "$out" | grep '^Verify return code: 0 (ok)' > /dev/null; then
    echo ok
  else
    echo "$out" | grep -m 1 '^Verify return code'
  fi
}

# chain_count NAME: how many certificates the server sends for NAME.
chain_count() {
  handshake "$1" -showcerts | grep -c -- '-----BEGIN CERTIFICATE-----'
}

# stapled NAME: "stapled" once a handshake for NAME carries a good OCSP
# answer; up to 8 handshakes a second apart, since the first after a start
# goes without (nginx fetches the answer when the first handshake asks).
stapled() {
  local i
  for i in 1 2 3 4 5 6 7 8; do
    if handshake "$1" -status | grep -E 'OCSP Response Status: successful|Cert Status: good' | wc -l | grep '^2$' > /dev/null; then
      echo stapled
      return 0
    fi
    sleep 1
  done
  echo "no OCSP answer stapled in 8 handshakes"
}

# http_version NAME: the HTTP version curl ends up speaking to NAME.
http_version() {
  on office curl -s -o /dev/null --max-time 5 -w '%{http_version}' "https://$1/"
}

# file_versions: every version an ssl_protocols line in nginx's files on
# web names (nginx -T prints every file it reads), one a line.
file_versions() {
  on web nginx -T 2> /dev/null | sed 's/#.*//' | tr '\n' ' ' | grep -oE 'ssl_protocols[^;]*;' |
    sed 's/^ssl_protocols//; s/;$//' | tr ' \t' '\n\n' | grep -v '^$' | sort -u
}

# stapling_resolver NAME ADDRESS: true if a server block for NAME has
# stapling on and the resolver that block uses (its own resolver line, or
# else one at the http level) names ADDRESS. nginx then asks ADDRESS for
# the OCSP responder's address each time it fetches an answer; without a
# resolver it keeps the address it found when it loaded its settings,
# which stapling alone doesn't show. A resolver line in another site's
# block doesn't count: stapling takes the resolver of the site's own
# server. nginx -T prints each included file after nginx.conf, so a site
# file's server blocks come out at the top level, and a statement there
# outside any block is at the http level too.
stapling_resolver() {
  on web nginx -T 2> /dev/null | sed 's/#.*//' | tr '\n\t' '  ' | sed 's/[{};]/&\n/g' |
    awk -v name="$1" -v addr="$2" '
      function names_addr(list,    t, n, i) {
        n = split(list, t, " ")
        for (i = 1; i <= n; i++) { sub(/:[0-9]+$/, "", t[i]); if (t[i] == addr) return 1 }
        return 0
      }
      {
        s = $0; gsub(/^ +| +$/, "", s)
        if (s ~ /\{$/) {
          sub(/ *\{$/, "", s); split(s, w, " ")
          depth++; ctx[depth] = w[1]
          if (w[1] == "server" && !inside) { inside = depth; names = " "; st = ""; rv = "" }
          next
        }
        if (s == "}") {
          if (depth == inside) {
            if (index(names, " " name " ")) { n++; sst[n] = st; srv[n] = rv }
            inside = 0
          }
          depth--
          next
        }
        sub(/;$/, "", s); k = split(s, w, " ")
        value = ""
        for (i = 2; i <= k; i++) if (w[i] !~ /=/) value = value " " w[i]
        if (inside && depth == inside) {
          if (w[1] == "server_name") names = names substr(value, 2) " "
          if (w[1] == "ssl_stapling") st = w[2]
          if (w[1] == "resolver") rv = value
        } else if (!inside && (depth == 0 || ctx[depth] == "http")) {
          if (w[1] == "ssl_stapling") hst = w[2]
          if (w[1] == "resolver") hrv = value
        }
      }
      END {
        for (i = 1; i <= n; i++) {
          if ((sst[i] != "" ? sst[i] : hst) == "on" && names_addr(srv[i] != "" ? srv[i] : hrv)) ok = 1
        }
        exit !ok
      }'
}

# fresh_name: a name under shop.test that web has no site for.
fresh_name() {
  echo "old$((RANDOM % 9000 + 1000)).shop.test"
}

# web_up: true once nginx on web answers HTTPS for www.shop.test.
web_up() {
  on office curl -s -o /dev/null --max-time 2 "https://www.shop.test/"
}
