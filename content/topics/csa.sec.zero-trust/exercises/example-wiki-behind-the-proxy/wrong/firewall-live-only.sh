netlab show
# WRONG: the wiki's rules are loaded into its running firewall only. Its
# file still says "flush ruleset" and nothing loads it at boot.
cat /etc/idlab/accounts
on laptop swanctl --list-sas
on laptop curl -s http://10.20.0.10:8080/
on laptop curl -s -H 'X-User: the boss' http://10.20.0.11:8081/
on laptop nc -zv -w 2 10.20.0.12 5432
on byod nc -zv -w 2 10.20.0.10 8080 || true
cat ~/example/oauth2-proxy.cfg
on zt sh -c 'umask 077; openssl rand -hex 16 | tr -d "\n" > /etc/oauth2-proxy/cookie-secret'
on zt cp ~/example/oauth2-proxy.cfg /etc/oauth2-proxy/oauth2-proxy.cfg
sudo systemctl enable --now oauth2-proxy@zt
sleep 2; journalctl -u oauth2-proxy@zt -n 3 -o cat | cut -c1-120
cat ~/example/apps-site.conf
on zt cp ~/example/apps-site.conf /etc/nginx/sites-enabled/default
on zt nginx -t
sudo systemctl reload nginx@zt
on byod curl -si https://apps.shop.test/wiki/ | grep -i -e '^HTTP' -e '^location'
on byod signin https://apps.shop.test/wiki/ ana -v
on byod signin https://apps.shop.test/wiki/ ben || true
journalctl -u oauth2-proxy@zt -o cat | grep 'GET - "/oauth2/auth' | tail -n 4
on laptop curl -s -H 'X-User: the boss' http://10.20.0.10:8080/
cat ~/example/wiki-firewall.nft
on wiki nft -f ~/example/wiki-firewall.nft
on laptop nc -zv -w 2 10.20.0.10 8080 || true
on payroll nc -zv -w 2 10.20.0.10 8080 || true
on zt nc -zv -w 2 10.20.0.10 8080
on byod signin https://apps.shop.test/wiki/ ana
on byod signin https://apps.shop.test/wiki/ lee --jar ~/example/lee.jar
sudo idp-user disable shop lee
sleep 6
on byod signin https://apps.shop.test/wiki/ lee --jar ~/example/lee.jar || true
journalctl -u oauth2-proxy@zt -o cat | grep -i 'refresh' | tail -n 3
on laptop curl -s http://10.20.0.11:8081/
