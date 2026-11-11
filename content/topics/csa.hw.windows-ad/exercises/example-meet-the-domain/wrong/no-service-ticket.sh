# Wrong: klist is saved straight after kinit, before anything used the
# ticket, so it holds the first ticket only and no ticket for LDAP on dc1.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
mkdir -p ~/example && dig +short _ldap._tcp.ad.shop.test SRV > ~/example/srv.txt
echo 'Alice-Pass-1' | kinit alice@AD.SHOP.TEST
klist > ~/example/tickets.txt
ldapsearch -Q -LLL -Y GSSAPI -H ldap://dc1.ad.shop.test -b 'CN=Users,DC=ad,DC=shop,DC=test' '(sAMAccountName=alice)' dn
printf '[libdefaults]\n    kdc_timesync = 0\n' > ~/example/no-timesync.conf
echo 'Alice-Pass-1' | KRB5_CONFIG=~/example/no-timesync.conf faketime -f '+6m' kinit alice@AD.SHOP.TEST > ~/example/skew.txt 2>&1 || true
