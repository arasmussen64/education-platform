# Prototype fix: Unbound treats .test as reserved (RFC 6761) and answers it
# itself with NXDOMAIN; the lab internet's names are under .test.
on resolver sed -i 's/^  qname-minimisation: yes$/  qname-minimisation: yes\n  local-zone: "test." nodefault/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on client dig +short www.shop.test
