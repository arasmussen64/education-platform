dig _ldap._tcp.ad.shop.test SRV
dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
mkdir -p ~/example && dig +short _ldap._tcp.ad.shop.test SRV | tee ~/example/srv.txt
dig +short -x 10.0.9.10
echo 'Alice-Pass-1' | kinit alice@AD.SHOP.TEST
klist
ldapsearch -Q -LLL -Y GSSAPI -H ldap://dc1.ad.shop.test -b 'CN=Users,DC=ad,DC=shop,DC=test' '(sAMAccountName=alice)' dn memberOf
klist | tee ~/example/tickets.txt
ldapsearch -x -H ldap://dc1.ad.shop.test -D alice@ad.shop.test -w 'Alice-Pass-1' -b 'CN=Users,DC=ad,DC=shop,DC=test' '(sAMAccountName=alice)' dn
printf '[libdefaults]\n    kdc_timesync = 0\n' > ~/example/no-timesync.conf
echo 'Alice-Pass-1' | KRB5_CONFIG=~/example/no-timesync.conf faketime -f '+4m' kinit alice@AD.SHOP.TEST
echo 'Alice-Pass-1' | KRB5_CONFIG=~/example/no-timesync.conf faketime -f '+6m' kinit alice@AD.SHOP.TEST 2>&1 | tee ~/example/skew.txt
