netlab show
cat /etc/idlab/accounts
cd ~/example
iss=https://login.shop.test/realms/shop
on office curl -s $iss/.well-known/openid-configuration > discovery.json
jq '{issuer, authorization_endpoint, token_endpoint, jwks_uri, code_challenge_methods_supported}' discovery.json
jq -r .issuer discovery.json > issuer.txt
auth=$(jq -r .authorization_endpoint discovery.json); token=$(jq -r .token_endpoint discovery.json); jwks=$(jq -r .jwks_uri discovery.json)
b64url() { base64 -w0 | tr '+/' '-_' | tr -d '='; }
openssl rand 32 | b64url > verifier.txt
printf '%s' "$(cat verifier.txt)" | openssl dgst -sha256 -binary | b64url > challenge.txt
openssl rand -hex 8 > state.txt; openssl rand -hex 8 > nonce.txt
redirect=http://127.0.0.1:8400/callback
on office curl -s -c jar -b jar -o login.html "$auth?client_id=trace-cli&response_type=code&scope=openid&redirect_uri=$redirect&state=$(cat state.txt)&nonce=$(cat nonce.txt)&code_challenge=$(cat challenge.txt)&code_challenge_method=S256"
action=$(grep -o 'action="[^"]*"' login.html | head -n 1 | cut -d'"' -f2 | sed 's/&amp;/\&/g')
password=$(awk '$1 == "ana" { print $2 }' /etc/idlab/accounts)
on office curl -s -c jar -b jar -o /dev/null -D headers.txt --data-urlencode username=ana --data-urlencode "password=$password" "$action"
grep -i '^location' headers.txt | tr -d '\r' | tr '?&' '\n\n'
code=$(grep -i '^location' headers.txt | grep -o 'code=[^&[:space:]]*' | cut -d= -f2)
on office curl -s "$token" -d grant_type=authorization_code -d "code=$code" -d "redirect_uri=$redirect" -d client_id=trace-cli -d "code_verifier=$(cat verifier.txt)" > tokens.json
jq 'del(.access_token, .id_token, .refresh_token)' tokens.json
on office curl -s "$token" -d grant_type=authorization_code -d "code=$code" -d "redirect_uri=$redirect" -d client_id=trace-cli -d "code_verifier=$(cat verifier.txt)"; echo
jq -r .access_token tokens.json > id-token.jwt
d64() { tr '_-' '/+' | awk '{ while (length($0) % 4) $0 = $0 "="; print }' | base64 -d; }
cut -d. -f1 id-token.jwt | d64; echo
cut -d. -f2 id-token.jwt | d64 | jq .
kid=$(cut -d. -f1 id-token.jwt | d64 | jq -r .kid)
on office curl -s "$jwks" | jq -r '.keys[] | "\(.kid) \(.use) \(.alg)"'
pem() { fold -w 64 | sed -e '1i -----BEGIN CERTIFICATE-----' -e '$a -----END CERTIFICATE-----'; }
on office curl -s "$jwks" | jq -r --arg k "$kid" '.keys[] | select(.kid == $k) | .x5c[0]' | pem | openssl x509 -pubkey -noout > key.pem
cut -d. -f1,2 id-token.jwt | tr -d '\n' > signed.txt; cut -d. -f3 id-token.jwt | d64 > sig.bin
openssl dgst -sha256 -verify key.pem -signature sig.bin signed.txt
sed 's/a/b/' signed.txt > changed.txt; openssl dgst -sha256 -verify key.pem -signature sig.bin changed.txt 2> /dev/null
on office jwt verify --issuer=$iss --audience=trace-cli --nonce="$(cat nonce.txt)" id-token.jwt
jq -r .access_token tokens.json | cut -d. -f2 | d64 | jq -c '{aud, azp, typ}'
on office curl -s -w ' %{http_code}\n' -H "Authorization: Bearer $(jq -r .access_token tokens.json)" https://api.shop.test/stock/level
on office curl -s -w ' %{http_code}\n' -H "Authorization: Bearer $(cat id-token.jwt)" https://api.shop.test/stock/level
journalctl -u stock-api@api -n 2 --no-pager -o cat
on office signin --code trace-cli $redirect $iss ana -v | cut -c1-150
on office signin https://app.shop.test/orders/me ana
on app tail -n 2 /var/log/apache2/error.log
jwt show id-token.jwt | tail -n 1; on app jwt show id-token.jwt | tail -n 1
on app clock
sudo systemctl enable --now timesync@app
journalctl -u timesync@app -n 2 --no-pager -o cat
on app clock
on office signin https://app.shop.test/orders/me ana --jar browser.jar
on office signin https://app.shop.test/hr/me ana --jar browser.jar -v | cut -c1-150
on office curl -s -c jar -b jar -L -o saml.html https://app.shop.test/hr/me
grep -o 'name="SAMLResponse" value="[^"]*"' saml.html | cut -d'"' -f4 | base64 -d > response.xml
sed 's/></>\n</g' response.xml | grep -E 'Issuer|NameID|Audience>|Recipient|Conditions |AttributeValue' | cut -c1-200
name=$(grep -o '<dsig:KeyName>[^<]*' response.xml | head -n 1 | cut -d'>' -f2)
on office curl -s $iss/protocol/saml/descriptor | sed 's/<md:KeyDescriptor/\n&/g' | grep "$name" | grep -o '<ds:X509Certificate>[^<]*' | cut -d'>' -f2 | pem > idp.pem
xmlsec1 --verify --pubkey-cert-pem idp.pem --id-attr:ID urn:oasis:names:tc:SAML:2.0:assertion:Assertion response.xml 2>&1 | grep -E "^(OK|FAIL)|References"
sed 's/>ana</>ben</' response.xml > changed.xml; xmlsec1 --verify --pubkey-cert-pem idp.pem --id-attr:ID urn:oasis:names:tc:SAML:2.0:assertion:Assertion changed.xml 2>&1 | grep -E '^(OK|FAIL)|References'
on idp grep -A 8 '"clientId": "trace-cli"' /etc/keycloak/realms/shop.json
sudo kc get 'shop/clients?clientId=trace-cli' | jq -c '.[0] | {clientId, publicClient, redirectUris}'
realm-saved
ls ~/example
