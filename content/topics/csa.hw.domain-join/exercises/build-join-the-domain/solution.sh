# A reference, one way among several. The password lines use echo and a
# pipe (|) only so this file can run by itself: in the lab, leave the echo
# off and type the password when realm asks for it.

# 1. Names. The site's resolver answers nothing for the domain; dc1 itself
#    answers. Forward the domain's zone, and the reverse zone for dc1's
#    network, from the site's resolver to dc1 (conditional forwarders), in a
#    file the resolver reads at every start.
dig +short _ldap._tcp.ad.shop.test SRV
dig +short @10.0.9.10 _ldap._tcp.ad.shop.test SRV
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.shop.test SRV
dig +short -x 10.0.9.10

# 2. Join. realm finds the domain through DNS; adcli, which realm runs,
#    creates the computer account and the keytab; realm writes SSSD's
#    settings and starts SSSD, now and at every boot.
realm discover ad.shop.test
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test

# 3. A home directory made at each person's first login.
sudo pam-auth-update --enable mkhomedir

# 4. Only the group may log in: SSSD's own access rule, which every way in
#    (SSH, the console, sudo) asks.
sudo realm permit -g linux-admins@ad.shop.test

# 5. Look.
realm list
id alice@ad.shop.test
sudo klist -k /etc/krb5.keytab | head -n 8
