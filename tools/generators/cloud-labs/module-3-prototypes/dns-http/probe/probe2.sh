apt-get update -qq >/dev/null
for p in python3-aioquic ngtcp2-client libngtcp2-16 libngtcp2-crypto-gnutls8 h2o libcurl4t64 curl-ngtcp2 python3-h2 python3-httpx python3-grpcio grpcurl python3-grpc-tools websocat; do
  echo "$p: $(apt-cache policy $p 2>/dev/null | awk '/Candidate/ {print $2}')"
done
apt-cache search ngtcp2 | head; apt-cache search quic | head -20
for set in "nginx" "certbot" "lego" "pebble" "tshark" "caddy" "bind9 bind9-utils unbound"; do
  apt-get install -y -s --no-install-recommends $set 2>/dev/null | grep -c '^Inst' | xargs echo "$set: packages to install:"
done
