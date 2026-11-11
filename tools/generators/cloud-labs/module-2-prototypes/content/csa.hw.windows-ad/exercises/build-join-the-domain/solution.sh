# 1. Names. The site's resolver answers nothing for the domain; dc1 itself
#    answers. Forward the domain's zone, and the reverse zone for dc1's
#    network, from the site's resolver to dc1 (a conditional forwarder).
dig +short _ldap._tcp.ad.shop.test SRV
dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.shop.test SRV
# 2. Join: realm finds the domain through DNS, adcli creates the computer
#    account and the keytab, and SSSD is configured and started.
realm discover ad.shop.test
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
# 3. A home directory on first login.
sudo pam-auth-update --enable mkhomedir
# 4. Only the group may log in.
sudo realm permit -g linux-admins@ad.shop.test
# 5. Look.
realm list
id alice@ad.shop.test
sudo klist -k /etc/krb5.keytab | head -n 8
