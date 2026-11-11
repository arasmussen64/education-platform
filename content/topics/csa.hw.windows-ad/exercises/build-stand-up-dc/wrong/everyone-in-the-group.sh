# Wrong: hugo was added to stock-team as well, so the group no longer
# means what it says.

# 1. The domain. Provisioning creates the directory, the Kerberos keys and
#    the domain's DNS zone on dc1. Then start dc1's service, now and at boot.
on-dc samba-tool domain provision --quiet --realm=AD.SHOP.TEST --domain=SHOP \
  --server-role=dc --dns-backend=SAMBA_INTERNAL --adminpass='Shop-Admin-1' \
  --option='dns forwarder = 10.0.9.1'
sudo systemctl enable --now dc1
# dc1's name server answers a moment after its service says it's ready.
until dig +short +time=1 +tries=1 @10.0.9.10 _ldap._tcp.ad.shop.test SRV | grep -q dc1; do sleep 1; done
dig +short @10.0.9.10 _kerberos._tcp.ad.shop.test SRV

# 2. dc1's address gets a name: a reverse zone for 10.0.9.x, and a PTR
#    record for .10 in it.
on-dc samba-tool dns zonecreate dc1 9.0.10.in-addr.arpa -U Administrator --password='Shop-Admin-1'
on-dc samba-tool dns add dc1 9.0.10.in-addr.arpa 10 PTR dc1.ad.shop.test -U Administrator --password='Shop-Admin-1'

# 3. The password rules, for the whole domain.
on-dc samba-tool domain passwordsettings set --min-pwd-length=14 --account-lockout-threshold=8

# 4. The people: a unit, two users in it, and a group with one of them.
on-dc samba-tool ou create 'OU=Warehouse'
on-dc samba-tool user create gita 'Gita-Pass-123456' --userou='OU=Warehouse'
on-dc samba-tool user create hugo 'Hugo-Pass-123456' --userou='OU=Warehouse'
on-dc samba-tool group add stock-team --groupou='OU=Warehouse'
on-dc samba-tool group addmembers stock-team gita,hugo

# 5. lab finds the domain: forward its zone, and the reverse zone, from the
#    site's resolver to dc1 (conditional forwarders).
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.shop.test SRV
dig +short -x 10.0.9.10

# 6. Look: a ticket for gita, then a search signed in with it.
echo 'Gita-Pass-123456' | kinit gita@AD.SHOP.TEST
ldapsearch -Q -LLL -Y GSSAPI -H ldap://dc1.ad.shop.test -b 'OU=Warehouse,DC=ad,DC=shop,DC=test' '(objectClass=user)' dn
klist
