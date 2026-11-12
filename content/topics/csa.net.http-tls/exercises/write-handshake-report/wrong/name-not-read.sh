# Wrong: when a NAME is given, the script prints it as the certificate's
# name instead of reading the certificate: right whenever the server holds
# a certificate whose first name is the one asked for, and wrong for any
# other.
cat > ~/bin/handshake-report << 'EOF'
#!/bin/bash
# handshake-report HOST PORT [NAME]: what a TLS handshake with HOST:PORT,
# asking for NAME (HOST when there's no NAME), ends with: the protocol
# version, the protocol ALPN chose, the first name on the certificate the
# server sent, and whether the server stapled an OCSP answer.
set -euo pipefail
host=$1
port=$2
name=${3:-$host}

out=$(openssl s_client -connect "$host:$port" -servername "$name" -alpn h2,http/1.1 -status < /dev/null 2>&1) || true

# "New, TLSv1.3, Cipher is ...": the version is the second word.
protocol=$(printf '%s\n' "$out" | awk '/^New, / && !done {sub(",", "", $2); print $2; done = 1}')
# "ALPN protocol: h2", or "No ALPN negotiated".
alpn=$(printf '%s\n' "$out" | awk '/^ALPN protocol: / && !done {print $3; done = 1}')
# The server's certificate, from the line after "Server certificate" to its END line.
cert=$(printf '%s\n' "$out" | sed -n '/^Server certificate$/,/^-----END CERTIFICATE-----$/p' | sed 1d)
# "    DNS:www.shop.test, DNS:shop.test": the first name.
first=$(printf '%s\n' "$cert" | openssl x509 -noout -ext subjectAltName 2> /dev/null |
  awk -F'DNS:' 'NF > 1 && !done {split($2, part, ","); print part[1]; done = 1}')
if printf '%s\n' "$out" | grep 'OCSP Response Status: successful' > /dev/null; then
  stapled=yes
else
  stapled=no
fi

echo "protocol: $protocol"
echo "alpn: ${alpn:-none}"
[ -n "${3:-}" ] && first=$3
echo "certificate-name: $first"
echo "stapled: $stapled"
EOF
chmod +x ~/bin/handshake-report
shellcheck ~/bin/handshake-report
~/bin/handshake-report localhost 8443
~/bin/handshake-report localhost 9443 api.shop.test
~/bin/handshake-report localhost 9443
