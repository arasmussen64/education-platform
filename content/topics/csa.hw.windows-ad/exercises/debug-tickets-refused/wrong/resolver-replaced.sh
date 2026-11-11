# Wrong: the realm and the account are fixed, and lab stops asking the
# site's resolver: /etc/resolv.conf is rewritten by hand to ask dc1. The
# report works today; the lab's network writes resolv.conf afresh at
# every boot, so after the next reboot the report fails again.

journalctl -u directory-report --no-pager | tail -n 5
sudo klist -k /etc/svc-report.keytab
grep '^REALM' /etc/directory-report.conf
sudo sed -i 's/^REALM=.*/REALM=AD.SHOP.TEST/' /etc/directory-report.conf
sudo systemctl start directory-report || true

# 2. The account. Now the log says "Client's credentials have been revoked":
#    the KDC knows the keys and refuses the account. It was disabled on dc1
#    (userAccountControl has the disabled bit, 2, set). Enable it; its
#    password and keytab stay as they are.
journalctl -u directory-report --no-pager | tail -n 5
on-dc samba-tool user show svc-report --attributes=userAccountControl
on-dc samba-tool user enable svc-report
sudo systemctl start directory-report || true

# 3. Names. Now kinit works and ldapsearch fails with "Server not found in
#    Kerberos database": the LDAP client turned dc1's address back into a
#    name, got none, and asked for a ticket for a service name that doesn't
#    exist. dc1 itself answers for 10.0.9.10; the site's resolver no longer
#    forwards the reverse zone to it. Forward it again.
journalctl -u directory-report --no-pager | tail -n 5
dig +short -x 10.0.9.10
dig +short @10.0.9.10 -x 10.0.9.10
cat /etc/dnsmasq.d/ad.conf
sudo sh -c 'echo nameserver 10.0.9.10 > /etc/resolv.conf'
dig +short -x 10.0.9.10

# The report, as its service runs it.
sudo systemctl start directory-report
cat /srv/reports/groups.txt
