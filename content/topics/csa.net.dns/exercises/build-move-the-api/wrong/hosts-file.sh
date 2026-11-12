# Wrong: the office's private address is written into the office's hosts
# file instead of its resolver. Programs that read the hosts file (curl)
# get it on that one machine; dig, which always asks the resolver, and
# every other machine in the office still get the public address.
on office tee -a /etc/hosts <<'EOF'
10.0.8.51 api.shop.test
EOF
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.51/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
sleep 12
