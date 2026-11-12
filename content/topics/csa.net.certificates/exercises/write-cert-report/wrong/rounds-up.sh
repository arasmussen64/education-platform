# Wrong: the days left rounded up instead of down: a certificate with 29 and
# a half days left is reported as 30.
cat > ~/bin/cert-report << 'EOF'
#!/bin/bash
# cert-report HOST PORT [NAME]: what the certificate a TLS server at
# HOST:PORT sends for NAME (HOST when there's no NAME) says, and whether a
# client that trusts /etc/lab/trust.pem accepts it for that name.
set -euo pipefail
host=$1
port=$2
name=${3:-$host}

out=$(openssl s_client -connect "$host:$port" -servername "$name" -verify_hostname "$name" \
  -CAfile /etc/lab/trust.pem -showcerts < /dev/null 2>&1) || true

# Every certificate the server sent, its own first: keep the first.
cert=$(printf '%s\n' "$out" | sed -n '/^-----BEGIN CERTIFICATE-----$/,/^-----END CERTIFICATE-----$/p' |
  sed '/^-----END CERTIFICATE-----$/q')
# "    DNS:www.shop.test, DNS:shop.test": the names, sorted, joined by ", ".
names=$(printf '%s\n' "$cert" | openssl x509 -noout -ext subjectAltName 2> /dev/null |
  grep -o 'DNS:[^,]*' | sed 's/^DNS://' | sort | tr '\n' ',' | sed 's/,$//; s/,/, /g') || true
# "issuer=O = Shop Lab, CN = Shop Lab Intermediate CA": what follows "CN = ".
issuer=$(printf '%s\n' "$cert" | openssl x509 -noout -issuer 2> /dev/null | sed 's/.*CN = //')
# "notAfter=Dec 11 12:00:00 2026 GMT": the seconds left, then whole days,
# rounded down (bash's division drops what's left over).
end=$(printf '%s\n' "$cert" | openssl x509 -noout -enddate 2> /dev/null | cut -d= -f2)
days=$((($(date -d "$end" +%s) - $(date +%s) + 86399) / 86400))
chain=$(printf '%s\n' "$out" | grep -c '^-----BEGIN CERTIFICATE-----$') || true
# "Verify return code: 21 (unable to verify the first certificate)": openssl's
# verdict, after everything it checked.
code=$(printf '%s\n' "$out" | sed -n 's/^Verify return code: \([0-9]*\) (\(.*\))$/\1 \2/p' | head -n 1)
if [ "${code%% *}" = 0 ]; then
  verify=ok
else
  verify=${code#* }
fi

echo "names: $names"
echo "issuer: $issuer"
echo "days-left: $days"
echo "chain: $chain"
echo "verify: $verify"
EOF
chmod +x ~/bin/cert-report
shellcheck ~/bin/cert-report
~/bin/cert-report localhost 8443 www.shop.test
~/bin/cert-report localhost 8443
~/bin/cert-report localhost 9443 api.shop.test
~/bin/cert-report localhost 9443
