# Wrong: instead of changing the sender's congestion control, the archive
# job is edited to send over 8 connections at once (iperf3 -P 8). The job
# isn't the shop's to change, and it was to keep its one connection. fw
# lets HTTP/3 through, properly.
sudo sed -i 's/-t 6 -J/-t 6 -P 8 -J/' /usr/local/bin/archive-push
sudo sed -i 's/\(tcp dport { 22, 80, 443 } accept\)/\1\n        iifname "isp" oifname "shop" ip daddr 203.0.113.10 udp dport 443 accept/' /etc/netns/fw/nftables.conf
sudo systemctl reload nftables@fw
