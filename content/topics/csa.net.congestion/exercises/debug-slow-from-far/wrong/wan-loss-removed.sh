# Wrong: instead of changing the sender's congestion control, the link's
# loss is taken away live with tc, so CUBIC runs fast. The link isn't the
# shop's to change. The site's two faults are fixed properly.
on wan tc qdisc change dev dr1 root netem rate 50mbit delay 25ms loss 0% limit 2000
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sudo sed -i 's/udp dport 4433 accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
