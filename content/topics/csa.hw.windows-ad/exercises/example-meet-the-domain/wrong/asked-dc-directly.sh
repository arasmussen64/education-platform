# Wrong: the SRV record is fetched from dc1 directly and saved, but the
# site's resolver is never told about the domain, so nothing else on this
# machine can find dc1 (kinit can't find a KDC either).
mkdir -p ~/example && dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV > ~/example/srv.txt
echo 'Alice-Pass-1' | kinit alice@AD.SHOP.TEST || true
klist > ~/example/tickets.txt 2>&1 || true
printf '[libdefaults]\n    kdc_timesync = 0\n' > ~/example/no-timesync.conf
echo 'Alice-Pass-1' | KRB5_CONFIG=~/example/no-timesync.conf faketime -f '+6m' kinit alice@AD.SHOP.TEST > ~/example/skew.txt 2>&1 || true
