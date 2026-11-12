# Wrong: the resolver is fixed, but a rule was added to edge's NAT by hand
# as well, which edge isn't the learner's to change, and which the next boot
# would lose anyway.
on resolver sed -i 's/^  qname-minimisation: yes$/  qname-minimisation: yes\n  local-zone: "test." nodefault/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on edge nft add rule ip nat postrouting ip saddr 10.10.0.53 counter
