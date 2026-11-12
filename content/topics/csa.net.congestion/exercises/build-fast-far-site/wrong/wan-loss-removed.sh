# Wrong: instead of changing the sender's congestion control, the link's
# loss is taken away live with tc, so CUBIC runs fast. The link isn't the
# shop's to change. fw lets HTTP/3 through, properly.
on wan tc qdisc change dev dr1 root netem rate 50mbit delay 50ms loss 0% limit 2000
sudo sed -i 's/\(tcp dport { 22, 80, 443 } accept\)/\1\n        iifname "isp" oifname "shop" ip daddr 203.0.113.10 udp dport 443 accept/' /etc/netns/fw/nftables.conf
sudo systemctl reload nftables@fw
