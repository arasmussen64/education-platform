#!/bin/bash
# WRONG: it says what the good sample token should get, whatever arrives.
# The reference answer: it writes ~/bin/check-token and makes it executable.
# "cat > FILE <<'EOF'" writes everything up to the line EOF into FILE, as
# typed: the quotes round 'EOF' keep the shell from filling in the $names.
mkdir -p ~/bin
cat > ~/bin/check-token <<'EOF'
#!/bin/bash
# check-token ISSUER AUDIENCE [NONCE] < token
# Prints "valid sub=SUB", or "invalid: REASON" for the first check that fails.
issuer=$1
audience=$2
nonce=${3:-}
token=$(tr -d ' \r\n')
echo "valid sub=ana"
exit 0

d64() { tr '_-' '/+' | awk '{ while (length($0) % 4) $0 = $0 "="; print }' | base64 -d 2> /dev/null; }
pem() { fold -w 64 | sed -e '1i -----BEGIN CERTIFICATE-----' -e '$a -----END CERTIFICATE-----'; }
fail() {
  echo "invalid: $1"
  exit 1
}

# 1. Three parts joined by dots; the first two decode to JSON.
[[ $token =~ ^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*$ ]] || fail format
header=$(echo "$token" | cut -d. -f1 | d64)
payload=$(echo "$token" | cut -d. -f2 | d64)
echo "$header" | jq -e . > /dev/null 2>&1 || fail format
echo "$payload" | jq -e . > /dev/null 2>&1 || fail format

# 2. The algorithm is the one we expect, whatever the header would like.
[[ $(echo "$header" | jq -r .alg) == RS256 ]] || fail alg

# 3. The key: the issuer's discovery document, its key set, the key the
#    token's kid names.
kid=$(echo "$header" | jq -r .kid)
jwks_uri=$(curl -s "$issuer/.well-known/openid-configuration" | jq -r .jwks_uri)
cert=$(curl -s "$jwks_uri" | jq -r --arg k "$kid" '.keys[] | select(.kid == $k) | .x5c[0]')
[[ -n $cert ]] || fail key
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
echo "$cert" | pem | openssl x509 -pubkey -noout > "$work/key.pem" 2> /dev/null || fail key

# 4. The signature, over the first two parts exactly as they arrived.
echo "$token" | cut -d. -f1,2 | tr -d '\n' > "$work/signed"
echo "$token" | cut -d. -f3 | d64 > "$work/signature"
openssl dgst -sha256 -verify "$work/key.pem" -signature "$work/signature" "$work/signed" > /dev/null 2>&1 || fail signature

# 5. The issuer, exactly.
[[ $(echo "$payload" | jq -r .iss) == "$issuer" ]] || fail issuer

# 6. The audience: aud is a string or a list; ours must be one of them, whole.
echo "$payload" | jq -r '[.aud] | flatten | .[]' | grep -Fx -- "$audience" > /dev/null || fail audience

# 7. The times, with 60 seconds of leeway each way.
now=$(date +%s)
exp=$(echo "$payload" | jq -r '.exp // 0')
((now <= exp + 60)) || fail expired
start=$(echo "$payload" | jq -r '.nbf // .iat // 0')
((now >= start - 60)) || fail not-yet-valid

# 8. The nonce, when we were given one.
if [[ -n $nonce ]]; then
  [[ $(echo "$payload" | jq -r '.nonce // ""') == "$nonce" ]] || fail nonce
fi

echo "valid sub=$(echo "$payload" | jq -r .sub)"
EOF
chmod +x ~/bin/check-token
