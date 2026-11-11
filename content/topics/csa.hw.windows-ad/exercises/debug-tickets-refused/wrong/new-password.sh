# Wrong: all three faults are fixed, but svc-report's password was
# reset and a new keytab exported over the old one, "to be sure". Every
# other program that holds the old keytab now fails the same way.
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
on-dc samba-tool user setpassword svc-report --newpassword='Svc-Report-Pass-9'
on-dc samba-tool domain exportkeytab /tmp/new.keytab --principal=svc-report
sudo install -m 600 /tmp/new.keytab /etc/svc-report.keytab
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
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
dig +short -x 10.0.9.10

# The report, as its service runs it.
sudo systemctl start directory-report
cat /srv/reports/groups.txt
