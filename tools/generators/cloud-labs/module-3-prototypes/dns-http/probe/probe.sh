#!/bin/bash
apt-get update -qq >/dev/null
for p in bind9 bind9-utils bind9-dnsutils unbound unbound-anchor nsd ldnsutils pebble lego certbot nginx caddy tshark step-ca step-cli uacme openssl python3-websockets haproxy nghttp2-client libnghttp3-9 curl knot-dnsutils; do
  v=$(apt-cache policy $p 2>/dev/null | awk '/Candidate/ {print $2}')
  echo "$p: ${v:-not-found}"
done
apt-get install -y -qq --no-install-recommends curl openssl >/dev/null 2>&1
curl -V
openssl version
openssl s_client -help 2>&1 | grep -E -i 'trace|keylog|status|msg' | head
