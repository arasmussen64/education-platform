# The reference fix: Unbound treats .test as reserved (RFC 6761) and answers
# every name under it with NXDOMAIN by itself, from a local zone it has by
# default; the lab internet's names are under .test, so the resolver is told
# that zone isn't its own (nodefault). sed adds the line after
# qname-minimisation, inside the server: block.
on resolver sed -i 's/^  qname-minimisation: yes$/  qname-minimisation: yes\n  local-zone: "test." nodefault/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on client dig +short www.shop.test
